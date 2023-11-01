from schotten_again import Card, Hand, Deck, Board, Game
import unittest
from collections import Counter
from MCTS_v2 import simulate_turn

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
        print("1")
        
    def test_to_str(self):
        for num in range(1,NUM_OF_NUMS+1):
            for color in range(1,NUM_OF_COLORS+1):
                self.assertEqual(str(Card(num,color)), f"{num}{COLORS[color][:2]}")
                
    def test_eq(self):
        self.assertEqual(Card(1,1),Card(1,1))
        self.assertNotEqual(Card(1,1),Card(9,6))
        self.assertNotEqual(Card(6,1),Card(6,2))
        self.assertEqual(Card(3,4),(3,4))
        self.assertNotEqual(Card(3,4),(4,3))
        
class test_hand(unittest.TestCase):
    def test_init(self):
        hand1 = Hand()
        self.assertEqual(hand1.hand, [])
        hand2 = Hand([Card(5,1), Card(1,1)])
        self.assertEqual(hand2.hand, [Card(5,1), Card(1,1)])
    
    @unittest.expectedFailure
    def test_illegal_hands_init(self):
        hand = Hand([Card(1,1),Card(1,2),Card(2,5),Card(6,6)])
        print("2")
        
    def test_len(self):
        self.assertEqual(len(Hand([Card(1,1)])), 1)
        
    def test_append(self):
        hand = Hand()
        hand.append(Card(9,1))
        self.assertEqual(hand.hand, [Card(9,1)])
        
    @unittest.expectedFailure
    def test_illegal_append_full(self):
        hand = Hand([Card(1,1),Card(1,2),Card(2,5)])
        hand.append(Card(1,1))
        print("3")
        
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
        self.assertEqual(hand1.hand_strength(), Hand.strength_from_list(hand1.hand))
        self.assertEqual(hand1.hand_strength(), 1+8+6)
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
        def test_board(board: Board):
            for i in range(54):
                self.assertEqual(type(board.deck.deck[i]), Card)
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
                    
        board = Board()
        test_board(board)
        board = Board(**vars(board))
        test_board(board)
                
    def test_str(self):
        state = []
        state.append('===   '*4)
        state.append('      ')
        state.append('===   '*3)
        state.append('      ')
        state.append('\n\n')
        state.append('      ')
        state.append('9Pu   '*7)
        state.append('      ')
        state.append('\n')
        state.append('      '*2)
        state.append('1Re   '*5)
        state.append('      '*2)
        state.append('\n')
        state.append('      '*3)
        state.append('2Bl   '*3)
        state.append('      '*3)
        state.append('\n\n')
        state.append('      '*4)
        state.append('===   ')
        state.append('      '*4)
        state.append('\n\n')
        state.append('      '*3)
        state.append('2Ye   '*3)
        state.append('      '*3)
        state.append('\n')
        state.append('      '*2)
        state.append('1Gr   '*5)
        state.append('      '*2)
        state.append('\n')
        state.append('      ')
        state.append('9Br   '*7)
        state.append('      ')
        state.append('\n\n')
        state.append('      '*8)
        state.append('===   ')
        state_str = ''.join(state)
        board = Board()
        board.stones = [2,2,2,2,0,2,2,2,1]
        for i in range(1,NUM_OF_STONES-1):
            board.cards[1][i].append(Card(9,1))
            board.cards[0][i].append(Card(9,2))
        for i in range(2,7):
            board.cards[1][i].append(Card(1,3))
            board.cards[0][i].append(Card(1,5))
        for i in range(3,6):
            board.cards[1][i].append(Card(2,6))
            board.cards[0][i].append(Card(2,4))
        self.assertEqual(state_str, str(board))
        self.assertEqual(state_str, board.change_pov().__repr__(1))
                   
    def test_copy(self):
        board = Board()
        board_copy = board.copy()
        board_copy.draw_card()
        board_copy.stones[0] = 1
        board_copy.cards[0][0].append(Card(1,1))
        board_copy.advantage[0] = 1
        board_copy.cards_on_board[0][0] = True
        self.assertEqual(len(board.deck),54)
        self.assertEqual(board.stones[0],0)
        self.assertEqual(len(board.cards[0][0]),0)
        self.assertEqual(board.advantage[0],0)
        self.assertFalse(board.cards_on_board[0][0])
        
    def test_is_legal_claim(self):
        hand1 = Hand([Card(2,2),Card(3,3)])
        hand2 = Hand([Card(9,3)])
        cards_on_board = [[False for _ in range(NUM_OF_COLORS)] for j in range(NUM_OF_NUMS)]
        cards_on_board[1][1] = True
        cards_on_board[2][2] = True
        cards_on_board[8][2] = True
        self.assertFalse(Board.is_legal_claim(hand1,hand2,False,cards_on_board))
        hand1.append(Card(1,1))
        cards_on_board[0][0] = True
        for i in range(NUM_OF_NUMS):
            cards_on_board[i][2] = True
        for col in range(NUM_OF_COLORS):
            cards_on_board[8][col] = True
            cards_on_board[7][col] = True
        self.assertTrue(Board.is_legal_claim(hand1,hand2,True,cards_on_board))
        for col in range(NUM_OF_COLORS):
            cards_on_board[8][col] = False
            cards_on_board[7][col] = False
        self.assertFalse(Board.is_legal_claim(hand1,hand2,True,cards_on_board))
        for i in range(NUM_OF_NUMS):
            cards_on_board[i][2] = False
        for col in range(NUM_OF_COLORS):
            cards_on_board[8][col] = True
            cards_on_board[7][col] = True
        self.assertFalse(Board.is_legal_claim(hand1,hand2,True,cards_on_board))
        hand3 = Hand([Card(6,2),Card(6,3),Card(6,4)])
        hand4 = Hand([Card(6,6),Card(6,5),Card(6,1)])
        self.assertFalse(Board.is_legal_claim(hand3,hand4,False,cards_on_board))
        self.assertTrue(Board.is_legal_claim(hand3,hand4,True,cards_on_board))
        
    def test_is_board_terminal(self):
        board = Board()
        self.assertEqual(board.is_board_terminal(),0)
        board.stones = [1,0,1,1,0,2,0,2,0]
        self.assertEqual(board.is_board_terminal(),0)
        board.stones = [1,1,1,1,0,2,0,2,0]
        self.assertEqual(board.is_board_terminal(),1)
        board.stones = [1,2,1,2,0,2,0,2,2]
        self.assertEqual(board.is_board_terminal(),2)
        board.stones = [1,1,1,2,0,2,2,1,2]
        self.assertEqual(board.is_board_terminal(),1)
        board.stones = [1,0,1,2,1,1,2,1,2]
        self.assertEqual(board.is_board_terminal(),1)
        
    def test_claim_stone(self):
        board = Board()
        board.place_card(1,Card(5,2),0)
        board.claim_stone(0,1)
        board.claim_stone(1,1)
        self.assertEqual(board.stones,[0 for _ in range(9)])
        board.place_card(1,Card(4,2),0)
        board.claim_stone(0,1)
        board.claim_stone(1,1)
        self.assertEqual(board.stones,[0 for _ in range(9)])
        board.place_card(1,Card(6,2),0)
        board.claim_stone(0,1)
        board.claim_stone(1,1)
        self.assertEqual(board.stones,[0 for _ in range(9)])
        board.place_card(2,Card(7,3),0)
        board.claim_stone(0,1)
        board.claim_stone(1,1)
        self.assertEqual(board.stones,[0 for _ in range(9)])
        board.place_card(1,Card(5,3),1)
        board.claim_stone(0,1)
        board.claim_stone(1,1)
        self.assertEqual(board.stones[1],1)
        board.place_card(1,Card(6,3),1)
        board.claim_stone(0,1)
        board.claim_stone(1,1)
        self.assertEqual(board.stones[1],1)
        self.assertEqual(board.stones,[0,1,0,0,0,0,0,0,0])
        
        board = Board()
        board.place_card(1,Card(5,2),1)
        board.claim_stone(0,1)
        board.claim_stone(1,1)
        self.assertEqual(board.stones,[0 for _ in range(9)])
        board.place_card(1,Card(4,2),1)
        board.claim_stone(0,1)
        board.claim_stone(1,1)
        self.assertEqual(board.stones,[0 for _ in range(9)])
        board.place_card(1,Card(6,2),1)
        board.claim_stone(0,1)
        board.claim_stone(1,1)
        self.assertEqual(board.stones,[0 for _ in range(9)])
        board.place_card(1,Card(7,3),0)
        board.claim_stone(0,1)
        board.claim_stone(1,1)
        self.assertEqual(board.stones,[0 for _ in range(9)])
        board.place_card(1,Card(5,3),0)
        board.claim_stone(0,1)
        board.claim_stone(1,1)
        self.assertEqual(board.stones,[0 for _ in range(9)])
        board.place_card(2,Card(6,3),1)
        board.claim_stone(0,1)
        board.claim_stone(1,1)
        self.assertEqual(board.stones[1],2)
        self.assertEqual(board.stones,[0,2,0,0,0,0,0,0,0])
    
    def test_board_for_player(self):
        board = Board()
        hand = [board.draw_card() for _ in range(6)]
        print([str(card) for card in board.deck])
        print(board)
        state = board.copy()
        state.deck = []
        for i in range(1,NUM_OF_COLORS + 1):
            for j in range(1, NUM_OF_NUMS + 1):
                if (not board.cards_on_board[j-1][i-1]) and (not Card(j,i) in hand):
                    state.deck.append(Card(j,i))
        print([str(card) for card in state.deck])
        print([str(card) for card in hand])
        print(state)
        self.assertEqual(len(state.deck),len(board.deck))
        
       
    def test_place_card_legal(self):
        board = Board()
        board.place_card(0,Card(1,1),0)
        board.place_card(8,Card(2,2),1)
        board.place_card(0,Card(9,6),0)
        board.place_card(0,Card(3,3),0)
        self.assertEqual(board.advantage[0],1)
        self.assertTrue(board.cards_on_board[0][0])
        self.assertTrue(board.cards_on_board[1][1])
        self.assertTrue(board.cards_on_board[8][5])
        self.assertTrue(board.cards_on_board[2][2])
        self.assertEqual(board.cards[1][8].hand, [Card(2,2)])
        self.assertEqual(board.cards[0][0].hand, [Card(1,1),Card(9,6),Card(3,3)])
 
class test_game(unittest.TestCase):
    def test_init(self):
        pass
    
class test_MCTS(unittest.TestCase):
    def test_simulate_turn(self):
        pass
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(test_board('test_board_for_player'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())        
    #unittest.main()
    
        