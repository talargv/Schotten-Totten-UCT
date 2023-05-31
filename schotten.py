import random as rand
from abc import ABC, abstractmethod, staticmethod

#COLORS = {1:"Purple", 2:"Brown", 3:"Red", 4:"Yellow", 5:"Green", 6:"Blue"}
NUM_OF_COLORS = 6
NUM_OF_NUMS = 9
NUM_OF_STONES = 9

class Card():
    def __init__(self, num: int, color: int, fake = False):
        self.num = num
        self.color = color
        self.fake = fake 
        # hands will contain best possible hand
        # with fake == True indicating that the card is not really placed by the player

    def __eq__(self, card):
        return self.num == card.num and self.color == card.color


class Deck():
    def __init__(self):
        self.deck = []
        for i in range(1,NUM_OF_COLORS + 1):
            for j in range(1, NUM_OF_NUMS + 1):
                self.deck.append(Card(j,i))
        rand.shuffle(self.deck)

    def draw_card(self):
        return self.deck.pop()

class Board():
    def __init__(self):
        self.deck = Deck()
        self.stones = [0 for _ in range(NUM_OF_STONES)] 
        # 0 - unclaimed 1 - claimed p1 2 - claimed p2
        self.cards = [[[Card(9,1,True), Card(8,1,True),Card(7,1,True)] for _ in range(NUM_OF_STONES)] for _ in range(2)]
        # cards[i][j][:3] best possible card triplet player i can have in front of stone j
        # cards[i][j][k].fake == False if and only if player i put card k in front of stone j
        # cards[i][j][3] == 1 if player i put 3 cards in front of stone j first
        # initialized best hand is a purple 7-8-9 color run
        # real ones are always at the beginning
        self.index_of_fakes = {"91":[(i,j) for i in range(2) for j in range(NUM_OF_STONES)],
                               "81":[(i,j) for i in range(2) for j in range(NUM_OF_STONES)],
                               "71":[(i,j) for i in range(2) for j in range(NUM_OF_STONES)]}
        # index_of_fakes["{num}{color}"] all places on board as (player,stone) tuples with a fake - Card(num,color,True)
        self.cards_on_board = [False for _ in range(NUM_OF_NUMS*NUM_OF_COLORS)] 
        # cards_on_board[k*NUM_OF_COLORS + j] == True if and only if card with color j+1 and num k+1 is on the board
    
    @staticmethod
    def convert_to_cards_on_board_index(num: int, color: int):
        """Converts num, color to an appropriate index in the cards_on_board variable"""
        return (num-1)*NUM_OF_COLORS + color-1

    def draw_card(self):
        return self.deck.draw_card()
    
    def claim_stone(self,player: int, stone: int):
        self.stones[stone] = player

    def clear_fakes(self, player: int, stone: int):
        for i in range(len(self.cards[player][stone])):
            if type(self.cards[player][stone][i]) == Card and self.cards[player][stone][i].fake == True: 
                self.cards[player][stone] = self.cards[player][stone][:i] # real cards are always at the beginning
                return

    def __best_card_with_two_placed(self, player: int, stone: int):
        """logic for best card available when two are already in place
            returns tuple(num: int, color: int) of a possible fake to add"""
        diff = abs(self.cards[player][stone][0].num - self.cards[player][stone][1].num)
        color = False

        if self.cards[player][stone][0].color == self.cards[player][stone][1].color:
            # color or color run is possible
            color = True

        if diff == 0: 
            # then only three of a kind is possible
            index = Board.convert_to_cards_on_board_index(self.cards[player][stone][0].num,1)
            for j in range(index, index+NUM_OF_COLORS):
                if self.cards_on_board[j] == False:
                    return (self.cards[player][stone][0].num, j+1)
        elif diff <= 2:
            # a run may be possible
            possible_nums = list(filter(
                lambda x: abs(self.cards[player][stone][0].num - x) <= 2 and abs(self.cards[player][stone][1].num - x) <= 2,
                (n for n in range(1, NUM_OF_NUMS + 1))))
            possible_nums.sort(reverse=True) # try best option of run first
            if color:
                # a color run may be possible
                for n in possible_nums:
                    if self.cards_on_board[Board.convert_to_cards_on_board_index(n, self.cards[player][stone][0].color)] == False:
                        return (n, self.cards[player][stone][0].color)
                # else a color might be possible 
                for k in range(1, NUM_OF_NUMS + 1):
                    if self.cards_on_board[Board.convert_to_cards_on_board_index(k,self.cards[player][stone][0].color)] == False:
                        return (k, self.cards[player][stone][0].color)
            else:
                # only a run might be available
                for n in possible_nums:
                    index = Board.convert_to_cards_on_board_index(n,1)
                    for j in range(NUM_OF_COLORS):
                        if self.cards_on_board[index+j] == False:
                            return (n,j+1)
        # only sum is available
        for i in range(len(self.cards_on_board)-1, -1, -1):
            if self.cards_on_board[i] == False:
                return ((i // NUM_OF_COLORS)+1, (i % NUM_OF_COLORS)+1)

    def __best_cards_with_one_placed_gen(self, num: int, color: int):
        """logic for best card available when one is already in place
            yields duos of tuple(num: int, color: int) of a possible fake to add"""
        POSSIBLE_RUNS = filter(lambda nums: nums[0] <= NUM_OF_NUMS and nums[1] >= 0,[(num+2, num+1), (num+1, num-1), (num-1, num-2)])
        # try color run
        for possible_run in POSSIBLE_RUNS:
            yield [(possible_run[0], color),(possible_run[1], color)]
        # try three of a kind 

        # generate best color combinations by order
        j,k = NUM_OF_NUMS,NUM_OF_NUMS - 1
        # MIGHT NOT WORK IF NUM_OF_NUMS IS EVEN 
        while True: 
            yield [(j, color), (k, color)]
            if j == 2 and k == 1:
                break
            if j+k % 2 == 1:
                if k == 1:
                    j -= 1
                elif j == NUM_OF_NUMS:
                    k -= 1
                else:
                    j += 1
                    k -= 1
            else:
                if j-k == 2:
                    if k == 1:
                        j -= 1
                    else:
                        k -= 1
                else:
                    j -= 1
                    k += 1
        # try run
        for possible_run in POSSIBLE_RUNS:
            for c in range(1, NUM_OF_COLORS + 1):
                for cc in range(1, NUM_OF_COLORS + 1):
                    yield[(possible_run[0], c), (possible_run[1], cc)]
        # only sum available
        j,k = NUM_OF_NUMS, NUM_OF_NUMS
        while True: 
            for c in range(1, NUM_OF_COLORS + 1):
                for cc in range(1, NUM_OF_COLORS + 1):
                    yield [(j, c), (k, cc)]
            if j == 1 and k == 1:
                break
            if j+k % 2 == 1:
                if k == 1:
                    j -= 1
                elif j == NUM_OF_NUMS:
                    k -= 1
                else:
                    j += 1
                    k -= 1
            else:
                if j-k == 0:
                    k -= 1
                else:
                    j -= 1
                    k += 1

    @staticmethod
    def __color_combinations():
        """generates all color triplets"""
        for i in range(3, NUM_OF_COLORS+1):
            for j in range(2,i):
                for k in range(1,j):
                    yield(i,j,k)

    def __best_cards_with_zero_placed_gen(self):
        # try color run
        POSSIBLE_RUNS = ((n,n+1,n+2) for n in range(NUM_OF_NUMS-2,0,-1))
        for possible_run in POSSIBLE_RUNS:
            for c in range(1, NUM_OF_COLORS+1):
                yield [(n,c) for n in possible_run]
        # try three of a kind
        for num in range(NUM_OF_NUMS, 0, -1):
            for combination in Board.__color_combinations():
                yield [(num, c) for c in combination]
        # generate best color combinations by order

        

    def get_best_hand(self, player: int, stone: int):
        """returns list((num, color)) of fakes to add"""
        cards_in_place = len(self.cards[player][stone])
        if cards_in_place >= 3:
            print("Wrong call")
            return
        if cards_in_place == 2:
            return [self.__best_card_with_two_placed(player, stone)]
        if cards_in_place == 1:
            for options in self.__best_cards_with_one_placed_gen(self.cards[player][stone][0].num, self.cards[player][stone][0].color):
                if self.cards_on_board[Board.convert_to_cards_on_board_index(options[0][0], options[0][1])] == False and\
                    self.cards_on_board[Board.convert_to_cards_on_board_index(options[1][0], options[1][1])] == False:
                    return options
        if cards_in_place == 0:
            return


                

                

    def update_fakes(self, card: Card):
        """deletes all fake occurrences of card
            calls get_best_hand to replace a new possible best hand"""
        for (player, stone) in self.index_of_fakes["{num}{color}".format(num = card.num, color = card.color)]:
            self.clear_fakes(player, stone)
            new_fakes = self.get_best_hand(player, stone)
            self.cards[player][stone].extend(map(lambda pair: Card(pair[0], pair[1], True), new_fakes))
            for fake_suggestion in new_fakes:
                try:
                    self.index_of_fakes["{num}{color}".format(num=fake_suggestion[0],color=fake_suggestion[1])].append((player,stone))
                except KeyError:
                    self.index_of_fakes["{num}{color}".format(num=fake_suggestion[0],color=fake_suggestion[1])] = [(player, stone)]
        self.index_of_fakes.pop("{num}{color}".format(num = card.num, color = card.color))
                    

    def place_card(self,stone: int, card: Card, player: int):
        self.cards[stone][player].insert(0, card)
        self.cards_on_board[Board.convert_to_cards_on_board_index(card.num, card.color)] = True
        self.update_fakes(card)
        
        if (len(self.cards[stone][player]) == 3 and len(self.cards[stone][1-player]) < 3):
            self.cards[stone][player].append(1)

class Player(ABC):
    @abstractmethod
    def choose_stone_and_card(self, state: list, hand: list) -> tuple(int, int):
        """Gets his side of the stones and hand. \n
        Return (index of chosen card in hand, index of chosen stone)"""
        pass

class Game():
    def __init__(self,p1: Player, p2: Player, cards_in_hand = 6):
        self.board = Board()
        self.players = [p1, p2]
        self.hands = [[self.board.draw_card() for i in range(cards_in_hand)] for _ in range(2)]  # [hand of player 1, hand of player 2]
        self.game_over = False

    def get_strength(self, cards: list) -> int:
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
        copy_of.sort(lambda x: x.num)
        if (copy_of[0].num + 1 == copy_of[1].num and copy_of[1].num + 1 == copy_of[2].num):
            run = True
        
        if (color,run) == (False, False):
            return first + (sum(x.num for x in copy_of)*2) - 4
        if (color,run) == (True, False):
            return first + 54 + (sum(x.num for x in copy_of)*2)
        if (color,run) == (False, True):
            return first + 46 + copy_of[0]*2
        return first + 122 + copy_of[0]*2


    def claim_stone(self, player: int):
        pass

    def is_game_over(self):
        count = [0,0,0]
        neighboring_stones_count, neighboring_stones_player = 0, 0
        for p in self.board.stones:
            if neighboring_stones_count == 3 and neighboring_stones_player != 0:
                break
            if neighboring_stones_player == p:
                neighboring_stones_count += 1
            else:
                neighboring_stones_count = 1
                neighboring_stones_player = p
            count[p] += 1
        if count[1] == 5:
            self.game_over = True
            print("Player 1 Won.")
            return
        if count[2] == 5:
            self.game_over = True
            print("Player 2 Won.")
            return
        


    def make_move(self, player: int):
        self.claim_stone(player)
        self.is_game_over()
        if self.game_over:
            return
        card, stone = self.players[player].choose_stone_and_card(self.board.cards[player], self.hands[player])
        self.board.place_card(stone, self.hands[player].pop(card), player)
        self.hands[player].append(self.board.draw_card())
        




