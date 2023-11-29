import random
import re
from typing import List,Union,Tuple
from schotten import Player,Card

class AnalogPlayer(Player):

    def __init__(self):
        super().__init__()
        self.cards = []
        self.stones = []
        self.hand = []
        self.is_init = False

    def __repr__(self):
        if not self.is_init:
            return ''
        output_as_list = []
        # print other player
        for s in range(6):
            if self.stones[s] == 3-self.p:
                output_as_list.append('===   ')
            else:
                output_as_list.append('      ')
        output_as_list.append('\n')
        for i in range(3):
            for stone in range(9):
                curr_card = self.cards[2-self.p][stone][i]
                output_as_list.append(f'{curr_card.num}{curr_card.color}{"F" if curr_card.fake == True else "T"}   ')
            output_as_list.append('\n')
        # print stones
        output_as_list.extend([f'@{s}@   ' for s in range(9)])
        output_as_list.append('\n')
        # print player
        for i in range(3):
            for stone in range(9):
                curr_card = self.cards[self.p-1][stone][i]
                output_as_list.append(f'{curr_card.num}{curr_card.color}{"F" if curr_card.fake == True else "T"}   ')
            output_as_list.append('\n')
        for s in range(9):
            if self.stones[s] == self.p:
                output_as_list.append('===   ')
            else:
                output_as_list.append('      ')
        output_as_list.append('\n')
        output_as_list.append('\n\n')
        # print hand
        for card in self.hand:
            output_as_list.append(f'{card.num}{card.color}   ')
        output_as_list.append('\n')
        # number the cards
        for i in range(len(self.hand)):
            output_as_list.append(f'{i}    ')
        output_as_list.append('\n')
        return ''.join(output_as_list)
    
    def choose_stone_and_card(self, state: List[List[List[Union[Card,int]]]], hand: List[Card], claimed: List[int]) -> Tuple[int, int]:
        self.cards = state
        self.hand = hand
        self.stones = claimed
        self.is_init = True
        print(self)

        while True:
            chosen_card = input("Choose a card: ")
            if re.match(f'[0-{len(self.hand)}]',chosen_card):
                break
            else:
                print(f"Invalid Input {chosen_card}")
        while True:    
            valid_stones = list(filter(lambda x: self.stones[x] == 0, range(len(self.stones))))
            print(f"Valid stones to choose from are: {valid_stones}")
            chosen_stone = input("Choose a stone: ")
            if int(chosen_stone) in valid_stones:
                break
            else:
                print(f"Invalid Input {chosen_stone}")
        return (int(chosen_card), int(chosen_stone))
    
class RandomPlayer(Player):
    def __init__(self):
        super().__init__()
        self.cards = []
        self.stones = []
        self.hand = []
        self.is_init = False

    def real_len(self, player: int, stone: int) -> int:
        """returns num of real cards"""
        for i in range(len(self.cards[player][stone])):
            if type(self.cards[player][stone][i]) == int or self.cards[player][stone][i].fake == True:
                return i
        return len(self.cards[player][stone])

    def __repr__(self):
        if not self.is_init:
            return ''
        output_as_list = []
        # print other player
        for s in range(9):
            if self.stones[s] == 3-self.p:
                output_as_list.append('===   ')
            else:
                output_as_list.append('      ')
        output_as_list.append('\n')
        for i in range(3):
            for stone in range(9):
                curr_card = self.cards[1][stone][i]
                output_as_list.append(f'{curr_card.num}{curr_card.color}{"F" if curr_card.fake == True else "T"}   ')
            output_as_list.append('\n')
        # print stones
        output_as_list.extend([f'@{s}@   ' for s in range(9)])
        output_as_list.append('\n')
        # print player
        for i in range(3):
            for stone in range(9):
                curr_card = self.cards[0][stone][i]
                output_as_list.append(f'{curr_card.num}{curr_card.color}{"F" if curr_card.fake == True else "T"}   ')
            output_as_list.append('\n')
        for s in range(9):
            if self.stones[s] == self.p:
                output_as_list.append('===   ')
            else:
                output_as_list.append('      ')
        output_as_list.append('\n')
        output_as_list.append('\n\n')
        # print hand
        for card in filter(lambda c: c, self.hand):
            output_as_list.append(f'{card.num}{card.color}   ')
        output_as_list.append('\n')
        # number the cards
        for i in range(len(self.hand)):
            output_as_list.append(f'{i}    ')
        output_as_list.append('\n')
        return ''.join(output_as_list)
    
    def choose_stone_and_card(self, state: List[List[List[Union[Card,int]]]], hand: List[Card], claimed: List[int]) -> Tuple[int, int]:
        self.cards = state
        self.hand = hand
        self.stones = claimed
        self.is_init = True
        print(self)
        valid_cards = list(filter(lambda i: hand[i], range(len(hand))))
        valid_stones = list(filter(lambda x: claimed[x] == 0 and self.real_len(0,x)<3, range(len(claimed))))
        try:
            return (random.choice(valid_cards),random.choice(valid_stones))
        except IndexError:
            return (0,0)
