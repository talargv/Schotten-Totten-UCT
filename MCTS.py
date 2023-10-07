from typing import List, Self, Union, Tuple, Type
from abc import ABC, abstractmethod
from numpy import log
from itertools import product
import random

from schotten_again import Board, Card, Player, Hand

class MonteCarloNode():
    def __init__(self, parent: Union[Type[Self], None]):
        self.parent = parent
        self.children = [] # Type: List[Self]
        self.value = 0
        self.exploit = 0
    
    def update(self):
        self.exploit = sum([child.exploit for child in self.children])
        self.value = sum([child.value*child.exploit for child in self.children]) / self.exploit
        
class DecisionNode(MonteCarloNode):
    def __init__(self, parent: Union[Type[Self], None], leading_action: str):
        """leading action is in the form of {card num}{card color}{stone}\n
        representing the action that lead to This node."""
        super().__init__(parent)
        self.leading_action = leading_action
        self.seen_children = {} # Format: {index of card chosen from hand}{index of stone chosen from hand}:Node
        
class MixedNode(MonteCarloNode):
    def __init__(self, parent: Union[Type[Self], None], leading_action: str):
        """leading action is in the form of {index of card chosen from hand}{index of stone chosen from hand}\n
        representing the action that lead to This node."""
        super().__init__(parent)
        self.leading_action = leading_action
        self.seen_children = {} # Format: {card num}{card color}{stone}:Node 
        
        
    def choose_action(self, board: Board, player: int, c: int=3):
        available_stones = [stone for stone in range(len(board.stones)) if board.stones[stone] == 0 and len(board.cards[player][stone]) < 3] 
        possible_actions = list(product(board.deck, available_stones))
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
        return random.choices(possible_actions, weights=distribution)

class MonteCarloTSPlayer():
    """Implemented decisions:
    - nodes are chance nodes. when traversing the tree the state of the game is stochastically updated.
    - simulations of the opponent's moves are skewed towards not-awful choices.
    - returned node is the 'best child'."""
    # NOTE: when simulating a game to termination the opponent has unfair advantage. 
    #       possible solution (if it becomes a problem) is to use the 'Hand Strength' heuristic
    #       or use opponent\chance nodes instead of mixed nodes.
    def __init__(self, board: Board, cards_in_hand: List[Card], player: int):
        self.board = board
        self.cards_in_hand = cards_in_hand
        self.p = player
    
    @staticmethod
    def simulate_turn(board: Board, player: int, possible_cards: List[Card], c: int=3) -> Tuple[Card, int]:
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
        return random.choices(possible_actions, weights=distribution)
        
    def simulate_others_turn(self, board: Board, c:int =2):
        MonteCarloTSPlayer.simulate_turn(board, 1-self.p, c)

    # TODO: CLAIM STONES
    def tree_policy(self, root: Type[MonteCarloNode]) -> Tuple[Type[MonteCarloNode], Board, List[Card]]:
        """Because the nodes contain information only about leading_action, TreePolicy 
        needs to return an updated board in accordance with the tree path"""
        board = self.board.copy()
        cards_in_hand = [Card(c.num, c.color) for c in self.cards_in_hand]
        while board.is_board_terminal() == 0:
            if type(root) == MixedNode:
                card, stone = root.choose_action(board, 1-self.p)
                action = f"{card.num}{card.color}{stone}"
                if not action in root.seen_children:
                    node = DecisionNode(root, action)
                    root.children.append(node)
                    root.seen_children[action] = node
                else:
                    node = root.seen_children[action]
                root = node
                board.place_card(stone, card, 1-self.p)
                board.deck.remove(card)
                board.claim_stone(1-self.p, stone)
            else:
                available_stones = [stone for stone in range(len(board.stones)) if board.stones[stone] == 0 and len(board.cards[self.p][stone]) < 3]
                if len(root.children) == len(available_stones) * len(cards_in_hand):
                    root = self.best_child(root)
                    
                    # Update state
                    card_index, stone = root.leading_action[0], root.leading_action[1]
                    board.place_card(stone, cards_in_hand[card_index], self.p)
                    cards_in_hand.pop(card_index)
                    cards_in_hand.append(board.draw_card())
                    for s in range(9):
                        board.claim_stone(self.p, s)
                    
                else:
                    # Expand:
                    #   Find unexplored action
                    for stone in available_stones:
                        for card_index in range(len(cards_in_hand)):
                            action = f"{card_index}{stone}"
                            if not action in root.seen_children:
                                #   Create node
                                new_node = MixedNode(root, action)
                                root.seen_children[action] = new_node
                                root.children.append(new_node)
                                
                                # Update state
                                board.place_card(stone, cards_in_hand[card_index], self.p)
                                cards_in_hand.pop(card_index)
                                cards_in_hand.append(board.draw_card())
                                for s in range(9):
                                    board.claim_stone(self.p, stone)
                                return new_node, board, cards_in_hand
        return root, board, cards_in_hand
    
    def best_child(self, node: MonteCarloNode, c = 1) -> MonteCarloNode:
        argmax = node.children[0]
        for child in node.children:
            val_max = argmax.value / argmax.exploit + c*(((2*log(node.exploit))/argmax.exploit)**0.5)
            val_curr = val_max = child.value / child.exploit + c*(((2*log(node.exploit))/child.exploit)**0.5)
            if val_curr > val_max:
                argmax = child
        return argmax
    
    def default_policy(self, board: Board, cards_in_hand: List[Card], node: Type[MonteCarloNode]) -> int:
        """return reward"""
        def simulate_turn(board: Board, cards_in_hand: List[Card], is_decision_maker: bool):
            if not is_decision_maker:
                card, stone = MonteCarloTSPlayer.simulate_turn(board, 1-self.p, board.deck)
                if card:
                    board.deck.remove(card)
                    board.place_card(stone, card, 1-self.p)
                    for s in range(9):
                        board.claim_stone(1-self.p, s)
            else:
                card, stone = MonteCarloTSPlayer.simulate_turn(board, self.p, cards_in_hand)
                if card:
                    cards_in_hand.remove(card)
                    cards_in_hand.append(board.draw_card())
                    board.place_card(stone, card, self.p)
                    for s in range(9):
                        board.claim_stone(self.p, s)

        if type(node) == MixedNode:
            is_decision_maker = False
        else:
            is_decision_maker = True
            
        while True:
            if board.is_board_terminal() != 0:
                return 0 if is_decision_maker else 1
            simulate_turn(board, cards_in_hand, is_decision_maker)
            if board.is_board_terminal() != 0:
                return 1 if is_decision_maker else 0
            simulate_turn(board, cards_in_hand, not is_decision_maker)
            
    
    def backup(self, node: Type[MonteCarloNode], reward: int):
        while node:
            node.exploit += 1
            node.value += reward
            node = node.parent
    
    def UCT(self, max_iter: int):
        root = DecisionNode(None,"")
        iter = 0
        while iter < max_iter:
            curr_node, curr_board, curr_hand = self.tree_policy(root)
            reward = self.default_policy(curr_board, curr_hand, curr_node)
            self.backup(curr_node, reward)
            iter += 1
        return self.best_child(root)

class MCTSAgent(Player):
    