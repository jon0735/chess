import numpy as np
import copy
from ai.tree import Node

# Most of this could be implemented more generally, instead of being hardcoded for chess. Consider doing this (If I suddenly have a bunch of free time (lol))

count = 0

def sum_eval(chess_content):
    chess = chess_content["chess"]
    if not chess.is_in_progress:
        if chess.winner == 1:
            return 100
        elif chess.winner == -1:
            return -100
        else:
            return 0
    return np.sum(chess_content["chess"].board)

def nn_eval(chess):
    pass


#Alpha beta choice
# TODO: More efficient copy. No need to copy legal_moves
# TODO: proper evaluation function argument structure/usage
def choose_move_ab(chess, depth=4, evaluation_function=None):
    assert depth > 0
    legal_moves = chess.legal_moves
    if not legal_moves or not chess.is_in_progress:  # If empty list of moves, or game having ended (should always be the same situation except testing scenarios)
        return None
    root = Node(content={"chess": copy.deepcopy(chess), "move": None})
    maximizing = True if chess.in_turn == 1 else False
    val = alpha_beta_prune(root, depth, maximizing)  # TODO fix eval function arg stuff here
    # print("Root node val: ", val)
    move = None
    # print("Children: ", len(root.children))
    for child in root.children:
        # print("child val: ", child.value)
        if child.value == val:
            return child.content["move"]
    raise Exception("No children with the expected value")
    


# TODO: Optimize (e.g. evaluate better looking branches first, iterative deepening)
# TODO: Consider: current approach does not lend itself easily to reusing tree next time. Only some branches are created, with no knowledge of 
# TODO: Generalize s.t. it can be used for other things than chess (probably wont do ? )
def alpha_beta_prune(node, depth, maximizing, alpha=-float('inf'), beta=float('inf'), eval_fun=sum_eval, count=None):    
    # if count is None:
    #     count = {"count": 0}
    # else:
    #     count["count"] += 1
    # print("AB-Prune. depth: ", depth, ", maximizing: ", maximizing, ", a: ", alpha, ", b: ", beta, ", count: ", count["count"])
    assert depth >= 0
    if depth == 0:
        node.value = eval_fun(node.content)
        return node.value
    if maximizing:
        value = -float('inf')
        chess = node.content["chess"]
        for move in chess.legal_moves:
            chess_copy = copy.deepcopy(chess)
            chess_copy.move(move)
            child_node = Node(content={"chess": chess_copy, "move": move})
            node.children.append(child_node)
            child_val = alpha_beta_prune(child_node, depth - 1, not maximizing, alpha=alpha, beta=beta, count=count)
            child_node.value = child_val
            value = max(value, child_val)
            alpha = max(value, alpha)
            if alpha >= beta:
                break
        return value
    else:
        value = float('inf')
        chess = node.content["chess"]
        for move in chess.legal_moves:
            chess_copy = copy.deepcopy(chess)
            chess_copy.move(move)
            child_node = Node(content={"chess": chess_copy, "move": move})
            node.children.append(child_node)
            child_val = alpha_beta_prune(child_node, depth - 1, not maximizing, alpha=alpha, beta=beta, count=count)
            child_node.value = child_val
            value = min(value, child_val)
            beta = min(value, beta)
            if alpha >= beta:
                break
        return value

# TODO monte carlo