from schotten_again import Card, Hand, Deck, Board, Game
import unittest
from collections import Counter

COLORS = {1:"Purple", 2:"Brown", 3:"Red", 4:"Yellow", 5:"Green", 6:"Blue"}
NUM_OF_COLORS = 6
NUM_OF_NUMS = 9
NUM_OF_STONES = 9
CARDS_IN_HAND = 6

class test_card(unittest.TestCase):
    @unittest.expectedFailure
    def test_card_init(self):
        card1 = Card(10, 6)
        card2 = Card(1, 0)
        card3 = Card("P", 0)
        card4 = Card(3, "p")
        
    def test_to_str(self):
        for num in range(NUM_OF_NUMS):
            for color in range(NUM_OF_COLORS):
                self.assertEqual(str(Card(num,color)), f"{num}{COLORS[color][:2]}")
                
    def test_eq(self):
        self.assertEqual(Card(1,1),Card(1,1))
        self.assertNotEqual(Card(1,1),Card(9,6))
        self.assertNotEqual(Card(6,7),Card(6,8))
        
class test_hand(unittest.TestCase):
    def test_init(self):
        hand1 = Hand()
        self.assertEqual(hand1.hand, [])
        hand2 = Hand([Card(5,1), Card(1,1)])
        self.assertEqual(hand2.hand, [Card(5,1), Card(1,1)])
    
    @unittest.expectedFailure
    def test_illegal_hands_init(self):
        hand = Hand([Card(1,1),Card(1,2),Card(2,5),Card(6,6)])
        
    def test_len(self):
        self.assertEqual(len(Hand([Card(1,1)])), 1)
        
    def test_append(self):
        hand = Hand()
        hand.append(Card(9,1))
        self.assertEqual(hand.hand, [Card(9,1)])
        
    @unittest.expectedFailure
    def test_illegal_append(self):
        hand = Hand()
        hand.append([])
        
    @unittest.expectedFailure
    def test_illegal_append_full(self):
        hand = Hand([Card(1,1),Card(1,2),Card(2,5)])
        hand.append(Card(1,1))
        
    def test_extend(self):
        hand = Hand()
        tmp = Hand([Card(1,1),Card(1,2)])
        hand.extend(Hand())
        self.assertEqual(hand.hand, [])
        hand.extend(tmp)
        self.assertEqual(hand.hand, [Card(1,1),Card(1,2)])
        hand.hand[1] = Card(9,6)
        self.assertEqual(tmp.hand, [Card(1,1),Card(1,2)])
        hand.append(Card(1,1))
        self.assertEqual(hand.hand, [Card(1,1),Card(9,6),Card(1,1)])
        hand = Hand()
        hand.extend([Card(9,1),Card(9,6)])
        self.assertEqual(hand.hand, [Card(9,1),Card(9,6)])
        
    @unittest.expectedFailure
    def test_illegal_extend(self):
        hand = Hand([Card(1,1),Card(1,2)])
        hand.extend([Card(9,1),Card(8,6)])
        
    def test_pop(self):
        hand = Hand()
        hand.pop()
        hand.append(Card(1,1))
        hand.pop()
        self.assertEqual(hand.hand, [])
        hand.extend([Card(1,1), Card(8,4)])
        hand.pop(0)
        self.assertEqual(hand.hand, [Card(8,4)])
        
    def test_get_item(self):
        hand = Hand([Card(1,1), Card(8,4)])
        self.assertEqual(hand[1],Card(8,4))
        
    def test_strength(self):
        # sum
        hand1 = Hand([Card(1,1), Card(8,4), Card(6,5)])
        self.assertEqual(hand1.hand_strength, Hand.strength_from_list(hand1.hand))
        self.assertEqual(hand1.hand_strength, 1+8+6)
        # run
        hand2 = Hand([Card(3,3),Card(5,3),Card(4,1)])
        hand3 = Hand([Card(3,3),Card(4,1),Card(5,3)])
        hand4 = Hand([Card(4,1),Card(3,3),Card(5,3)])
        self.assertEqual(hand2.hand_strength(),hand3.hand_strength())
        self.assertEqual(hand3.hand_strength(),hand4.hand_strength())
        self.assertEqual(hand2.hand_strength(),26+3)
        # color
        hand5 = Hand([Card(1,1),Card(4,1),Card(5,1)])
        hand6 = Hand([Card(4,1),Card(1,1),Card(5,1)])
        hand7 = Hand([Card(1,6),Card(5,6),Card(4,6)])
        self.assertEqual(hand5.hand_strength(),hand6.hand_strength())
        self.assertEqual(hand6.hand_strength(),hand7.hand_strength())
        self.assertEqual(hand5.hand_strength(),33+1+5+4)
        # three of a kind
        hand8 = Hand([Card(7,5),Card(7,4),Card(7,2)])
        hand9 = Hand([Card(1,2),Card(1,4),Card(1,5)])
        self.assertEqual(hand8.hand_strength(), 56+7)
        self.assertEqual(hand9.hand_strength(),56+1)
        # color run
        hand10 = Hand([Card(3,1),Card(1,1),Card(2,1)])
        hand11 = Hand([Card(8,6),Card(7,6),Card(9,6)])
        self.assertEqual(hand10.hand_strength(),65+1)
        self.assertEqual(hand11.hand_strength(),65+7)
        
    def test_copy(self):
        hand = Hand([Card(1,1),Card(4,1),Card(5,1)])
        tmp = hand.copy()
        tmp.pop()
        self.assertEqual(hand.hand,[Card(1,1),Card(4,1),Card(5,1)])
        self.assertEqual(len(tmp),2)
        hand = Hand()
        hand.copy()
        
    def test_iter(self):
        L = [Card(1,1),Card(4,1),Card(5,1)]
        hand = Hand([Card(1,1),Card(4,1),Card(5,1)])
        for i, card in enumerate(hand):
            self.assertEqual(L[i], card)
    
    def test_to_list(self):
        hand = Hand([Card(1,1),Card(4,1),Card(5,1)])
        L1 = hand.tolist(copy=False)
        L1[0] = Card(2,2)
        self.assertEqual(hand[0], Card(2,2))
        hand = Hand([Card(1,1),Card(4,1),Card(5,1)])
        L2 = hand.tolist()
        L2[0] = Card(2,2)
        self.assertEqual(hand[0], Card(1,1))
        
    def test_hand_not_on_board(self):
        available_cards = [[False for _ in range(NUM_OF_COLORS)] for j in range(NUM_OF_NUMS)]
        hand = Hand([Card(1,1),Card(4,1),Card(5,1)])
        self.assertTrue(hand.hand_not_on_board(available_cards))
        available_cards[8][5] = True
        self.assertTrue(hand.hand_not_on_board(available_cards))
        available_cards[3][0] = True
        self.assertFalse(hand.hand_not_on_board(available_cards))
        
