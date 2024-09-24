"""
	For http://en.battleship-game.org/

	TODO:
		- change priority by those who give more info in case it hits: DONE
		- give priority to find the bigger ships first: DONE
			- make the rest ships contribute to tiebreake: DONE
		- abilaty to define costum map: DONE
"""
from __future__ import annotations

import json
import random
import sys
import time
import numpy as np
from typing import List, Tuple
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from pynput import keyboard

# typing
from selenium.webdriver import Firefox
from selenium.webdriver.remote.webelement import WebElement

FIREFOX_DRIVER = "/Users/alexito_player/Drivers/geckodriver"
runing_loop = True

class BattleField:
	def __init__(self, browser:Firefox, class_search: str) -> None:
		self.browser = browser

		self.battlefield = browser.find_element(
			By.XPATH, 
			f"//*[contains(@class, 'battlefield battlefield__{class_search}')]"
		)

		self.turns = 0

	def wait_for_turn(self, me: BattleField, delay=0.5):
		a = time.time()
		y = lambda: (len(me.get_active_ships()) == 0) ^ (len(self.get_active_ships()) == 0)
		game_ended = y()
		
		n_of_loops = 0
		while not self._is_active() and not game_ended:
			time.sleep(delay)
			
			# time out (1 min 30 sec)
			if time.time() - a > 90:
				return True
			
			game_ended = y()
			n_of_loops +=1

		if n_of_loops > 1:
			self.turns += 1

		return game_ended

	def get_active_ships(self) -> List[int]:
		ship_types = self.battlefield.find_elements(By.XPATH, ".//*[contains(@class, 'ship-type ship-type__len_')]")
		
		resp = []
		for ship_type in ship_types:
			for ship in ship_type.find_elements(By.CLASS_NAME, 'ship'):
				if 'ship__killed' not in ship.get_attribute('class'):
					resp.append(int(ship_type.get_attribute('class').split('ship-type__len_')[-1]))

		return resp

	def get_cells_battlefield(self) -> List[List[WebElement]]:
		table_html = self.battlefield.find_element(By.XPATH, ".//*[@class='battlefield-table']")

		mapa: List[List[WebElement]] = []
		for row in table_html.find_elements(By.XPATH, ".//tr"):
			mapa.append([])
			for cell in row.find_elements(By.XPATH, ".//td"):
				mapa[-1].append(cell)
		
		return mapa

	def get_battlefield(self) -> np.ndarray:
		table_html = self.battlefield.find_element(By.XPATH, ".//*[@class='battlefield-table']")

		mapa: List[List[int]] = []
		for row in table_html.find_elements(By.XPATH, ".//tr"):
			mapa.append([])
			for cell in row.find_elements(By.XPATH, ".//td"):
				cell_classes = cell.get_attribute('class')

				if 'battlefield-cell__hit' in cell_classes and 'battlefield-cell__done' not in cell_classes:
					mapa[-1].append(-2)
				elif 'battlefield-cell__empty' in cell_classes:
					mapa[-1].append(0)
				else:
					mapa[-1].append(-1)
		
		return np.asanyarray(mapa)

	def _is_active(self) -> bool:
		return not ('battlefield__wait' in self.battlefield.get_attribute('class'))


def init_browser() -> webdriver.Firefox:
	if FIREFOX_DRIVER == "":
		print("No driver provided")
		exit(0)
    
	user_agent = "python script"
	firefox_service = Service(FIREFOX_DRIVER)
	firefox_options = Options()
	firefox_options.set_preference('general.useragent.override', user_agent)

	# Launch firefox driver
	browser = webdriver.Firefox(service=firefox_service, options=firefox_options)
	return browser

def start_friend_game(browser: Firefox):
	browser.find_element(By.XPATH, "//*[text()='friend']").click()
	time.sleep(0.1)
	browser.find_element(By.XPATH, "//*[text()='Play']").click()

def start_game(browser: Firefox):
	browser.find_element(By.XPATH, "//*[text()='Play']").click()

