import numpy as np
import os
import random

SIZE = 10
CAN_GLUE = True
PECAS = [	# http://en.battleship-game.org
	(1, 4),
	(1, 3),
	(1, 3),
	(1, 2),
	(1, 2),
	(1, 2),
	(1, 1),
	(1, 1),
	(1, 1),
	(1, 1),
]

def print_prob_mapa(mapa:np.ndarray):
	print('  ', *map(chr, range(65, 65+SIZE)),sep='  ', end='\n\n')
	
	for i, line in enumerate(mapa):
		print(f'{i+1:2} ', *map(lambda x: str(x).zfill(2), line))


def _calc_peca_prob(mapa:np.ndarray, peca:tuple):
	new_mapa = np.zeros(mapa.shape, dtype=np.int8)
	
	# horizontal
	for i in range(SIZE-peca[0]+1):
		for j in range(SIZE-peca[1]+1):

			if np.all(mapa[i:i+peca[0],j:j+peca[1]] == 0):
				new_mapa[i:i+peca[0],j:j+peca[1]] += 1
	
	
	if peca == peca[::-1]:
		return new_mapa

	# vertical
	peca = peca[::-1]
	for i in range(SIZE-peca[0]+1):
		for j in range(SIZE-peca[1]+1):

			if np.all(mapa[i:i+peca[0],j:j+peca[1]] == 0):
				new_mapa[i:i+peca[0],j:j+peca[1]] += 1

	return new_mapa

def calc_prob(mapa:np.ndarray):
	new_mapa = mapa.copy()

	for i in PECAS:
		new_mapa += _calc_peca_prob(mapa, i)

	return new_mapa


def calc_hit(mapa:np.ndarray, hit:str):
	was_hit = False
	if hit[0] == '!':
		was_hit = True
		hit = hit[1:]
	
	x, y = ord(hit[0].lower()) - 97, int(hit[1:])-1

	if was_hit:
		mapa[max(0, y-1):y+2,max(0, x-1):x+2] = -1
	else:
		mapa[y,x] = -1

def high_probs(mapa:np.ndarray):
	resp = []
	m = np.max(mapa)
	
	for i in range(SIZE):
		for j in range(SIZE):
			if mapa[i,j] == m:
				resp.append(f'{chr(j+65)}{i+1}')

	return resp

def main():
	mapa = np.zeros((SIZE, SIZE), dtype=np.int8)
	# mapa[3,3] = -1
	# mapa = np.asarray([[*range(i*SIZE, (i+1)*SIZE)] for i in range(SIZE)])


	while True:
		os.system('cls' if os.name == 'nt' else 'clear')
		
		probs = calc_prob(mapa)
		best_plays = high_probs(probs)
		random.shuffle(best_plays)
		
		print_prob_mapa(probs)
		print('\n'+' '.join(best_plays), end='\n\n')

		hit = input()
		if hit == 'q':
			break
		elif hit == '':
			pass
		else:
			calc_hit(mapa, hit)


if __name__ == '__main__':
	main()
