import numpy as np

def card_to_index(card):
    pass

def combination_to_index(combination):
    pass

def compute_prob(size_of_deck,num_of_cards):  
    curr_turn = 54-size_of_deck + 1
    k = curr_turn // 2
    x1, x2 = 28-k, 61-2*k
    if curr_turn % 2 == 1:
        x1 -= 1
        x2 -= 1
    if num_of_cards == 2:
        return (x1*(x1-1))/(x2*(x2-1))
    if num_of_cards == 1:
        return x1/x2
    if num_of_cards == 3:    
        return (x1*(x1-1)*(x1-2))/(x2*(x2-1)*(x2-2)) 
    
def get_available_combinations(combination_matrix, not_on_board):
    # combination matrix is (54 choose 3) x 54 
    # not on board is 54x1
    
    return np.sum(combination_matrix @ not_on_board, axis=1) == 3

def chance_of_winning(combination_index, available_combinations, prob):
    # available combinations for the opponent
    # prob for the opponent
    if combination_index == available_combinations.size()-1:
        return 1
    return prob *(1 - np.sum(available_combinations[combination_index+1,:], axis=1))
    


        