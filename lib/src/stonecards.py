from typing import Iterable, Optional, Sequence

from card import Card
from constants import *

class StoneCards():
    def __init__(self, cards: Iterable[Card]):
        """Class for handling triplets in front of stones."""
        tmp = tuple(cards)
        if len(tmp) > 3:
            raise TypeError("Too many cards")
        self.cards = tmp
    
    def __len__(self):
        return len(self.cards)
    
    def __getitem__(self, index):
        return self.cards[index]
    
    @staticmethod
    def strength_from_seq(cards: Sequence[Card]):
        """sum in [4,26], run in [27,33], color in [40,56]
            three of a kind in [57,65], color run in [66,72]"""
        if len(cards) < 3:
            print(f"WARNING: hand length is too short")
            return
        # check if three of a kind
        if cards[0].num == cards[1].num and cards[1].num == cards[2].num:
            return 56+cards[0].num
        
        is_run, is_color = False, False
        # check if run
        tmp = sorted(cards, key=lambda x: x.num)
        if tmp[0].num + 1 == tmp[1].num and tmp[1].num + 1 == tmp[2].num:
            is_run = True
        if cards[0].color == cards[1].color and cards[1].color == cards[2].color:
            is_color = True
        
        if is_run and is_color:
            return 65+tmp[0].num
        elif is_run:
            return 26+tmp[0].num
        elif is_color:
            return cards[0].num + cards[1].num + cards[2].num + 33
        else:
            return cards[0].num + cards[1].num + cards[2].num
    
    def copy(self):
        return StoneCards(self.cards.copy())
    
    def hand_strength(self):
        return StoneCards.strength_from_seq(self.cards)
    
    def __iter__(self):
        return iter(self.cards)
    
    def __next__(self):
        return next(self.cards)
    
    def tolist(self,copy=True):
        if copy:
            return list(self.cards.copy())
        return list(self.cards)