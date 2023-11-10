from schotten_again import Player, Card, Board, Game, Hand, NUM_OF_STONES, CARDS_IN_HAND

from abc import ABC, abstractmethod
from itertools import product
from numpy import log
from typing import List, Tuple

import random

class QuiteAwfulPlayer(Player):
    def __init__(self, c=3):
        self.c = c
    
    def claim(self, board: Board):
        return list(range(NUM_OF_STONES))
    
    def choose_stone_and_card(self, cards_in_hand: List[Card], board: Board, **kwargs) -> Tuple[int, int]:
        available_stones = board.available_stones(0)
        if len(available_stones) == 0 or len(cards_in_hand) == 0:
            #print('No moves available')
            return -1,-1
        
        card, stone = simulate_turn(board, 0, cards_in_hand, c=self.c)
        return cards_in_hand.index(card), stone

class UCTNode(ABC):
    def __init__(self, parent, leading_action: str, action_type: int):
        """An abstract class for decision/chance/opponent nodes."""
        self.parent = parent # Type: extends UCTNode
        self.total_reward = 0
        self.number_of_visits = 0
        self.leading_action = leading_action
        # leading action encodes the change in state the parent node has caused to the game
        if not (type(action_type) == int and action_type < 3 and action_type >= 0):
            raise ValueError("action_type must be in {0,1,2}")
        self.action_type = action_type
        # action type encodes what type of change the leading action has caused.
        # action_type == 0 if action is Opponent placing a card on the board
        # appropriate leading action format for the children is {card num}{card color}{stone index}
        # action_type == 1 if action is Player placing a card on the board
        # appropriate leading action format for the children is {card index in hand}{stone index} 
        # action type == 2 if action is Player drawing a card
        # appropriate leading action format for the children is {card num}{card color}
        self.children = []
        
    def tree_policy(self, board: Board, cards_in_hand: List[Card]):
        """Receives current state, and returns a child node for continuous propagation.
        does not change inputs, but creates new nodes if necessary.
        assumes board is not terminal"""
        pass
        
    def UCB(self,c=1):
        argmax = self.children[0]
        for child in self.children:
            val_max = argmax.total_reward / argmax.number_of_visits + 2*c*((log(self.number_of_visits)/argmax.number_of_visits)**0.5)
            val_curr = child.total_reward / child.number_of_visits + 2*c*((log(self.number_of_visits)/child.number_of_visits)**0.5)
            if val_curr > val_max:
                argmax = child
                val_max = val_curr
        return argmax
    
class DecisionNode(UCTNode):
    def __init__(self, parent, leading_action: str, *args):
        super().__init__(parent, leading_action, 1)
          
    def generate_child(self, leading_action: str):
        child = ChanceNode(self, leading_action)
        self.children.append(child)
        return child
          
    def tree_policy(self, board: Board, cards_in_hand: List[Card]):
        assert board.is_board_terminal() == 0
        
        available_stones = board.available_stones(player=0)
        
        if len(cards_in_hand) == 0 or len(available_stones) == 0:
            if len(self.children) == 1:
                return self.children[0]
            return self.generate_child('')
        
        if len(self.children) == len(available_stones)*len(cards_in_hand):
            return self.UCB()
        else:
            """actions_tree = [[False for _ in range(len(available_stones))] for j in range(len(cards_in_hand))]
            for child in self.children:
                actions_tree[int(child.leading_action[0])][int(child.leading_action[1])] = True
            available_action = [f'{i}{j}' for i in range(len(actions_tree)) for j in range(len(actions_tree[0])) if actions_tree[i][j]==False]
            chosen_action = random.choice(available_action)
            return self.generate_child(chosen_action)"""
            actions_table = set()
            for child in self.children:
                actions_table.add(child.leading_action)
            available_actions = [f'{card_index}{stone}' for card_index in range(len(cards_in_hand)) for stone in available_stones if not f'{card_index}{stone}' in actions_table]
            chosen_action = random.choice(available_actions)
            return self.generate_child(chosen_action)
            
                
class ChanceNode(UCTNode):
    def __init__(self, parent, leading_action: str, *args):
        super().__init__(parent, leading_action, 2)
          
    def generate_child(self, leading_action: str):
        child = OpponentNode(self, leading_action)
        self.children.append(child)
        return child    

    def tree_policy(self, board: Board, cards_in_hand: List[Card]):
        assert board.is_board_terminal() == 0
        
        available_stones = board.available_stones(player=0)
        
        if len(board.deck) <= 6 or len(cards_in_hand) == 0 or len(available_stones) == 0:
            if len(self.children) == 1:
                return self.children[0]
            return self.generate_child('')
        
        chosen_card = random.randint(0, len(board.deck)-1)
        chosen_action = f'{board.deck[chosen_card].num}{board.deck[chosen_card].color}'
        for child in self.children:
            if child.leading_action == chosen_action:
                return child
        return self.generate_child(chosen_action)

