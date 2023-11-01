from basic_players import AnalogPlayer, RandomPlayer, HandStrengthEstimate
from schotten_again import Game, Card
from MCTS_v2 import QuiteAwfulPlayer, UCTPlayer

import random

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
        
game = Game(UCTPlayer(max_iter=1000), QuiteAwfulPlayer())
res = game.play()
print(res)