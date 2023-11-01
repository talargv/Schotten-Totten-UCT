from schotten import Board,Card
def get_strength(cards):
    """Gets 3 cards a player put in front of a stone, and possibly a 1 indicating he was first.\n
    {sum: 4-47, run: 48-61, color: 62-105, three-of-a-kind: 106-123, color-run: 124-139} 
    order by strength, and first == True adds 1"""
    first = 1 if len(cards) == 4 else 0

    if (cards[0].num == cards[1].num and cards[1].num == cards[2].num):
        return first + 104 + cards[0].num*2
        
    color, run = False, False
    if (cards[0].color == cards[1].color and cards[1].color == cards[2].color):
        color = True

    copy_of = cards[:3]
    copy_of.sort(key=lambda x: x.num)
    if (copy_of[0].num + 1 == copy_of[1].num and copy_of[1].num + 1 == copy_of[2].num):
        run = True
        
    if (color,run) == (False, False):
        return first + (sum(x.num for x in copy_of)*2) - 4
    if (color,run) == (True, False):
        return first + 54 + (sum(x.num for x in copy_of)*2)
    if (color,run) == (False, True):
        return first + 46 + copy_of[0].num*2
    return first + 122 + copy_of[0].num*2

for num1 in range(1,10):
    for num2 in range(1,10):
        for color1 in range(1,7):
            for color2 in range(1,7):
                if num1!= num2 or color1 != color2:
                    H = [(num1,color1),(num2,color2)]
                    g = list(Board.best_card_with_two_placed_gen([(num1,color1),(num2,color2)]))
                    for i in range(1,len(g)):
                        if (i%1024==0):
                            print(i)
                        prev_hand = [Card(num1,color1),Card(num2,color2)]
                        prev_hand.append(Card(g[i-1][0][0],g[i-1][0][1]))
                        curr_hand = [Card(num1,color1),Card(num2,color2)]
                        curr_hand.append(Card(g[i][0][0],g[i][0][1]))
#                        try:
#                            if g.index(g[i]) == i and (get_strength(prev_hand) < get_strength(curr_hand)) and (not (num,color) in g[i]) and g.index([g[i][1],g[i][0]]) == i:
#                                print(g[i],g[i-1])
#                        except ValueError:
#                            print('')
                        if g.index(g[i]) == i and (get_strength(prev_hand) < get_strength(curr_hand)) and (not g[i][0] in H) and (not g[i-1][0] in H):
                            print(g[i],g[i-1])