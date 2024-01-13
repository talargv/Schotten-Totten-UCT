import random as rand

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Union, Type, Tuple, Optional
from itertools import chain

global COLORS
global NUM_OF_COLORS
global NUM_OF_NUMS
global NUM_OF_STONES

COLORS = {1:"Purple", 2:"Brown", 3:"Red", 4:"Yellow", 5:"Green", 6:"Blue"}
NUM_OF_COLORS = 6
NUM_OF_NUMS = 9
NUM_OF_STONES = 9
CARDS_IN_HAND = 6
NUM_OF_PLAYERS = 2
class Card():
    def __init__(self, num: int, color: int):
        """num in [1,NUM_OF_NUMS], color in [1,NUM_OF_COLORS]"""
        if num < 1 or num > 9 or color < 1 or color > 6:
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
        if isinstance(other, tuple):
            try:
                assert len(other) == 2
            except AssertionError:
                raise TypeError()
            return self.num == other[0] and self.color == other[1]
        else:
            return self.num == other.num and self.color == other.color

class Hand():
    def __init__(self, cards: List[Card]=None):
        """Class for handling triplets in front of stones."""
        if cards is None:
            self.hand = []
        else:
            if len(cards) > 3:
                raise ValueError("Too many cards")
            self.hand = cards
    
    def __len__(self):
        return len(self.hand)
        
    def append(self, card: Card):
        if len(self.hand) == 3:
            raise ValueError(f"Too many cards in hand\n{[str(card) for card in self.hand]}")
        self.hand.append(card)
        
    def extend(self, cards,copy=True):
        if len(self) + len(cards) > 3:
            raise ValueError("Too many cards")
        if type(cards) == list:
            self.hand.extend(cards)
        #elif copy:
        #    self.hand.extend(cards.hand.copy())
        else:
            self.hand.extend(cards.hand)
    
    def pop(self, index=-1) -> Optional[Card]:
        if len(self) == 0 and (index == -1 or index == 0):
            return
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
        if hand[0].num == hand[1].num and hand[1].num == hand[2].num:
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
            if available_cards[card.num-1][card.color-1]:
                return False
        return True
       
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
    
