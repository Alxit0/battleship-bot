import random
from typing import List, Tuple
import numpy as np
from tqdm import tqdm

from bot import calc_probabil_map, calc_next_move


class Ship:
    def __init__(self, sz: int) -> None:
        self.sz = sz
        self.hp = sz

        self.pos: Tuple[int]
        self.horientation: bool
    
    def put_in_map(self, table_sz, mapa, idx):
        while True:
            x = y = 0
            horientation = random.random() > 0.5
            if horientation:
                # horizontal
                x = random.randint(0, table_sz-self.sz)
                y = random.randint(0, table_sz)

                if np.any(mapa[max(y-1,0):y+2, max(x-1,0):x+self.sz+2] != 0):
                    continue

                mapa[y, x:x+self.sz] = idx

            else:
                # vertical
                x = random.randint(0, table_sz)
                y = random.randint(0, table_sz-self.sz)
                
                if np.any(mapa[max(y-1,0):y+self.sz+2, max(x-1,0):x+2] != 0):
                    continue

                mapa[y:y+self.sz, x] = idx
        
            break
        
        self.pos = (y, x)
        self.horientation = horientation

        return self.sz, self.pos, self.horientation

    def hit(self):
        self.hp -= 1


class FakeBattlefield:
    def __init__(self, ships, map_sz: int=10) -> None:
        self.ships: List[Ship] = list(map(Ship, ships))
        self.pieces_config = []

        self.map = self.generate_random_map(
            map_sz,
            self.ships
        )

        self.enemy_map_version = np.zeros((map_sz, map_sz), np.int32)
        self.n_fails = 0
        self.error_found = False

    def get_map(self):
        return self.enemy_map_version

    def get_active_ships(self):
        return list(map(lambda x=Ship:x.sz, self.ships))

    def fire(self, y, x):
        hit_value = self.map[y, x]
        
        if self.enemy_map_version[y, x] == -1 and not self.error_found:
            print(self.map)
            self.error_found = True
        
        if hit_value == 0:
            # miss
            self.enemy_map_version[y, x] = -1
            self.n_fails += 1
        
        elif hit_value > 0:
            # hit
            cur_ship = self.ships[hit_value-1]

            self.enemy_map_version[y, x] = -2
            cur_ship.hit()
            
            if -1 < y-1 < 10:
                if -1 < x-1 < 10:
                    self.enemy_map_version[y-1, x-1] = -1
                if -1 < x+1 < 10:
                    self.enemy_map_version[y-1, x+1] = -1
            if -1 < y+1 < 10:
                if -1 < x-1 < 10:
                    self.enemy_map_version[y+1, x-1] = -1
                if -1 < x+1 < 10:
                    self.enemy_map_version[y+1, x+1] = -1
            
            # sunk
            if cur_ship.hp != 0:
                return
            
            ship_y, ship_x = cur_ship.pos

            if cur_ship.horientation:
                self.enemy_map_version[max(0,ship_y-1):ship_y+1, max(0,ship_x-1):ship_x+1+cur_ship.sz] = -1
            else:
                self.enemy_map_version[max(0,ship_y-1):ship_y+1+cur_ship.sz, max(0,ship_x-1):ship_x+1] = -1

    def generate_random_map(self, table_sz: int, ships: List[int]) -> np.ndarray:
        new_map = np.zeros((table_sz, table_sz), dtype=np.int32)

        table_sz -= 1
        ships = ships[::-1]

        for idx, ship in enumerate(self.ships):
            piece_cnf = ship.put_in_map(table_sz, new_map, idx+1)
            self.pieces_config.append(piece_cnf)
            
        return new_map
    

def solve_battlefield(battlefield: FakeBattlefield) -> int:

    while sum(map(lambda x=Ship:x.hp, battlefield.ships)):
        prob_map = calc_probabil_map(
            battlefield.get_map(),
            battlefield.get_active_ships(),
            prio_ship_sz=True
        )
        
        y, x = calc_next_move(prob_map)
        battlefield.fire(y, x)
    
    return battlefield.n_fails


def main():
    n = 500

    a = 0
    max_moves = 0
    best_map = None
    
    for _ in tqdm(range(n)):
        fk_battlefield = FakeBattlefield([4, 3, 3, 2, 2, 2, 1, 1, 1, 1], 10)
        n_moves = solve_battlefield(fk_battlefield)
        a += n_moves
        if n_moves > max_moves:
            best_map = fk_battlefield
            max_moves = n_moves

        # print(f"{n_moves = }")
    
    print(f"Media: {a/n} moves")
    print("Best Map:")
    print(best_map.map)
    print(f"Took {max_moves} moves")
    print(best_map.pieces_config)

if __name__ == "__main__":
    main()
