from constants import *

class Card():
    def __init__(self, num: int, color: int):
        if num < 1 or num > NUM_OF_NUMS or color < 1 or color > NUM_OF_COLORS:
            raise ValueError("Invalid number or color")
        self.num = num
        self.color = color
        
    def copy(self):
        return Card(self.num, self.color)
        
    def __repr__(self) -> str:
        return f"{self.num}{COLORS[self.color][:2]}"
    
    def __hash__(self):
        return hash((self.num, self.color))
    
    def __eq__(self, other):
        if isinstance(other, Card):
            return self.num == other.num and self.color == other.color
        else:
            try:
                assert len(other) == 2
            except AssertionError:
                raise TypeError()
            return self.num == other[0] and self.color == other[1]