import numpy as np
import copy
from ai.tree import Node

# Most of this could be implemented more generally, instead of being hardcoded for chess. Consider doing this (If I suddenly have a bunch of free time (lol))

def sum_eval(chess_content):
    return np.sum(chess_content["chess"].board)

def nn_eval(chess):
    pass


#Alpha beta choice
# TODO: More efficient copy. No need to copy legal_moves
# TODO: proper evaluation function argument structure/usage
def choose_move_ab(chess, depth=4, evaluation_function=None):
    legal_moves = chess.legal_moves
    if not legal_moves or not chess.is_in_progress:  # If empty list of moves, or game having ended (should always be the same situation except testing scenarios)
        return None
    root = Node(content=copy.deepcopy(chess))
    pass

def alpha_beta_prune(node, depth, maximizing, alpha=float('inf'), beta=-float('inf'), eval_fun=sum_eval):
    if depth == 0:
        node.value = eval_fun(node.content)
        return node.value
    if maximizing:
        value = -float('inf')

    else:
        value = float('inf')
        pass