def simulate_turn(board: Board, player: int, possible_cards: List[Card], c: float=5) -> Tuple[Card, int]:
    available_stones = [stone for stone in range(len(board.stones)) if board.stones[stone] == 0 and len(board.cards[player][stone]) < 3] 
    possible_actions = list(product(possible_cards, available_stones))
    distribution = [1 for _ in range(len(possible_actions))]
    for i in range(len(possible_actions)):
        stone = possible_actions[i][1]
        card = possible_actions[i][0]
        hand = board.cards[player][stone]
        if len(hand) == 0:
            distribution[i] *= c
        elif len(hand) == 1:
            if abs(hand[0].num - card.num) < 3 or hand[0].color == card.color:
                distribution[i] *= c
        else: 
            if Hand.strength_from_list([card] + hand.hand) > 26: # better than sum
                distribution[i] *= c
    return random.choices(possible_actions, weights=distribution)[0]

class OpponentNode(UCTNode):
    def __init__(self, parent, leading_action: str, *args):
        super().__init__(parent, leading_action, 0)
          
    def generate_child(self, leading_action: str):
        child = DecisionNode(self, leading_action)
        self.children.append(child)
        return child    
    
    def tree_policy(self, board: Board, cards_in_hand: List[Card]):
        assert board.is_board_terminal() == 0
        
        available_stones = board.available_stones(player=1)
        
        if len(board.deck) == 0 or len(available_stones) == 0:
            if len(self.children) == 1:
                return self.children[0]
            return self.generate_child('')
        
        chosen_card, chosen_stone = simulate_turn(board=board, player=1, possible_cards=board.deck)
        action = f'{chosen_card.num}{chosen_card.color}{chosen_stone}'
        for child in self.children:
            if child.leading_action == action:
                return child
        return self.generate_child(action)
        
class UCT():
    def __init__(self, board: Board, cards_in_hand: List[Card]):
        self.board = board
        self.cards_in_hand = cards_in_hand
        
    def update_state_from_action(self, board: Board, cards_in_hand: List[Card], action: str, action_type: int):
        """See UCTNode constructor for more information"""
        if action == '':
            return
        if action_type == 0:
            board.deck.deck.remove(Card(int(action[0]),int(action[1])))
            board.place_card(int(action[2]), Card(int(action[0]),int(action[1])), 1)
        elif action_type == 1:
            board.place_card(int(action[1]), cards_in_hand.pop(int(action[0])), 0)
        else:
            board.deck.deck.remove(Card(int(action[0]),int(action[1])))
            cards_in_hand.append(Card(int(action[0]),int(action[1])))
            
    def tree_search(self, root: DecisionNode):
        node = root
        board = self.board.copy()
        cards_in_hand = [Card(card.num,card.color) for card in self.cards_in_hand]
        
        while board.is_board_terminal() == 0:
            num_children_before = len(node.children) # Data to check if a new child was created
            node = node.tree_policy(board, cards_in_hand)
            try:
                self.update_state_from_action(board, cards_in_hand, node.leading_action, node.parent.action_type)
            except ValueError as e:
                print(board)
                print([str(card) for card in cards_in_hand])
                print(type(node.parent), node.parent.action_type, node.leading_action)
                for child in node.parent.children:
                    print(node.leading_action, end=' ')
                print('')
                raise e
            parent = node.parent
            if type(parent) == DecisionNode and len(parent.children) > num_children_before: # a new child was created
                return node, board, cards_in_hand
        return node, board, cards_in_hand
        
    def backup(self, node: UCTNode, reward: int):
        while node:
            node.number_of_visits += 1
            node.total_reward += reward
            node = node.parent
        
    def uct(self, max_iter=10000) -> Tuple[int, int]:
        root = DecisionNode(None,'')
        iter = 0
        while iter < max_iter:
            iter += 1
            #print(iter)
            node, board, cards_in_hand = self.tree_search(root) 
            random.shuffle(board.deck.deck)
            others_hand = [board.draw_card() for _ in range(min(CARDS_IN_HAND,len(board.deck)))]
            hands = [cards_in_hand,others_hand]
            # ASSERTION
            for card in hands[0]:
                assert not card is None
            for card in hands[1]:
                assert not card is None
            # END ASSERTION
            if type(node) != DecisionNode:
                hands = [others_hand, cards_in_hand]
                board = board.change_pov()
            simulation = Game(QuiteAwfulPlayer(), QuiteAwfulPlayer(), board=board, hands=hands)
            res = simulation.play(show=False)
            if type(node) == DecisionNode:
                res = 1-res
            self.backup(node, res)
        chosen_child = root.UCB()
        return int(chosen_child.leading_action[0]), int(chosen_child.leading_action[1])
            
    
class UCTPlayer(Player):
    def __init__(self, max_iter=10000):
        self.max_iter = max_iter
        
    def choose_stone_and_card(self, cards_in_hand: List[Card], board: Board, **kwargs) -> Tuple[int,int]:
        available_stones = [stone for stone in range(len(board.stones)) if board.stones[stone] == 0 and len(board.cards[0][stone]) < 3]
        if len(available_stones) == 0:
            #print('No stones available')
            return -1,-1
        return UCT(board, cards_in_hand).uct(max_iter=self.max_iter)
    
    def claim(self, board: Board) -> List[int]:
        return list(range(NUM_OF_STONES))