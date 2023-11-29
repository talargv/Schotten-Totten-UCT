from schotten_again import Hand,Card

strength_func = Hand.strength_from_list

with open('cards_ordered.txt') as cards_file:
    L = [list(map(lambda s: Card(int(s[0]),int(s[1])),line.rstrip('\n').split(','))) for line in cards_file.readlines()]
    

for i in range(1,len(L)):
    try:
        assert strength_func(L[i]) <= strength_func(L[i-1])
    except Exception:
        print(i)