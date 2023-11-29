from card import Card
from deck import Deck
from player import Player
from constants import *

class Game():
    def __init__(self, p1: Player, p2: Player, board_gen, **kwargs):
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
    
    
    def play(self, show=True):
        while not self.game_over:
            #print(self.board)
            if show:
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
            if show:
                print("Player 1 wins.")
            return
        if res == 2:
            self.game_over = True
            if show:
                print("Player 2 wins.")
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