class test_deck(unittest.TestCase):
    @unittest.expectedFailure
    def test_illegal_init(self):
        Deck([1])
        
    def test_init(self):
        deck = Deck()
        deck_counter = Counter(deck.deck)
        self.assertEqual(len(list(deck_counter.keys())), 54)
        self.assertEqual(len(deck.deck), 54)
        deck = Deck([Card(i+1,j+1) for i in range(9) for j in range(6)])
        self.assertEqual(deck[0], Card(1,1))
        
    def test_copy(self):
        deck = Deck()
        deck_copy = deck.copy()
        self.assertListEqual(deck_copy.deck, deck.deck)
        card = deck.deck[0]
        deck_copy.deck[0] = deck_copy.deck[1]
        self.assertEqual(deck.deck[0], card)
        
    def test_draw_card(self):
        deck = Deck([Card(1,1), Card(2,2)])
        card = deck.draw_card()
        deck.draw_card()
        self.assertEqual([], deck.deck)
        self.assertEqual(card, Card(2,2))
        
class test_board(unittest.TestCase):
    def test_init(self):
        board = Board()
        for i in range(54):
            self.assertEqual(type(board.deck[i]), Card)
        for i in range(NUM_OF_STONES):
            self.assertEqual(board.stones[i], 0)
            self.assertEqual(board.advantage[i], 0)
        for i in range(2):
            for j in range(NUM_OF_STONES):
                self.assertEqual(len(board.cards[i][j]), 0)
                self.assertTrue(type(board.cards[i][j]) == Hand)
        for i in range(NUM_OF_NUMS):
            for j in range(NUM_OF_COLORS):
                self.assertFalse(board.cards_on_board[i][j])
                
    def test_str(self):
        state = """===   ===   ===   ===   ===   ===   ===   ===   ===   \n\n
        
        """
        
    
        
        
        