import random
import re
from typing import List, Union, Tuple
from schotten_again import Player,Card,Hand,Board


NUM_OF_COLORS = 6
NUM_OF_NUMS = 9
NUM_OF_STONES = 9

class Tools():
    @staticmethod
    def gen_cards() -> Card:
        """generate all possible cards"""
        for i in range(NUM_OF_NUMS):
            for j in range(NUM_OF_COLORS):
                yield Card(i,j)
        return
    
    @staticmethod
    def gen_n_cards(n) -> List[Card]:
        """generate all possible lists of unique n cards"""
        if n == 0:
            yield []
            return
        g = Tools.gen_cards()
        for card in g:
            g_nm1 = Tools.gen_n_cards(n-1)
            for card_list in g_nm1:
                if card in card_list:
                    continue
                card_list.append(card)
                yield card_list
        return
    
    @staticmethod
    def gen_n_available_cards(n, available_cards: List[List[int]]) -> List[Card]:
        """generate all possible lists of unique n cards with respect to available cards"""
        for cards in Tools.gen_n_cards(n):
            to_yield = True
            for card in cards:
                if available_cards[card.num][card.color]:
                    to_yield = False
            if to_yield:
                yield cards
        return
            
                
    
# NOTE: computation might be problematic
# because it doesn't account for uses of the same card for different players
class HandStrengthEstimate(Player):
    def update_board(self, board: Board):
        self.board = board
        
    @staticmethod
    def get_strengths_count(hand: Hand, available_cards, accumulate=False) -> List[int]:
        """counts num of different possible combinations with same strength"""
        L = [0 for _ in range(72)]
        g = Tools.gen_n_available_cards(3-len(hand), available_cards)
        for cards in g:
            tmp_hand = Hand(cards)
            H = hand.copy()   
            H.extend(tmp_hand)
            L[Hand.strength_from_list(H)] += 1
        if accumulate:
            count = 0 
            for i in range(len(L)):
                tmp = L[i]
                L[i] += count
                count += tmp
        return L
            
    def estimate_strength(self, player, stone, cards_in_hand: List[Card], C=3/4) -> float:
        """Estimated Strength = HandFactor * (1+C*NeighborFactor) \n
        HandFactor = (wins + ties*(len on player's side / sum on both sides))/total \n
        C - A hyperparameter\n
        NeighborFactor - claimed neighbors/4 + other's claimed neighbors/4 \n
        4 is max number of neighbors"""
        
        hand1 = self.board.cards_on_board[player][stone]
        hand2 = self.board.cards_on_board[1-player][stone]
        available_cards = self.board.cards_on_board
        advantage = self.board.advantage[stone] == player+1
        
        
        hand2_possible_strength_count = HandStrengthEstimate.get_strengths_count(hand2, available_cards, accumulate=True)
        possible_hands_gen = Tools.gen_n_available_cards(3-len(hand1), available_cards)
        wins, ties, losses, total = 0, 0, 0, 0
        for cards in possible_hands_gen:
            # check if in hand 
            in_hand = False
            for c1 in cards:
                for c2 in cards_in_hand:
                    if c1 == c2:
                        in_hand = True
            if in_hand:
                continue
            # end check
            
            curr_hand_strength = Hand.strength_from_list(hand1.tolist(copy=False)+cards)
            curr_wins = hand2_possible_strength_count[curr_hand_strength-1]
            curr_ties = hand2_possible_strength_count[curr_hand_strength] - curr_wins
            wins += curr_wins
            ties += curr_ties
            losses += hand2_possible_strength_count[-1] - curr_ties - curr_wins
            total += hand2_possible_strength_count[-1]
        if len(hand1) == 3 and advantage:
            wins += ties
            ties = 0
        if len(hand2) == 3 and len(hand1) < 3:
            losses += ties
            ties = 0
        hand_factor = (wins + ties*(len(hand1)/(len(hand1)+len(hand2)))) / total
        claimed_neighbors = 0
        if stone + 1 < len(self.board.stones) and self.board.stones[stone+1] == player+1:
            claimed_neighbors += 1
            if stone + 2 < len(self.board.stones) and self.board.stones[stone+2] == player+1:
                claimed_neighbors += 1
        if stone - 1 >= 0 and self.board.stones[stone-1] == player+1:
            claimed_neighbors += 1
            if stone - 2 >= 0 and self.board.stones[stone-2] == player+1:
                claimed_neighbors += 1
                
        others_claimed_neighbors = 0
        if stone + 1 < len(self.board.stones) and self.board.stones[stone+1] == 2-player:
            others_claimed_neighbors += 1
            if stone + 2 < len(self.board.stones) and self.board.stones[stone+2] == 2-player:
                others_claimed_neighbors += 1
        if stone - 1 >= 0 and self.board.stones[stone-1] == 2-player:
            others_claimed_neighbors += 1
            if stone - 2 >= 0 and self.board.stones[stone-2] == 2-player:
                others_claimed_neighbors += 1
        
        return hand_factor * (1+(C/4)*(others_claimed_neighbors+claimed_neighbors))
        
    def choose_stone_and_card(self, cards_in_hand: List[Card], board: Board) -> Tuple[int,int]:
        self.update_board(board)
        available_stones = [i for i in range(NUM_OF_STONES) if len(self.board.cards[self.p][i]) < 3]
        if len(available_stones) == 0:
            return 0,0
        argmax_card = 0
        argmax_stone, max_strength = 0, -1
        for card_index in range(len(cards_in_hand)):
            card = cards_in_hand[card_index]
            for stone in available_stones:
                self.board.place_card(stone, card, self.p)
                curr_strength = self.estimate_strength(self.p, stone, cards_in_hand)
                if curr_strength > max_strength:
                    max_strength = curr_strength
                    argmax_stone = stone
                    argmax_card = card_index
                self.board.pop_from_stone(self.p, stone)
        return argmax_card, argmax_stone
        
    def claim(self,board: Board):
        self.update_board(board)
        return [i for i in range(NUM_OF_STONES)]
            
        
        