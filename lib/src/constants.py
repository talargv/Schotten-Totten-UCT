COLORS = {1:"Purple", 2:"Brown", 3:"Red", 4:"Yellow", 5:"Green", 6:"Blue"}
NUM_OF_COLORS = 6
NUM_OF_NUMS = 9
NUM_OF_STONES = 9
CARDS_IN_HAND = 6
NUM_OF_PLAYERS = 2
STONE_CARDS_LIMIT = 3
with open('cards_ordered.txt') as cards_file:
    ALL_TRIPLETS = [list(map(lambda s: Card(int(s[0]),int(s[1])),line.rstrip('\n').split(','))) for line in cards_file.readlines()]