def exit_game(browser: Firefox):
	notifications = browser.find_elements(By.XPATH, ".//*[contains(@class, 'notification notification__')]")
	notifications = [i for i in notifications if 'none' not in i.get_attribute('class').split()]

	if len(notifications) == 1:
		try:
			notifications[0].find_element(By.XPATH, ".//*[contains(@class, 'notification-submit')]").click()
		except:
			browser.find_element(By.CLASS_NAME, "leave-link").click()


def randomize_layout(browser: Firefox):
	browser.find_element(By.XPATH, "//*[text()='Randomise']").click()
	time.sleep(.1)

def _place_piece(
		browser: webdriver.Firefox, 
		piece: WebElement, 
		field: List[List[WebElement]], 
		pos: Tuple[int, int], 
		horientation: bool,
		sz: int):
	

	# Locate the source element
	source_element = piece

	# Create action chain object
	actions = ActionChains(browser)

	# correct horientation
	if horientation:

		x_offset = field[0][0].location['x'] - source_element.location['x'] + 1
		y_offset = field[0][0].location['y'] - source_element.location['y'] + 1
		
		actions.drag_and_drop_by_offset(source_element, x_offset, y_offset)
		actions.click(field[0][0])

		source_element = field[0][0]

	# Locate the target element (where to drop)
	y, x = pos
	target_element = field[y][x]

	# Perform drag and drop
	x_offset = target_element.location['x'] - source_element.location['x'] + 1
	y_offset = target_element.location['y'] - source_element.location['y'] + 1
	actions.drag_and_drop_by_offset(source_element, x_offset, y_offset)
	
	actions.perform()

def load_layout(browser: webdriver.Firefox):
	with open("./map_cnf.json", "r") as file:
		layout = json.load(file)

	# go to page
	browser.find_element(By.XPATH, "//*[text()='Reset']").click()

	# get pieces / field
	pieces = browser.find_elements(By.XPATH, "//*[contains(@class, 'ship-box')]")
	field = []
	for row in browser.find_elements(By.XPATH, "//tr[@class='battlefield-row']"):
		field.append(row.find_elements(By.XPATH, ".//*[@class='battlefield-cell-content']"))

	# place pieces
	pieces_organized = [(piece, pos, horiz, sz) for piece, (sz, pos, horiz) in zip(pieces, layout)] 
	pieces_organized.sort(key=lambda x: (x[1][0] < 2) + (x[1][1] < 2))
	pieces_organized.sort(key=lambda x: x[2])

	for piece, pos, horiz, sz in pieces_organized:

		_place_piece(browser, piece, field, pos, not horiz, sz)
	
	time.sleep(3)



def click_in_position(browser: Firefox, cell:WebElement):
	
	# Perform the click action at the specified coordinates
	actions = ActionChains(browser)
	
	actions.move_to_element(cell).perform()
	time.sleep(0.2)
	
	actions.click().perform()
	time.sleep(0.4)

def calc_probabil_map(cur_map: np.ndarray, active_ships: List[int], *, prio_ship_sz=False) -> np.ndarray:
	h, w = cur_map.shape
	new_mapa = cur_map.copy()

	def _clac_prob_peca(tam, peso):
		# horizontal
		for i in range(h):
			for j in range(w-tam+1):
				if np.all(cur_map[i, j:j+tam] >= 0):
					new_mapa[i, j:j+tam] = new_mapa[i, j:j+tam] + peso

		# vertical
		for i in range(h-tam+1):
			for j in range(w):
				if np.all(cur_map[i:i+tam, j] >= 0):
					new_mapa[i:i+tam, j] = new_mapa[i:i+tam, j] + peso


	m = max(active_ships)
	for i in set(active_ships):
		if i == m and prio_ship_sz:
			_clac_prob_peca(i, 100)
		else:
			_clac_prob_peca(i, 1)
		
	return new_mapa

