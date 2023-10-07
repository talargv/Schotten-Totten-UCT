import random as rand

from abc import ABC, abstractmethod
from typing import List, Union, Type, Self, Tuple, Optional

COLORS = {1:"Purple", 2:"Brown", 3:"Red", 4:"Yellow", 5:"Green", 6:"Blue"}
NUM_OF_COLORS = 6
NUM_OF_NUMS = 9
NUM_OF_STONES = 9
CARDS_IN_HAND = 6

class Card():
    def __init__(self, num: int, color: int):
        """num in [1,NUM_OF_NUMS], color in [1,NUM_OF_COLORS]"""
        self.num = num
        self.color = color
        
    def __repr__(self) -> str:
        return f"{self.num}{COLORS[self.color][:2]}"
    
    def __eq__(self, other):
        if type(other) == type(self):
            return self.num == other.num and self.color == other.color
        elif type(other) == tuple or type(other) == list:
            try:
                assert len(other) == 2
            except AssertionError:
                raise TypeError()
            return self.num == other[0] and self.color == other[1]
        else:
            raise TypeError()
class Hand():
    def __init__(self, cards: List[Card]=[]):
        """Class for handling triplets in front of stones."""
        self.hand = cards
    
    def __len__(self):
        return len(self.hand)
        
    def append(self, card: Card):
        self.hand.append(card)
        
    def extend(self, cards: Union[Self,List[Card]],copy=True):
        if type(cards) == list:
            self.hand.extend(cards)
        #elif copy:
        #    self.hand.extend(cards.hand.copy())
        else:
            self.hand.extend(cards.hand)
    
    def pop(self, index=-1) -> Optional[Card]:
        return self.hand.pop(index)
    
    def __getitem__(self, index):
        return self.hand[index]
    
    @staticmethod
    def strength_from_list(hand: List[Card]):
        """sum in [4,26], run in [27,33], color in [40,56]
            three of a kind in [57,65], color run in [66,72]"""
        if len(hand) < 3:
            print(f"WARNING: hand length is too short")
            return
        # check if three of a kind
        if hand[0].num == hand[1].num and hand[1] == hand[2]:
            return 56+hand[0].num
        
        is_run, is_color = False, False
        # check if run
        tmp = sorted(hand, key=lambda x: x.num)
        if tmp[0].num + 1 == tmp[1].num and tmp[1].num + 1 == tmp[2].num:
            is_run = True
        if hand[0].color == hand[1].color and hand[1].color == hand[2].color:
            is_color = True
        
        if is_run and is_color:
            return 65+tmp[0].num
        elif is_run:
            return 26+tmp[0].num
        elif is_color:
            return hand[0].num + hand[1].num + hand[2].num + 33
        else:
            return hand[0].num + hand[1].num + hand[2].num
    
    def copy(self):
        return Hand(self.hand.copy())
    
    def hand_strength(self):
        return Hand.strength_from_list(self.hand)
    
    def __iter__(self):
        return iter(self.hand)
    
    def __next__(self):
        return next(self.hand)
    
    def tolist(self,copy=True):
        if copy:
            return self.hand.copy()
        return self.hand
    
    def hand_not_on_board(self, available_cards: List[List[int]]) -> bool: 
        for card in self.hand:
            if available_cards[card.num][card.color]:
                return False
        return True
    
    
class Deck():
    def __init__(self, deck: List[Card]=[]):
        if deck:
            self.deck = deck
        else:
            self.deck = []
            for i in range(1,NUM_OF_COLORS + 1):
                for j in range(1, NUM_OF_NUMS + 1):
                    self.deck.append(Card(j,i))
            rand.shuffle(self.deck)
            
    def copy(self):
        return Deck(self.deck.copy())
    
    
    def draw_card(self):
        try:
            return self.deck.pop()
        except IndexError:
            return
        
