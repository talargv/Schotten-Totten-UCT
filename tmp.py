from itertools import product
from collections import Counter
# generate list
L = []
# color-run
for num in range(7,0,-1):
    for color in range(1,7):
        L.append(f"{num}{color},{num+1}{color},{num+2}{color}")
# three of a kind        
for num in range(9,0,-1):
    for color1 in range(1,5):
        for color2 in range(color1+1,6):
            for color3 in range(color2+1,7):
                L.append(f"{num}{color1},{num}{color2},{num}{color3}")
# color                
tmp = []
for num1 in range(1,8):
    for num2 in range(num1+1,9):
        for num3 in range(num2+1,10):
            if num1+1 == num2 and num2+1 == num3:
                continue
            tmp.append((num1,num2,num3))
tmp.sort(key = lambda x: sum(x),reverse=True)
for t in tmp:
    for color in range(1,7):
        L.append(f"{t[0]}{color},{t[1]}{color},{t[2]}{color}")
# run
for num in range(7,0,-1):
    for colors in filter(lambda x: x[0] != x[1] or x[1] != x[2] or x[2] != x[0], product(range(1,7), repeat=3)):
        L.append(f"{num}{colors[0]},{num+1}{colors[1]},{num+2}{colors[2]}")
        
# sum
def to_card(u: int):
    y = ((u-1) % 6) + 1
    x = (u - y + 6) // 6
    return (x, y)

def is_three_of_a_kind(cards):
    card1, card2, card3 = cards
    return card1[0] == card2[0] and card2[0] == card3[0]

def is_color(cards):
    card1, card2, card3 = cards
    return card1[1] == card2[1] and card2[1] == card3[1]

def is_run(cards):
    nums = [card[0] for card in cards]
    nums.sort()
    return nums[0]+1 == nums[1] and nums[1]+1 == nums[2]

tmp = []
for num1 in range(1,53):
    for num2 in range(num1+1, 54):
        for num3 in range(num2+1, 55):
            cards = (to_card(num1), to_card(num2), to_card(num3))
            if not (is_three_of_a_kind(cards) or is_color(cards) or is_run(cards)):
                tmp.append(cards)
tmp.sort(key=lambda cards: cards[0][0]+cards[1][0]+cards[2][0], reverse=True)
                
L.extend(map(lambda cards: f"{cards[0][0]}{cards[0][1]},{cards[1][0]}{cards[1][1]},{cards[2][0]}{cards[2][1]}",tmp))

with open("cards_ordered.txt", 'w') as cards_ordered_file:
    cards_ordered_file.write("\n".join(L))
    
#C = Counter(L)
#print(list(filter(lambda key: C[key] > 1,C.keys())))