import itertools
import random as rand
from abc import ABC, abstractmethod
from typing import List, Tuple, Union, Type

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
    
    def __repr__(self) -> str:
        return f"{self.num}{self.color}{'F' if self.fake else 'T'}"


class Deck():
    def __init__(self):
        self.deck = []
        for i in range(1,NUM_OF_COLORS + 1):
            for j in range(1, NUM_OF_NUMS + 1):
                self.deck.append(Card(j,i))
        rand.shuffle(self.deck)

    def draw_card(self):
        try:
            return self.deck.pop()
        except IndexError:
            return

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
        self.fake_generator = [[Board.best_cards_with_zero_placed_gen() for _ in range(NUM_OF_STONES)] for x in range(2)]
        # next(self.fake_generator[player][stone]) = next best fakes you can add to location [player][stone]
        
    def prettify_cards_on_board(self):
        L = []
        for k in range(NUM_OF_NUMS):
            for j in range(NUM_OF_COLORS):
                if self.cards_on_board[k*NUM_OF_COLORS + j] == True:
                    L.append((k+1,j+1))
        return L

    def real_len(self, player: int, stone: int) -> int:
        """returns num of real cards"""
        for i in range(len(self.cards[player][stone])):
            if type(self.cards[player][stone][i]) == int or self.cards[player][stone][i].fake == True:
                return i
        return len(self.cards[player][stone])
    
    def __repr__(self):
        output_as_list = []
        # print player 1
        for s in range(NUM_OF_STONES):
            if self.stones[s] == 1:
                output_as_list.append('===   ')
            else:
                output_as_list.append('      ')
        output_as_list.append('\n')
        for i in range(3):
            for stone in range(NUM_OF_STONES):
                curr_card = self.cards[0][stone][i]
                output_as_list.append(f'{curr_card.num}{curr_card.color}{"F" if curr_card.fake == True else "T"}   ')
            output_as_list.append('\n')
        # print stones
        output_as_list.append('@@@   '*9)
        output_as_list.append('\n')
        # print player 2
        for s in range(NUM_OF_STONES):
            if self.stones[s] == 2:
                output_as_list.append('===   ')
            else:
                output_as_list.append('      ')
        output_as_list.append('\n')
        for i in range(3):
            for stone in range(NUM_OF_STONES):
                curr_card = self.cards[1][stone][i]
                output_as_list.append(f'{curr_card.num}{curr_card.color}{"F" if curr_card.fake == True else "T"}   ')
            output_as_list.append('\n')
        return ''.join(output_as_list)
    
    @staticmethod
    def convert_to_cards_on_board_index(num: int, color: int):
        """Converts num, color to an appropriate index in the cards_on_board variable"""
        return (num-1)*NUM_OF_COLORS + color-1

    def draw_card(self):
        return self.deck.draw_card()
    
    def claim_stone(self,player: int, stone: int):
        """Does nothing when stone is claimed"""
        if self.stones[stone] != 0:
            return
        print(f"Player {player} is claiming stone {stone}!!!")
        self.stones[stone] = player

    def clear_fakes(self, player: int, stone: int):
        for i in range(len(self.cards[player][stone])):
            if type(self.cards[player][stone][i]) == Card and self.cards[player][stone][i].fake == True: 
                fakes = self.cards[player][stone][i:]
                for fake in fakes:
                    self.index_of_fakes[str(fake)[:2]].remove((player,stone))
                self.cards[player][stone] = self.cards[player][stone][:i] # real cards are always at the beginning
                return
            
    @staticmethod
    def best_card_with_two_placed_gen(cards: List[Tuple[int, int]]):
        num1, color1, num2, color2 = cards[0][0], cards[0][1], cards[1][0], cards[1][1]
        diff = abs(num1-num2)
        run = diff > 0 and diff <= 2
        
        def possible_runs_gen(num1: int, num2: int):
            m = max(num1, num2) + 1
            for x in range(m,min(num1,num2)-2,-1):
                if abs(num1-x) <= 2 and abs(num2-x) <= 2 and x > 0 and x <= NUM_OF_NUMS and num1 !=x and num2!=x:
                    yield x
            return

        if diff == 0:
            # try three of a kind
            possible_colors = filter(lambda x: x != color1 and x != color2,
                                      (c for c in range(1, NUM_OF_COLORS + 1)))
            for col in possible_colors:
                yield [(num1, col)]
        else:
            if color1 == color2: # is color\color run possible?
                # try color run
                if run:
                    possible_runs = possible_runs_gen(num1, num2)
                    for possible_run in possible_runs:
                        yield [(possible_run, color1)]
                # then try color 
                for num in filter(lambda x: x != num2 and x != num1, range(NUM_OF_NUMS,0,-1)):
                    yield [(num, color1)]
            # then run
            if run:
                possible_runs = possible_runs_gen(num1, num2)
                for possible_run in possible_runs:
                    for col in range(NUM_OF_COLORS, 0, -1):
                        yield [(possible_run, col)]
        # finally sum
        for n in range(NUM_OF_NUMS, 0, -1):
            for c in range(NUM_OF_COLORS, 0, -1):
                yield [(n,c)]
        return

    @staticmethod
    def best_cards_with_one_placed_gen(num: int, color: int):
        """logic for best card available when one is already in place
            yields duos of tuple(num: int, color: int) of a possible fake to add"""
        POSSIBLE_RUNS = filter(lambda nums: nums[0] <= NUM_OF_NUMS and nums[1] > 0,[(num+2, num+1), (num+1, num-1), (num-1, num-2)])
        # try color run
        for possible_run in POSSIBLE_RUNS:
            yield [(possible_run[0], color),(possible_run[1], color)]
        # try three of a kind 
        filter_color = lambda x: x != color
        for c in filter(filter_color, range(2, NUM_OF_COLORS + 1)):
            for cc in filter(filter_color, range(1,c)):
                yield [(num, c), (num, cc)]
        # generate best color combinations by order
        j,k = NUM_OF_NUMS,NUM_OF_NUMS - 1
        # MIGHT NOT WORK IF NUM_OF_NUMS IS EVEN 
        while True: 
            yield [(j, color), (k, color)]
            if j == 2 and k == 1:
                break
            if (j+k) % 2 == 1:
                if k == 1:
                    j -= 1
                elif j == NUM_OF_NUMS:
                    k -= 1
                else:
                    j += 1
                    k -= 1
            else:
                if j-k == 2:
                    j -= 1
                else:
                    j -= 1
                    k += 1
        # try run
        POSSIBLE_RUNS = filter(lambda nums: nums[0] <= NUM_OF_NUMS and nums[1] > 0,[(num+2, num+1), (num+1, num-1), (num-1, num-2)])
        for possible_run in POSSIBLE_RUNS:
            for c in range(1, NUM_OF_COLORS + 1):
                for cc in range(1, NUM_OF_COLORS + 1):
                    yield[(possible_run[0], c), (possible_run[1], cc)]
        # only sum available
        j,k = NUM_OF_NUMS, NUM_OF_NUMS
        while True: 
            for c in range(1, NUM_OF_COLORS + 1):
                for cc in range(1, NUM_OF_COLORS + 1):
                    if j != k or c != cc:
                        yield [(j, c), (k, cc)]
            if j == 1 and k == 1:
                break
            if (j+k) % 2 == 1:
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
        return

    @staticmethod
    def __color_combinations():
        """generates all color triplets"""
        for i in range(3, NUM_OF_COLORS+1):
            for j in range(2,i):
                for k in range(1,j):
                    yield(i,j,k)

    @staticmethod
    def __compute_max_sum(n,r,up_limit):
        q = n // r
        p = n % r
        return r*(q*up_limit - (q*(q-1))//2) + (p)*(up_limit-q)
    
    @staticmethod
    def __compute_min_sum(n,r,down_limit):
        q = n // r
        p = n % r
        return r*(down_limit*q+(q*(q-1))//2) + p*(down_limit+q)

    @staticmethod
    def __equal_sum_combinations(s: int,n: int,r: int,up_limit: int,low_limit: int):
        """generates, without repetitions, all combinations of n integers,
            all of which are between up_limit and low_limit (including), with at most r instances of the same number,
            that add up to sum"""
        if n == 0 or up_limit < low_limit:
            yield []
            return
        if n == 1:
            assert up_limit >= s and low_limit <= s
            yield [s]
            return
        assert up_limit > 0 and low_limit > 0 and up_limit >= low_limit
        min_min_int = max(s - Board.__compute_max_sum(n-1,r,up_limit),low_limit)
        max_min_int = max(up_limit - (n//r) + 1, low_limit)
        q = n // r
        p = n % r
        assert (p==1 or up_limit-q+1>=low_limit) and (p==0 or up_limit-q>=low_limit) # assert that there is enough numbers
        for rep in range(1, min(r + 1,n + 1)):
            for num in range(min_min_int, max_min_int+1):
                if Board.__compute_min_sum(n-rep,r,num+1) + num*rep <= s\
                and Board.__compute_max_sum(n-rep,r,up_limit) + num*rep >= s:
                    for combination in Board.__equal_sum_combinations(s-(num*rep),n-rep,r,up_limit,num+1):
                        yield [num for _ in range(rep)] + combination
        return

    @staticmethod
    def best_cards_with_zero_placed_gen():
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
        for s in range(3*NUM_OF_NUMS-3, 5, -1):  # assumes num_of_nums >= 3
            for nums in Board.__equal_sum_combinations(s,3,1,NUM_OF_NUMS,1):
                for c in range(1, NUM_OF_COLORS + 1):
                    yield [(num,c) for num in nums]
        POSSIBLE_RUNS = ((n,n+1,n+2) for n in range(NUM_OF_NUMS-2,0,-1))
        # best runs
        for possible_run in POSSIBLE_RUNS:
            for sc in range(3*NUM_OF_COLORS-1, 3, -1):
                for colors in Board.__equal_sum_combinations(sc,3,2,NUM_OF_COLORS,1):
                    for unique_perms in set(itertools.permutations(colors,3)):
                        yield [(run[0],run[1]) for run in zip(possible_run,unique_perms)]
        # best sums
        for s in range(3*NUM_OF_NUMS-1, 3, -1):  # assumes num_of_nums >= 3
            for nums in Board.__equal_sum_combinations(s,3,2,NUM_OF_NUMS,1):
                for sc in range(3*NUM_OF_COLORS-1, 3, -1):
                    for colors in Board.__equal_sum_combinations(sc,3,2,NUM_OF_COLORS,1):
                        for unique_perms in set(itertools.permutations(colors,3)):
                            yield [(comb[0],comb[1]) for comb in zip(nums,unique_perms)]
        return                

    def update_gen(self, player: int, stone: int):
        """Called when a new card is placed on the board
            Updated fake generator accordingly"""
        r_len = self.real_len(player,stone)
        if r_len == 1:
            card = (self.cards[player][stone][0].num, self.cards[player][stone][0].color)
            self.fake_generator[player][stone] = Board.best_cards_with_one_placed_gen(card[0],card[1])
        elif r_len == 2:
            cards = [(self.cards[player][stone][0].num, self.cards[player][stone][0].color),
                     (self.cards[player][stone][1].num, self.cards[player][stone][1].color)]
            self.fake_generator[player][stone] = Board.best_card_with_two_placed_gen(cards)
        else:
            self.fake_generator[player][stone] = None
    
    def update_fakes(self, card: Card, source_player: int, source_stone: int):
        """deletes all fake occurrences of card
            calls get_best_hand to replace a new possible best hand
            (source_player, source_stone): data of where a new card was place"""
        self.update_gen(source_player, source_stone)
        
        def helper_gen():
            """Used to ensure (source_player, source_stone) is attended"""
            try:
                for pair in self.index_of_fakes["{num}{color}".format(num = card.num, color = card.color)]:
                    player, stone = pair[0], pair[1]
                    if player != source_player or stone != source_stone:
                        yield (player, stone)
            except KeyError:
                # card was not on board as a fake
                print('')
            yield (source_player, source_stone)
            return
        
        g = list(helper_gen())
             
        for pair in g:  
            player, stone = pair[0], pair[1]  
            self.clear_fakes(player, stone)
            if self.real_len(player,stone) < 3:  # if 3 cards are put in front of a stone, no fakes are needed
                # get next valid fakes
                while True:
                    new_fakes = next(self.fake_generator[player][stone])
                    is_valid = True
                    for fake in new_fakes:
                        if fake[0] < 1 or fake[1] < 1 or fake[0] > NUM_OF_NUMS or fake[1] > NUM_OF_COLORS:
                            print('Huh?')
                        if self.cards_on_board[Board.convert_to_cards_on_board_index(fake[0],fake[1])]:
                            is_valid = False
                    if is_valid:
                        break
                # add fakes       
                self.cards[player][stone].extend(map(lambda pair: Card(pair[0], pair[1], True), new_fakes))
                for fake_suggestion in new_fakes:
                    try:
                        self.index_of_fakes["{num}{color}".format(num=fake_suggestion[0],color=fake_suggestion[1])].append((player,stone))
                    except KeyError:
                        self.index_of_fakes["{num}{color}".format(num=fake_suggestion[0],color=fake_suggestion[1])] = [(player, stone)]
        try:
            self.index_of_fakes.pop("{num}{color}".format(num = card.num, color = card.color))
        except KeyError:
            # card was not on board as a fake
            pass
                    

    def place_card(self,stone: int, card: Card, player: int):
        print(f"Player {player+1} is placing card {card.num}{card.color} in front of stone {stone}!")
        self.cards[player][stone].insert(0, card)
        self.cards_on_board[Board.convert_to_cards_on_board_index(card.num, card.color)] = True
        self.update_fakes(card, player, stone)
        
        if (self.real_len(player,stone) == 3 and self.real_len(1-player,stone) < 3):
            print(f"Player {player+1} has put 3 cards in front of stone {stone}!", '  '.join([str(c) for c in self.cards[player][stone]]))
            self.cards[player][stone].append(1)

class Player(ABC):
    def __init__(self):
        self.p = -1 # valid p in [1,2]

    def assign_player(self,p):
        """The player gets if he is player 1 or player 2.
            used in prints"""
        self.p = p
    
    @abstractmethod
    def choose_stone_and_card(self, state: List[List[List[Union[Card,int]]]], hand: List[Card], claimed: List[int]) -> Tuple[int, int]:
        """Gets the state of the board, the state of the stones and his hand.
        Return (index of chosen card in hand, index of chosen stone)
        In the case you have nowhere to place a card, return (0,0)"""
        pass
        

class Game():
    def __init__(self,p1: Type[Player], p2: Type[Player], cards_in_hand = 6):
        self.board = Board()
        self.players = [p1, p2]
        p1.assign_player(1)
        p2.assign_player(2)
        self.hands = [[self.board.draw_card() for i in range(cards_in_hand)] for _ in range(2)]  # [hand of player 1, hand of player 2]
        self.game_over = False

    def play(self):
        while not self.game_over:
            print(f'Player 1, make your move: ')
            self.make_move(0)
            if self.game_over:
                return
            print(f'Player 2, make your move: ')
            self.make_move(1)

    def get_strength(self, cards: List[Union[Card,int]]) -> int:
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


    def claim_stone(self, player: int):
        for stone in range(0,NUM_OF_STONES):
            there_is_a_fake = False
            for card in range(3):
                if self.board.cards[player][stone][card].fake == True:
                    there_is_a_fake = True
            if there_is_a_fake:
                continue
            if self.get_strength(self.board.cards[player][stone]) > self.get_strength(self.board.cards[1-player][stone]):
                self.board.claim_stone(player+1,stone)  # +1 because of how claims are stored in self.stones

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
        if neighboring_stones_count == 3 and neighboring_stones_player != 0:
            self.game_over = True
            print(f"Player {neighboring_stones_player} wins.")
            return
        if count[1] == 5:
            self.game_over = True
            print("Player 1 wins.")
            return
        if count[2] == 5:
            self.game_over = True
            print("Player 2 wins.")
            return
        


    def make_move(self, player: int):
        self.claim_stone(player)
        self.is_game_over()
        if self.game_over:
            return
        card, stone = self.players[player].choose_stone_and_card([self.board.cards[player].copy(),self.board.cards[1-player].copy()], self.hands[player].copy(),self.board.stones.copy())
        if card == 0 and stone == 0:
            return
        self.board.place_card(stone, self.hands[player].pop(card), player)
        self.hands[player].append(self.board.draw_card())
        



    