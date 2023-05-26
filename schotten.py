import random as rand
from abc import ABC, abstractmethod

#COLORS = {1:"Purple", 2:"Brown", 3:"Red", 4:"Yellow", 5:"Green", 6:"Blue"}
NUM_OF_COLORS = 6
NUM_OF_NUMS = 9
NUM_OF_STONES = 9

class Card():
    def __init__(self, num: int, color: int, fake = False):
        self.num = num
        self.color = color
        self.fake = fake 
        # hands will contain best possible hand
        # with fake == True indicating that the card is not really placed by the player

    def __eq__(self, card):
        return self.num == card.num and self.color == card.color


class Deck():
    def __init__(self):
        self.deck = []
        for i in range(1,NUM_OF_COLORS + 1):
            for j in range(1, NUM_OF_NUMS + 1):
                self.deck.append(Card(j,i))
        rand.shuffle(self.deck)

    def draw_card(self):
        return self.deck.pop()

class Board():
    def __init__(self):
        self.deck = Deck()
        self.stones = [0 for _ in range(NUM_OF_STONES)] 
        # 0 - unclaimed 1 - claimed p1 2 - claimed p2
        self.cards = [[[Card(9,1,True), Card(8,1,True),Card(7,1,True)] for _ in range(NUM_OF_STONES)] for _ in range(2)]
        # cards[i][j][:3] best possible card triplet player i can have in front of stone j
        # cards[i][j][k].fake == False if and only if player i put card k in front of stone j
        # cards[i][j][3] == 1 if player i put 3 cards in front of stone j first
        # initialized best hand is a purple 7-8-9 color run
        # real ones are always at the beginning
        self.index_of_fakes = {"91":[(i,j) for i in range(2) for j in range(NUM_OF_STONES)],
                               "81":[(i,j) for i in range(2) for j in range(NUM_OF_STONES)],
                               "71":[(i,j) for i in range(2) for j in range(NUM_OF_STONES)]}
        # index_of_fakes["{num}{color}"] all places on board as (player,stone) tuples with a fake - Card(num,color,True)

    def draw_card(self):
        return self.deck.draw_card()
    
    def claim_stone(self,player: int, stone: int):
        self.stones[stone] = player

    def place_card(self,stone: int, card: Card, player: int):
        self.cards[stone][player].insert(0, card)
        change = False # == True if card has a fake copy 
        for i in range(len(self.cards[stone][player])):
            card = self.cards[stone][player][i]
            if card == self.cards[stone][player][0] and card.fake == True:
                self.cards[stone][player].pop(i)
                change = True
        if not change:
            self.cards[stone][player].pop()
        
        if (len(self.cards[stone][player]) == 3 and len(self.cards[stone][1-player]) < 3):
            self.cards[stone][player].append(1)

class Player(ABC):
    @abstractmethod
    def choose_stone_and_card(self, state: list, hand: list) -> tuple(int, int):
        """Gets his side of the stones and hand. \n
        Return (index of chosen card in hand, index of chosen stone)"""
        pass

class Game():
    def __init__(self,p1: Player, p2: Player, cards_in_hand = 6):
        self.board = Board()
        self.players = [p1, p2]
        self.hands = [[self.board.draw_card() for i in range(cards_in_hand)] for _ in range(2)]  # [hand of player 1, hand of player 2]
        self.game_over = False

    def get_strength(self, cards: list) -> int:
        """Gets 3 cards a player put in front of a stone, and possibly a 1 indicating he was first.\n
        {sum: 0-25, run: 27, color: 29, three-of-a-kind: 31, color-run: 33} and first adds 1"""
        strength = 1 if len(cards) == 4 else 0

        if (cards[0].num == cards[1].num and cards[1].num == cards[2].num):
            return strength + 31
        
        color, run = False, False
        if (cards[0].color == cards[1].color and cards[1].color == cards[2].color):
            color = True

        copy_of = cards[:3]
        copy_of.sort(lambda x: x.num)
        if (copy_of[0].num + 1 == copy_of[1].num and copy_of[1].num + 1 == copy_of[2].num):
            run = True
        
        if (color,run) == (False, False):
            return strength + sum(x.num for x in copy_of)
        if (color,run) == (True, False):
            return strength + 29
        if (color,run) == (False, True):
            return strength + 27
        return strength + 33


    def claim_stone(self, player: int):
        pass

    def is_game_over(self):
        count = [0,0,0]
        neighboring_stones_count, neighboring_stones_player = 0, 0
        for p in self.board.stones:
            if neighboring_stones_count == 3 and neighboring_stones_player != 0:
                break
            if neighboring_stones_player == p:
                neighboring_stones_count += 1
            else:
                neighboring_stones_count = 1
                neighboring_stones_player = p
            count[p] += 1
        if count[1] == 5:
            self.game_over = True
            print("Player 1 Won.")
            return
        if count[2] == 5:
            self.game_over = True
            print("Player 2 Won.")
            return
        


    def make_move(self, player: int):
        self.claim_stone(player)
        self.is_game_over()
        if self.game_over:
            return
        card, stone = self.players[player].choose_stone_and_card(self.board.cards[player], self.hands[player])
        self.board.place_card(stone, self.hands[player].pop(card), player)
        self.hands[player].append(self.board.draw_card())
        




