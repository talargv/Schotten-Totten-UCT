NUM_OF_NUMS = 9
NUM_OF_COLORS = 6
from schotten_again import Card, Hand
from itertools import combinations, filterfalse

get_card_stream = lambda _=None : (Card(num,color) for num in range(1,NUM_OF_NUMS+1) for color in range(1,NUM_OF_COLORS+1))

for card in get_card_stream():
    duos = filterfalse(lambda d: card in d, combinations(get_card_stream(), 2))
    duos_sorted = sorted(duos, key=lambda d: Hand.strength_from_list(d+(card,)), reverse=True)
    with open(f"./combinations_sorted/duos_sorted_{card.num}{card.color}", 'w') as f:
        for d in map(lambda x: f"{x[0].num}{x[0].color},{x[1].num}{x[1].color}\n",duos_sorted):
            f.write(d)