def close_wrapper(func):
    def try_or_close(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            self.close()
            raise e
    return try_or_close
                     
class Board():
    def __init__(self,**kwargs):
        self.deck = kwargs.get('deck',None)
        if self.deck is None:
            self.deck = Deck()
        self.stones = kwargs.get('stones',None) 
        if self.stones is None:
            self.stones = [0 for _ in range(NUM_OF_STONES)]
        # 0 - unclaimed 
        # 1 - claimed p1
        # 2 - claimed p2
        self.cards = kwargs.get('cards', None)
        if self.cards is None:
            self.cards = [[Hand() for _ in range(NUM_OF_STONES)] for i in range(2)]
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
    
    def copy(self):
        items = {}
        items['deck'] = self.deck.copy()
        items['stones'] = self.stones.copy()
        items['cards'] = [[self.cards[i][j].copy() for j in range(NUM_OF_STONES)] for i in range(2)]
        items['advantage'] = self.advantage.copy()
        items['cards_on_board'] = [self.cards_on_board[i].copy() for i in range(NUM_OF_NUMS)]
        return Board(**items)
    
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
        
    def claim_stone(self,player: int, stone: int, show=True):
        """Does nothing when stone is claimed"""
        if self.stones[stone] != 0:
            return
        if not Board.is_legal_claim(self.cards[player][stone],self.cards[1-player][stone],
                                    self.advantage[stone] == player+1,self.cards_on_board):
            if show:
                print(f"Invalid claim")
            return
        self.stones[stone] = player+1
        
    def place_card(self, stone: int, card: Card, player: int):
        self.cards[player][stone].append(card)
        if len(self.cards[player][stone]) == 3 and self.advantage[stone] == 0:
            self.advantage[stone] = player + 1
        self.cards_on_board[card.num-1][card.color-1] = True

    def close(self):
        pass

class FakesGen():
    def __init__(self, hand: Hand):
        self.length = len(hand)
        if self.length == 0:
            self.source = open('./combinations_sorted/triplets_sorted.txt')
        elif self.length == 1:
            card = hand[0]
            self.source = open(f'./combinations_sorted/duos_sorted_{card.num}{card.color}')
        elif self.length == 2:
            cards = tuple(hand.tolist(copy=False))
            card_stream = map(lambda card: (card,),
                                filter(lambda card: not card in hand,(Card(num,color) for num in range(1,NUM_OF_NUMS+1) for color in range(1,NUM_OF_COLORS+1))))
            self.source = iter(sorted(card_stream, key=lambda x: Hand.strength_from_list(cards+x), reverse=True))
        else:
            self.source = iter([[]])
       
    @staticmethod
    def key_to_card_list(key: str) -> List[Card]:
        if len(key) == 0:
            return []
        return list(map(lambda s: Card(int(s[0]),int(s[1])),key.rstrip('\n').split(',')))
    
    @staticmethod
    def card_list_to_key(card_list: List[Card]):
        if len(card_list) == 0:
            return ''
        return ','.join(map(lambda card: f'{card.num}{card.color}', card_list))
            
    def __iter__(self):
        return self
            
    def __next__(self) -> List[Card]:
        try:
            next_cards = next(self.source)
        except StopIteration:
            self.close()
            return
        except ValueError:
            return
        if self.length < 2:
            return FakesGen.key_to_card_list(next_cards)
        elif self.length == 2:
            return list(next_cards)
        else:
            return next_cards
                
    def close(self):
        if self.length < 2:
            self.source.close()

"""
class FakesGen():
    def __init__(self, hand: Hand, index=0, pre_computed = None):
        
        self.hand = hand
        self.index = index
        if not pre_computed is None:
            self.source = pre_computed
        else:
            
            if len(hand) == 0:    
                with open('./combinations_sorted/triplets_sorted.txt') as cards_file:
                    hand_cards = self.hand.tolist(copy=False)
                    self.source = list(filter(
                        lambda cards: all(map(lambda card: card in cards, hand_cards)),
                        [list(map(lambda s: Card(int(s[0]),int(s[1])),line.rstrip('\n').split(','))) for line in cards_file.readlines()]
                        ))
            elif len(hand) == 1:
                card = hand[0]
                with open(f'./combinations_sorted/duos_sorted_{card.num}{card.color}') as cards_file:
                    self.source = [list(map(lambda s: Card(int(s[0]),int(s[1])),line.rstrip('\n').split(','))) for line in cards_file.readlines()]
            elif len(hand) == 2:
                cards = tuple(hand.tolist(copy=False))
                card_stream = map(lambda card: (card,),
                                  filter(lambda card: not card in hand,(Card(num,color) for num in range(1,NUM_OF_NUMS+1) for color in range(1,NUM_OF_COLORS+1))))
                self.source = sorted(card_stream, key=lambda x: Hand.strength_from_list(cards+x), reverse=True)
            else:
                self.source = [()]

    def update(self, cards_on_board: List[List[int]]):
        hand_cards = self.hand.tolist(copy=False)
        not_on_board = lambda card: (not cards_on_board[card.num-1][card.color-1]) or card in hand_cards
        while True:
            cards = self.source[self.index]
            if all(map(not_on_board, cards)):
                break
            self.index += 1
        
    @property
    def current(self):
        try:
            return list(chain(self.hand, self.source[self.index]))
        except IndexError:
            raise StopIteration
        
    def copy(self):
        return FakesGen(self.hand, index=self.index, pre_computed=self.source)
"""  

class WorkState():
    def __init__(self):
        """
        Manages computation of fakes generation.
        
        Format of key for both maps is '{card1.num}{card1.color},{card2.num}{card2.color},...'
        """
        # Map<str, List<Card>>
        self.__data = defaultdict(list)
        # Map<str, FakesGen>
        self.__work = {}
        
    @close_wrapper    
    def get(self, key: str, index: int):
        self.__add(key)
        try:
            return self.__data[key][index]
        except IndexError:
            s="Break"
            raise IndexError()
    
    @close_wrapper
    def __add(self, key: str) -> None:
        """
        Add a new key to state.
        
        Does nothing if the key already exists.
        """
        if key in self.__work:
            return
        key_to_hand = Hand(FakesGen.key_to_card_list(key))
        self.__work[key] = FakesGen(key_to_hand)
        self.__do_work(key)
    
    @close_wrapper
    def __do_work(self, key: str):
        next_cards = next(self.__work[key])
        if not next_cards is None:
            self.__data[key].append(next_cards)
    
    @close_wrapper
    def update(self, keys: List[str], indices: List[int], cards_on_board: List[List[int]]) -> None:
        """
        Updates indices in place.
        
        Assumes len(keys) == len(indices)
        Assumes keys exists in self.work
        """
        for i in range(len(keys)):
            key = keys[i]
            hand_cards = FakesGen.key_to_card_list(key)
            not_on_board = lambda card: (not cards_on_board[card.num-1][card.color-1]) or card in hand_cards
            
            while True:
                index = indices[i]
                
                cards = self.get(key, index)
                
                if all(map(not_on_board, cards)):
                    break
                self.__do_work(key)
                indices[i] = index+1 if index+1 < len(self.__data[key]) else index
    
    def close(self):
        for fakes_gen in self.__work.values():
            fakes_gen.close()

class Fakes():
    def __init__(self, 
                 hands: List[List[Hand]], 
                 cards_on_board: List[List[int]],
                 pre_computed: WorkState = None, 
                 indices: List[List[int]] = None):
        
        if not pre_computed is None:
            self.work_state = pre_computed
        else:
            self.work_state = WorkState()
        
        if indices is not None:
            self.indices = indices
        else:
            self.indices = [[0 for stone in range(NUM_OF_STONES)] for player in range(NUM_OF_PLAYERS)]
        if not hands is None:    
            self.update(hands, cards_on_board)
            
    def close(self):
        self.work_state.close()
    
    @close_wrapper
    def place_card(self, stone: int, player: int, hands: List[List[Hand]], cards_on_board: List[List[int]]):
        self.indices[player][stone] = 0
        self.update(hands, cards_on_board)
    
    @close_wrapper   
    def update(self, hands: List[List[Hand]], cards_on_board: List[List[int]]):
        flat_indices = list(chain(*self.indices))
        flat_keys = list(map(lambda hand: FakesGen.card_list_to_key(hand.tolist(copy=False)), chain(*hands)))
        self.work_state.update(flat_keys, flat_indices, cards_on_board)
        self.indices = [[flat_indices[stone + (player*9)] for stone in range(NUM_OF_STONES)] for player in range(NUM_OF_PLAYERS)]

    @close_wrapper                
    def get(self, player: int, stone: int, hand: Hand):
        index = self.indices[player][stone]
        key = FakesGen.card_list_to_key(hand.tolist(copy=False))
        fakes = self.work_state.get(key=key, index=index)
        return hand.tolist(copy=True) + fakes

    @close_wrapper
    def copy(self):
        return Fakes(hands=None,
                     cards_on_board=None,
                     pre_computed = self.work_state,
                     indices=[l[:] for l in self.indices])

class BoardWithFakes(Board):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fakes = kwargs.get('fakes', None)
        if self.fakes is None:
            self.fakes = Fakes(self.cards,self.cards_on_board)
    
    @close_wrapper    
    def change_pov(self):
        state = self.copy()
        
        cards = state.cards
        fakes_arr = state.fakes.indices
        stones = state.stones
        advantage = state.advantage
        
        state.stones = [stones[len(stones)-1-i] for i in range(len(stones))]
        state.advantage = [advantage[len(advantage)-1-i] for i in range(len(advantage))]
        
        stones = state.stones
        advantage = state.advantage
        
        for i in range(NUM_OF_STONES):
            if stones[i] == 1:
                stones[i] = 2
            elif stones[i] == 2:
                stones[i] = 1
            if advantage[i] == 1:
                advantage[i] = 2
            elif advantage[i] == 2:
                advantage[i] = 1
        
        cards[0] = [cards[0][NUM_OF_STONES-1-i] for i in range(len(cards[0]))]
        cards[1] = [cards[1][NUM_OF_STONES-1-i] for i in range(len(cards[1]))]
        cards[0], cards[1] = cards[1], cards[0]
        
        fakes_arr[0] = [fakes_arr[0][NUM_OF_STONES-1-i] for i in range(len(fakes_arr[0]))]
        fakes_arr[1] = [fakes_arr[1][NUM_OF_STONES-1-i] for i in range(len(fakes_arr[1]))]
        fakes_arr[0], fakes_arr[1] = fakes_arr[1], fakes_arr[0]
        
        return state
        
    @close_wrapper
    def copy(self):
        items = {}
        items['deck'] = self.deck.copy()
        items['stones'] = self.stones.copy()
        items['cards'] = [[self.cards[i][j].copy() for j in range(NUM_OF_STONES)] for i in range(2)]
        items['advantage'] = self.advantage.copy()
        items['cards_on_board'] = [self.cards_on_board[i].copy() for i in range(NUM_OF_NUMS)]
        items['fakes'] = self.fakes.copy()
        return BoardWithFakes(**items)
    
    def pop_from_stone(self,player,stone):
        raise Exception
    
    @close_wrapper
    def is_legal_claim(self, player: int, stone: int):
        if len(self.cards[player][stone]) < 3:
            return False
        val_player = Hand.strength_from_list(self.fakes.get(player, stone, self.cards[player][stone]))
        val_other = Hand.strength_from_list(self.fakes.get(1-player, stone, self.cards[1-player][stone]))
        # TEST
        """
        hand1 = self.cards[player][stone]
        hand2 = self.cards[1-player][stone]
        res_this = val_player > val_other or (val_player == val_other and self.advantage[stone] == player+1)
        res_that = Board.is_legal_claim(hand1, hand2, self.advantage[stone] == player+1, self.cards_on_board)
        if not res_this == res_that:
            s = 'BREAK'
        """
        # END TEST
        return val_player > val_other or (val_player == val_other and self.advantage[stone] == player+1)
    
    @close_wrapper
    def claim_stone(self,player: int, stone: int, show=True):
        """Does nothing when stone is claimed"""
        if self.stones[stone] != 0:
            return
        if not self.is_legal_claim(player, stone):
            if show:
                print(f"Invalid claim")
            return
        self.stones[stone] = player+1
        
    @close_wrapper        
    def place_card(self, stone: int, card: Card, player: int):
        super().place_card(stone, card, player)
        self.fakes.place_card(stone, player, self.cards, self.cards_on_board)
        

class Player(ABC):
    """Player always acts as if he is player 1.
    Board is received with other players card in the deck."""
    @abstractmethod
    def choose_stone_and_card(self, cards_in_hand: List[Card], board: Board, **kwargs) -> Tuple[int,int]:
        """if you cant make a move, return (-1,-1), otherwise (card, stone)"""
        available_stones = board.available_stones(0)
        if len(available_stones) == 0 or len(cards_in_hand) == 0:
            #print('No moves available')
            return (-1,-1)
        return 0, 0
    
    @abstractmethod
    def claim(self,board: Board) -> List[int]:
        return list(range(NUM_OF_STONES))
            
class Game():
    def __init__(self, p1: Type[Player], p2: Type[Player], board_gen, owner=False, **kwargs):
        tmp = kwargs.get('board', None)
        if tmp is None:
            self.board = board_gen()
        else:
            self.board = tmp
        self.players = [p1, p2]
        tmp = kwargs.get('hands', None)
        if tmp is None:
            self.hands = [[self.board.draw_card() for _ in range(CARDS_IN_HAND)] for p in range(2)]
        else:
            self.hands = tmp
        self.game_over = False
        self.owner = owner
    
    @close_wrapper
    def play(self, show=True):
        while not self.game_over:
            if show:
                print(self.board)
                print(f'Player 1, make your move: ')
            self.make_move(0,show)
            self.is_game_over(show)
            if self.game_over:
                return 0
            if show:
                print(f'Player 2, make your move: ')
            self.make_move(1,show)
            self.is_game_over(show)
        return 1
            
    def claim_stone(self, player: int, stone: int, show: bool=True):
        self.board.claim_stone(player, stone, show)
        
    def is_game_over(self, show=True):
        res = self.board.is_board_terminal()
        if res == 1:
            self.game_over = True
            if self.owner:
                print(self.board)
                print("\nGame Over")
            if self.owner:
                self.board.close()
            return
        elif res == 2:
            self.game_over = True
            if self.owner:
                print(self.board)
                print("\nGame Over")
            if self.owner:
                self.board.close()
            return
        
    def make_move(self, player: int, show=True):
        state = self.board.copy()
        if player == 1:
            state = self.board.change_pov()
        deck = []
        for i in range(1,NUM_OF_COLORS + 1):
            for j in range(1, NUM_OF_NUMS + 1):
                if (not self.board.cards_on_board[j-1][i-1]) and (not Card(j,i) in self.hands[player]):
                    deck.append(Card(j,i))
        state.deck = Deck(deck)
        claims = self.players[player].claim(state)
        if player == 1:
            claims = [NUM_OF_STONES-stone-1 for stone in claims]
        for s in claims:
            self.claim_stone(player, s, show)
            
        card, stone = self.players[player].choose_stone_and_card(self.hands[player], state)
        if card < 0 or stone < 0:
            return
        if player == 1:
            stone = NUM_OF_STONES-1-stone
        self.board.place_card(stone, self.hands[player].pop(card), player)
        drawn_card = self.board.draw_card()
        if not (drawn_card is None):
            self.hands[player].append(drawn_card)
            
    def close(self):
        self.board.close()