from abc import ABC, abstractmethod
from typing import List, Iterable

from card import Card
from deck import Deck
from stonecards import StoneCards
from constants import *
from enums import PlayerIndex, StoneIndex

class __StateOfCards():
    def __init__(self):
        self.__cards = [[StoneCards() for _ in range(NUM_OF_STONES)] for i in range(NUM_OF_PLAYERS)]
        
    def get(self, player: PlayerIndex, stone: StoneIndex) -> StoneCards:
        return self.__cards[player][stone]
    
    def add_at(self, player: PlayerIndex, stone: StoneIndex, card: Card) -> None:
        if len(self.__cards[player][stone]) == 3:
            raise IndexError(f"Cannot add at {player.name}{stone.name}")
        self.__cards[player][stone] = StoneCards(self.__cards[player][stone])
    
class __StateOfStones():
    def __init__(self):
        tmp = PlayerIndex.NOPLAYER
        self.__stones = [tmp for _ in range(NUM_OF_STONES)]
        
    def claim(self, stone: StoneIndex, player: PlayerIndex) -> None:
        self.__stones[stone] = player
        
    def claims(self, stones: Iterable[StoneIndex], player: PlayerIndex) -> None:
        for stone in stones:
            self.__stones[stone] = player 

class __StateOfAdvantages():
    
   
class BoardBaseClass():
    def __init__(self,**kwargs):
        self.deck = kwargs.get('deck',None)
        if self.deck is None:
            self.deck = Deck()
        self.stones = kwargs.get('stones',None) 
        if self.stones is None:
            self.stones = __StateOfStones()
        # 0 - unclaimed 
        # 1 - claimed p1
        # 2 - claimed p2
        self.cards = kwargs.get('cards', None)
        if self.cards is None:
            self.cards = __StateOfCards()
        # cards[i][j][k] is the (k+1)th card player i has in front of stone j
        self.advantage = kwargs.get('advantage', None)
        if self.advantage is None:
            self.advantage = [0 for _ in range(NUM_OF_STONES)]
        # 0 - no player has placed 3 cards
        # 1 - first player has placed 3 cards first
        # 2 - second player has placed 3 cards first
        self.cards_on_board = kwargs.get('cards_on_board', None)
        if self.cards_on_board is None:
            self.cards_on_board = [[False for _ in range(NUM_OF_COLORS)] for j in range(NUM_OF_NUMS)]
        # cards_on_board[i][j] == True iff Card(num=i+1,color=j+1) is on the board
 
        
    def available_stones(self, player: int) -> List[int]:    
        return [stone for stone in range(len(self.stones)) if self.stones[stone] == 0 and len(self.cards[player][stone]) < 3]
    
    def change_pov(self):
        state = self.copy()
        state.stones = [state.stones[len(state.stones)-1-i] for i in range(len(state.stones))]
        state.advantage = [state.advantage[len(state.advantage)-1-i] for i in range(len(state.advantage))]
        for i in range(NUM_OF_STONES):
            if state.stones[i] == 1:
                state.stones[i] = 2
            elif state.stones[i] == 2:
                state.stones[i] = 1
            if state.advantage[i] == 1:
                state.advantage[i] = 2
            elif state.advantage[i] == 2:
                state.advantage[i] = 1
        state.cards[0] = [state.cards[0][NUM_OF_STONES-1-i] for i in range(len(state.cards[0]))]
        state.cards[1] = [state.cards[1][NUM_OF_STONES-1-i] for i in range(len(state.cards[1]))]
        state.cards[0], state.cards[1] = state.cards[1], state.cards[0]
        
        return state
        
    def __repr__(self, p=0):
        """p = 0 if viewpoint is from first player. p = 1 otherwise"""
        board = self
        if p == 1:
            board = self.change_pov()
        # print other player
        output_as_list = []
        for s in range(NUM_OF_STONES):
            if board.stones[s] == 2:
                output_as_list.append('===   ')
            else:
                output_as_list.append('      ')
                
        output_as_list.append('\n\n')
        
        for i in range(3):
            for stone in range(NUM_OF_STONES):
                if i >= len(board.cards[1][stone]):
                    output_as_list.append('      ')
                else:
                    output_as_list.append(str(board.cards[1][stone][i])+'   ')
            output_as_list.append('\n')
            
        output_as_list.append('\n')
        
        # print stones
        for s in range(NUM_OF_STONES):
            if board.stones[s] == 0:
                output_as_list.append('===   ')
            else:
                output_as_list.append('      ')
        
        output_as_list.append('\n\n')
        
        # print player
        for i in range(3):
            for stone in range(NUM_OF_STONES):
                if 2-i >= len(board.cards[0][stone]):
                    output_as_list.append('      ')
                else:
                    output_as_list.append(str(board.cards[0][stone][2-i])+'   ')
            output_as_list.append('\n')
            
        output_as_list.append('\n')
        
        for s in range(NUM_OF_STONES):
            if board.stones[s] == 1:
                output_as_list.append('===   ')
            else:
                output_as_list.append('      ')
        #output_as_list.append('\n')
        return ''.join(output_as_list)
    
    def to_dict(self):
        """Copies content to a dictionary"""
        items = {}
        items['deck'] = self.deck.copy()
        items['stones'] = self.stones.copy()
        items['cards'] = [[self.cards[i][j].copy() for j in range(NUM_OF_STONES)] for i in range(2)]
        items['advantage'] = self.advantage.copy()
        items['cards_on_board'] = [self.cards_on_board[i].copy() for i in range(NUM_OF_NUMS)]
       
    @abstractmethod
    def factory(self, **kwargs):
        """Creates a new instance of self"""
        pass
        
    def copy(self):
        items = self.to_dict()
        return self.factory(**items)
    
    def draw_card(self):
        return self.deck.draw_card()
    
    @staticmethod
    def is_legal_claim_static(hand1: Hand, hand2: Hand,
                       advantage: bool, cards_on_board: List[List[bool]]) -> bool:
        """given hand1 and hand2 that represents card placements in front of the same stone,
        returns True iff claim is legal"""
        if len(hand1) < 3:
            return False
        
        hand1_strength = hand1.hand_strength()
        if len(hand2) == 3:
            if advantage:
                return hand1_strength >= hand2.hand_strength()
            else:
                return hand1_strength > hand2.hand_strength() 
        assert advantage # supposed to be True
        if len(hand2) == 2:
            for num in range(NUM_OF_NUMS):
                for color in range(NUM_OF_COLORS):
                    if hand2[0] == (num+1,color+1) or hand2[1] == (num+1,color+1) or cards_on_board[num][color] == True:
                        continue
                    other_strength = Hand.strength_from_list([hand2[0],hand2[1],Card(num+1,color+1)])
                    if other_strength > hand1_strength:
                        return False
            return True
        elif len(hand2) == 1:
            for num1 in range(NUM_OF_NUMS):
                for color1 in range(NUM_OF_COLORS):
                    for num2 in range(NUM_OF_NUMS):
                        for color2 in range(NUM_OF_COLORS):
                            if (num1,color1) == (num2,color2) or hand2[0] == (num1+1,color1+1) or hand2[0] == (num2+1,color2+1) or \
                            cards_on_board[num1][color1] == True or cards_on_board[num2][color2] == True:
                                continue
                            other_strength = Hand.strength_from_list([hand2[0],Card(num1+1,color1+1),Card(num2+1,color2+1)])
                            if other_strength > hand1_strength:
                                return False
            return True
        else:
            for num1 in range(NUM_OF_NUMS):
                for color1 in range(NUM_OF_COLORS):
                    for num2 in range(NUM_OF_NUMS):
                        for color2 in range(NUM_OF_COLORS):
                            for num3 in range(NUM_OF_NUMS):
                                for color3 in range(NUM_OF_COLORS):
                                    if (num1,color1) == (num2,color2) or (num1,color1) == (num3,color3) or (num2,color2) == (num3,color3) \
                                        or cards_on_board[num1][color1] == True or cards_on_board[num2][color2] == True or cards_on_board[num3][color3]:
                                        continue
                                    other_strength = Hand.strength_from_list([Card(num1+1,color1+1),Card(num2+1,color2+1),Card(num3+1,color3+1)])
                                    if other_strength > hand1_strength:
                                        return False
            return True
        
    def is_board_terminal(self) -> int:
        """0 - Not terminal, 1 - player 1 wins, 2 - player 2 wins"""
        count = [0,0,0]
        neighboring_stones_count, neighboring_stones_player = 0, 0
        for p in self.stones:
            if neighboring_stones_count == 3 and neighboring_stones_player != 0:
                break
            if neighboring_stones_player == p:
                neighboring_stones_count += 1
            else:
                neighboring_stones_count = 1
                neighboring_stones_player = p
            count[p] += 1
        if neighboring_stones_count == 3 and neighboring_stones_player != 0:
            return neighboring_stones_player
        if count[1] >= 5:
            return 1
        if count[2] >= 5:
            return 2
        return 0
        
    @abstractmethod        
    def claim_stone(self,player: int, stone: int, show=True):
        """Does nothing when stone is claimed"""
        pass