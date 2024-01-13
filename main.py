from schotten_again import Game, BoardWithFakes
from basic_players import AnalogPlayer
from MCTS_v2 import UCTPlayer, QuiteAwfulPlayer

p1 = AnalogPlayer()
p2 = UCTPlayer(max_iter=100)

game = Game(p2, p1, BoardWithFakes, True)
game.play(show=False)