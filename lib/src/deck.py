import random as rand
from typing import List

from card import Card
from constants import *

class Deck():
    def __init__(self, deck: List[Card]=None):
        if deck is None:
            self.deck = [Card(j,i) for i in range(1,NUM_OF_COLORS + 1) for j in range(1, NUM_OF_NUMS + 1)]
            rand.shuffle(self.deck)
        else:
            self.deck = deck
            
    def copy(self):
        return Deck(self.deck.copy())
    
    def __len__(self):
        return len(self.deck)
    
    def __getitem__(self, key):
        return self.deck[key]
    
    def draw_card(self):
        try:
            return self.deck.pop()
        except IndexError:
            return