class Board():
    def __init__(self,**kwargs):
        self.deck = kwargs.get('deck',Deck())
        self.stones = kwargs.get('stones',[0 for _ in range(NUM_OF_STONES)]) 
        # 0 - unclaimed 
        # 1 - claimed p1
        # 2 - claimed p2
        self.cards = kwargs.get('cards',[[Hand() for _ in range(NUM_OF_STONES)] for i in range(2)])
        # cards[i][j][k] is the (k+1)th card player i has in front of stone j
        self.advantage = kwargs.get('advantage',[0 for _ in range(NUM_OF_STONES)])
        # 0 - no player has placed 3 cards
        # 1 - first player has placed 3 cards first
        # 2 - second player has placed 3 cards first
        self.cards_on_board = kwargs.get('cards_on_board',[[False for _ in range(NUM_OF_COLORS)] for j in range(NUM_OF_NUMS)])
        # cards_on_board[i][j] == True iff Card(num=i+1,color=j+1) is on the board
        
    def __repr__(self, p=0):
        """p = 0 if viewpoint is from first player. p = 1 otherwise"""
        
        # print other player
        output_as_list = []
        for s in range(NUM_OF_STONES):
            if self.stones[s] == 2-p:
                output_as_list.append('===   ')
            else:
                output_as_list.append('      ')
                
        output_as_list.append('\n\n')
        
        for i in range(3):
            for stone in range(NUM_OF_STONES):
                if i >= len(self.cards[1-p][stone]):
                    output_as_list.append('      ')
                else:
                    output_as_list.append(str(self.cards[1-p][stone][i])+'   ')
            output_as_list.append('\n')
            
        output_as_list.append('\n')
        
        # print stones
        for s in range(NUM_OF_STONES):
            if self.stones[s] == 0:
                output_as_list.append('===   ')
            else:
                output_as_list.append('      ')
        
        # print player
        for i in range(3):
            for stone in range(NUM_OF_STONES):
                if i >= len(self.cards[p][NUM_OF_STONES-1-stone]):
                    output_as_list.append('      ')
                else:
                    output_as_list.append(str(self.cards[p][NUM_OF_STONES-1-stone][i])+'   ')
            output_as_list.append('\n')
            
        output_as_list.append('\n\n')
        
        for s in range(NUM_OF_STONES):
            if self.stones[s] == p+1:
                output_as_list.append('===   ')
            else:
                output_as_list.append('      ')
        output_as_list.append('\n')
        return ''.join(output_as_list)
    
    def copy(self):
        items = {}
        items['deck'] = self.deck.copy()
        items['stones'] = self.stones.copy()
        items['cards'] = [[self.cards[i][j].copy() for j in range(NUM_OF_STONES)] for i in range(2)]
        items['advantage'] = self.advantage.copy()
        items['cards_on_board'] = [self.cards_on_board[i].copy() for i in range(NUM_OF_NUMS)]
        return Board(items)
    
    def pop_from_stone(self,player,stone) -> Optional[Card]:
        """Reverses the action of the place_card function"""
        if self.advantage[stone] == player+1:
            self.advantage[stone] = 0
        return self.cards[player][stone].pop()
    
    def draw_card(self):
        return self.deck.draw_card()
    
    @staticmethod
    def is_legal_claim(hand1: Hand, hand2: Hand,
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
                    if hand2[0] == (num,color) or hand2[1] == (num,color) or cards_on_board[num][color] == True:
                        continue
                    other_strength = Hand.strength_from_list(hand2[0],hand2[1],Card(num,color))
                    if other_strength > hand1_strength:
                        return False
            return True
        elif len(hand2) == 1:
            for num1 in range(NUM_OF_NUMS):
                for color1 in range(NUM_OF_COLORS):
                    for num2 in range(NUM_OF_NUMS):
                        for color2 in range(NUM_OF_COLORS):
                            if (num1,color1) == (num2,color2) or hand2[0] == (num1,color1) or hand2[0] == (num2,color2) or \
                            cards_on_board[num1][color1] == True or cards_on_board[num2][color2] == True:
                                continue
                            other_strength = Hand.strength_from_list(hand2[0],Card(num1,color1),Card(num2,color2))
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
                                    other_strength = Hand.strength_from_list(Card(num1,color1),Card(num2,color2),Card(num3,color3))
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
        if count[1] == 5:
            return 1
        if count[2] == 5:
            return 2
        return 0
        
    def claim_stone(self,player: int, stone: int):
        """Does nothing when stone is claimed"""
        if self.stones[stone] != 0:
            return
        if not Board.is_legal_claim(self.cards[player][stone],self.cards[1-player][stone],
                                    self.advantage[stone] == player+1,self.cards_on_board):
            print(f"Invalid claim")
            return
        self.stones[stone] = player+1
        
    def place_card(self, stone: int, card: Card, player: int):
        self.cards[player][stone].append(card)
        if len(self.cards[player][stone]) == 3 and self.advantage[stone] == 0:
            self.advantage[stone] = player + 1



class Player(ABC):
    @abstractmethod
    def choose_stone_and_card(self, cards_in_hand: List[Card], board: Board) -> Tuple[int,int]:
        """if you cant make a move, return (0,0), otherwise (card, stone)"""
        pass
    
    def assign_player(self, p: int):
        self.p = p
    
    @abstractmethod
    def claim(self,board: Board) -> List[int]:
        pass
            
class Game():
    def __init__(self, p1: Type[Player], p2: Type[Player], **kwargs):
        self.board = kwargs.get('board',Board())
        self.players = [p1, p2]
        p1.assign_player(0)
        p2.assign_player(1)
        self.hands = [[self.board.draw_card() for _ in range(CARDS_IN_HAND)] for p in range(2)]
        self.game_over = False
    
    def play(self):
        while not self.game_over:
            print(f'Player 1, make your move: ')
            self.make_move(0)
            self.is_game_over()
            if self.game_over:
                return
            print(f'Player 2, make your move: ')
            self.make_move(1)
            self.is_game_over()
            
    def claim_stone(self, player: int, stone: int):
        self.board.claim_stone(player, stone)
        
    def is_game_over(self):
        res = self.board.is_board_terminal()
        if res == 1:
            self.game_over = True
            print("Player 1 wins.")
            return
        if res == 2:
            self.game_over = True
            print("Player 2 wins.")
            return
        
    def make_move(self, player: int, copy=True):
        if copy:
            state = self.board.copy()
        else:
            state = self.board
        claims = self.players[player].claim(state)
        for s in claims:
            self.claim_stone(player, s)
        card, stone = self.players[player].choose_stone_and_card(self.hands[player], state)
        if card == 0 and stone == 0:
            return
        self.board.place_card(stone, self.hands[player].pop(card), player)
        self.hands[player].append(self.board.draw_card())
        
            