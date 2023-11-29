from basic_players import AnalogPlayer, RandomPlayer, HandStrengthEstimate
from schotten_again import Game, Card, BoardWithFakes, Board
from MCTS_v2 import QuiteAwfulPlayer, UCTPlayer

import random
import time

CARDS_IN_HAND = 6

"""for i in range(100):
    print(i)
    game = Game(QuiteAwfulPlayer(), QuiteAwfulPlayer())
    try:
        game.play(show=False)
    except KeyboardInterrupt:
        print(game.board)
        print(game.board.stones)
        print([str(card) for card in game.board.deck.deck])
        print([str(card) for card in game.hands[0]])
        print([str(card) for card in game.hands[1]])"""
for _ in range(1):
    game = Game(UCTPlayer(max_iter=150), QuiteAwfulPlayer(), BoardWithFakes,owner=True)
    #game = Game(QuiteAwfulPlayer(), QuiteAwfulPlayer(), BoardWithFakes, owner=True)
    start = time.time()
    game.play(show=False)
    end = time.time()
    print(end-start)
"""try:
    res = game.play(show=True)
except (KeyboardInterrupt) as err:
    print(game.board)
    print(game.board.stones)
    print([str(card) for card in game.board.deck.deck])
    print([str(card) for card in game.hands[0]])
    print([str(card) for card in game.hands[1]])
    raise err"""
#game.play(show=False)
#print(res)
#game.play(show=False)
#board = game.board
#print(board)
#board2 = BoardWithFakes(**vars(board))
#print(board2)