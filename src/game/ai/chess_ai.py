import numpy as np
import copy
import time
from chess.chess import Chess
from ai.tree import Node
# from chess.chess_util import efficient_copy

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
# TODO: More efficient copy (Doesn't actually seem to be that much of a problem). No need to copy legal_moves
# TODO: proper evaluation function argument structure/usage
def choose_move_ab(chess, depth=4, evaluation_function=None, return_tree=False):
    assert depth > 0
    legal_moves = chess.legal_moves
    if not legal_moves or not chess.is_in_progress:  # If empty list of moves, or game having ended (should always be the same situation except testing scenarios)
        return None
    root = Node(content={"chess": copy.deepcopy(chess), "move": None})
    maximizing = True if chess.in_turn == 1 else False
    time_dict = {"move": 0, "copy": 0, "eval": 0, "other": 0, "node_creation": 0}

    val = alpha_beta_prune(root, depth, maximizing, time_dict=time_dict)  # TODO fix eval function arg stuff here
    # print(time_dict)
    # print("Root node val: ", val)
    move = None
    # print("Children: ", len(root.children))
    for child in root.children:
        # print("child val: ", child.value)
        if child.value == val:
            if return_tree:
                return child.content["move"], root, time_dict
            return child.content["move"]
    raise Exception("No children with the expected value")
    

# TODO count branching factor and total number of nodes. Consider sorting moves based on heuristic
# TODO: Optimize (e.g. evaluate better looking branches first, iterative deepening)
# TODO: Consider: current approach does not lend itself easily to reusing tree next time. Only some branches are created, with no knowledge of which moves have corresponding nodes
# TODO: Generalize s.t. it can be used for other things than chess (probably wont do ? )
def alpha_beta_prune(node, depth, maximizing, alpha=-float('inf'), beta=float('inf'), eval_fun=sum_eval, time_dict=None):
    # assert depth >= 0
    # print("depth: ", depth, "a: ", alpha, ", b: ", beta)
    # if time_dict is None:
        # time_dict = {"move": 0, "copy": 0, "other": 0}
    if depth == 0:
        start_eval = time.clock()
        node.value = eval_fun(node.content)
        end_eval = time.clock()
        time_dict["eval"] += end_eval - start_eval
        return node.value
    value = -float('inf') if maximizing else float("inf")

    chess = node.content["chess"]
    for move in chess.legal_moves:
        start_copy = time.clock()
        # chess_copy = copy.deepcopy(chess)
        chess_copy = chess._efficient_copy()
        time_dict["copy"] += time.clock() - start_copy
        start_move = time.clock()
        chess_copy.move(move)
        time_dict["move"] += time.clock() - start_move
        start_node = time.clock()
        child_node = Node(content={"chess": chess_copy, "move": move})
        node.children.append(child_node)
        end_node = time.clock()
        time_dict["node_creation"] += end_node - start_node
        # rec_start = time.clock()
        child_val = alpha_beta_prune(child_node, depth - 1, not maximizing, alpha=alpha, beta=beta, time_dict=time_dict)
        # rec_end = time.clock()
        # recursion_time += rec_end - rec_start
        other_start = time.clock()
        child_node.value = child_val

        value = max(value, child_val) if maximizing else min(value, child_val)
        if maximizing:
            alpha = max(value, alpha)
        else:
            beta = min(value, beta)
        other_end = time.clock()
        time_dict["other"] += other_end - other_start
        if alpha >= beta:
            break
    # end_other = time.clock()
    # time_dict["other"] += end_other - start_other - recursion_time
    return value

# def efficient_copy(chess):
#     chess_dict = {"board": copy.deepcopy(chess.board),
#                   "in_turn": chess.in_turn,
#                   "turn_num": chess.turn_num,
#                   "is_in_progress": chess.is_in_progress,
#                   "draw_counter": chess.draw_counter,
#                   "winner": chess.winner,
#                   "last_move": chess.last_move,
#                   "legal_castles": copy.deepcopy(chess.legal_castles),
#                   "legal_moves": []}
#     return Chess(chess_dict=chess_dict)

# self.board = chess_util.get_start_board()
#             self.in_turn = 1
#             self.turn_num = 1
#             self.is_in_progress = True
#             self.draw_counter = 0
#             self.winner = None
#             self.last_move = None
#             self.legal_castles = {'(0, 2)' : True, '(0, 6)' : True, '(7, 2)' : True, '(7, 6)' : True}  # String keys for easier node communication
#             self.legal_moves = get_legal_moves(self, self.in_turn)

def count_tree_size(node, count_dict, level):
    count_dict["count"] += 1
    if not node.children: # children is empty -> leaf node
        return
    if len(count_dict["branch"]) <= level > 0:
        count_dict["branch"].append([])
    count_dict["branch"][level].append(len(node.children))
    for child in node.children:
        count_tree_size(child, count_dict, level + 1)



# TODO monte carlo