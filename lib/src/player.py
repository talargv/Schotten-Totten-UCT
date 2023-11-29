from abc import ABC, abstractmethod
from typing import List, Tuple

from board import BoardBaseClass
from card import Card
from constants import *

class Player(ABC):
    """Player always acts as if he is player 1.
    Board is received with other players card in the deck."""
    @abstractmethod
    def choose_stone_and_card(self, cards_in_hand: List[Card], board, **kwargs) -> Tuple[int,int]:
        """if you cant make a move, return (-1,-1), otherwise (card, stone)"""
        available_stones = board.available_stones(0)
        if len(available_stones) == 0 or len(cards_in_hand) == 0:
            return (-1,-1)
        return 0, 0
    
    @abstractmethod
    def claim(self,board) -> List[int]:
        return list(range(NUM_OF_STONES))