def calc_next_move(prob_map: np.ndarray):
	"""Legend:
	- -2: hit
	- -1: miss
	- 0>: empty

	Args:
		prob_map (np.ndarray): _description_

	Returns:
		_type_: _description_
	"""
	h, w = prob_map.shape
	if np.any(prob_map == -2):
		# destroy
		possible_cells = []
		for i in range(h):
			for j in range(w):
				if prob_map[i, j] != -2:
					continue

				if i != 0:
					possible_cells.append((i-1, j))
				if i != h-1:
					possible_cells.append((i+1, j))
				if j != 0:
					possible_cells.append((i, j-1))
				if j != w-1:
					possible_cells.append((i, j+1))
		
		empty_cells = [(i, j) for i, j in possible_cells if prob_map[i, j] >= 0]

		# chose with highest probability
		empty_cells.sort(key=lambda x:prob_map[x[0], x[1]], reverse=True)
		
		if len(empty_cells) > 0:
			return random.choice(empty_cells)

	# get those with max prob
	max_value = prob_map.max()
	possible_cells = []
	for i in range(h):
		for j in range(w):
			if prob_map[i, j] == max_value:
				possible_cells.append((i, j))

	# prioretize a checker pattern
	checkers1 = []
	checkers2 = []
	for i in possible_cells:
		y, x = i
		if y%2 == x%2:
			checkers1.append(i)
		else:
			checkers2.append(i)

	if len(checkers1) > 0:
		possible_cells = checkers1
	else:
		possible_cells = checkers2

	# prioretize by given entropy
	def _calc_entropy(y, x):
		return np.sum(prob_map[max(y-1,0):y+2, max(x-1,0):x+2] >= 0)

	max_entropy = max(map(lambda x:_calc_entropy(*x), possible_cells))
	possible_cells = [i for i in possible_cells if _calc_entropy(*i) == max_entropy]

	return random.choice(possible_cells)


def play_game(browser: Firefox) -> bool:
	# input("Waiting for start (enter) ... ")
	battlefield = BattleField(browser, "rival")
	me = BattleField(browser, "self")
	
	n_moves = 0

	can_clear = False
	while True:
		if battlefield.wait_for_turn(me, delay=0.2):
			print("Game ended.")
			break
		
		if can_clear:
			clear_last_lines(2)
		can_clear = True
		
		active_ships = battlefield.get_active_ships()
		print(f"{active_ships = }")
		
		cur_map = battlefield.get_battlefield()
		prob_map = calc_probabil_map(cur_map, active_ships, prio_ship_sz=True)
		# print(prob_map)

		line, col = calc_next_move(prob_map)
		print("move =", chr(ord('A')+col), line+1)

		chosen_cell = battlefield.get_cells_battlefield()[line][col]
		click_in_position(browser, chosen_cell)

		n_moves += 1

	return (len(me.get_active_ships()) != 0, battlefield.turns)


def on_press(key):
	global runing_loop
	try:
		if key.char == 'q':
			runing_loop = False
	except:
		pass

def clear_last_lines(n=2):
	for _ in range(n):
		# Move cursor up n lines
		sys.stdout.write("\033[F")
		# Clear the current line
		sys.stdout.write("\033[K")

def main():
	global runing_loop
	listener = keyboard.Listener(on_press=on_press)
	listener.start()

	browser = init_browser()
	
	browser.get("http://en.battleship-game.org/")

	runing_loop = True
	stats = [0, 0]

	load_layout(browser)

	i = 1
	while i <= 10:
		print("#"*10, f"Game {i}", "#"*10)
		
		# start_friend_game(browser)
		start_game(browser)
		
		result, n_moves = play_game(browser)
		
		clear_last_lines(3)
		print("Win" if result else "Lose")
		print(f"{n_moves = }")
		stats[result] += 1

		time.sleep(.1)
		exit_game(browser)
		
		if not runing_loop:
			input("Pause")
			clear_last_lines(1)
			runing_loop = True
		
		i += 1

		if input('New game? (y/n) ') == 'n':
			break
		
	print("#"*15)
	print(f"Wins: {stats[1]}\nLoses: {stats[0]}")
	
	browser.close()

def main_friend(match_url: str):
	browser = init_browser()
	
	browser.get(match_url)

	start_game(browser)
	play_game(browser)


if __name__ == "__main__":
	if len(sys.argv) < 2:
		main()
	else:
		main_friend(sys.argv[1])
