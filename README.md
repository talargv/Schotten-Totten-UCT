# UCT for Schotten Totten
## Description
Implementation of the Monte Carlo Tree Search - based algorithm Upper Confidence Bound for Trees (more info can be found [here](http://www.incompleteideas.net/609%20dropbox/other%20readings%20and%20resources/MCTS-survey.pdf)), for the two-player card game Schotten Totten.
More info about Schotten Totten game and it's rules can be found in [the rulebook](https://cdn.1j1ju.com/medias/d5/72/2f-schotten-totten-rulebook.pdf).

The project aims to implement a good enough bot based on the UCT algorithm to compete against a human player.
_Current implementation is too slow to do enough iterations to be competitive. A seperate project aims to implement efficiently in Rust for better performance_

## Quickstart
You can play against the UCT bot by running ```python main.py``` in the command line. *The version provided in main.py does 100 iterations of UCT. You can tweak the number of iterations by changing the ```max_iter``` variable*

## Using Game and Player
The game is played using the API provided by the Game class. A game is played by calling the **play** method.

The game is constructed by calling ```Game(p1, p2, board_gen, owner)```, where:
- **p1\p2** - Instances of types implementing Player. current players available:
  - **RandomPlayer** - Randomly chooses moves (moves are uniformly distributed).
  - **AnalogPlayer** - A manualy controlled player *(such as used in ```main.py```)* 
  - **QuiteAwfulPlayer** - Randomly chooses moves, where possibly good moves are more likely to be chosen.
  - **UCTPlayer** - Implements UCT, where simulations are carried out using QuiteAwfulPlayer.
- **board_gen** - A class implementing a board. **It is _highly suggested_ to use BoardWithFakes**. It caches some calculations locally to speed up logics for determining which claims for stones are legitimate.
- **owner** - True iff the game is run through this instance. _This is relevant when using BoardWithFakes, as both the main game and simulations carried out in UCT use shared resources, and need to be closed at the end\ when an error is raised_.

The ```Player``` class is an abstract class that contains the logic for players to carry out moves.
A Player implements the following methods:
- ```choose_stone_and_card``` - Gets the cards the player has in hand and a board, and returns two indices, indicating the index of the card in hand to play, and the stone index to put in front.
- ```claim``` - Gets a board and returns a list of indices of stones that the player claims. _The method has a default implementation that tries to claim all stones every turn_.
