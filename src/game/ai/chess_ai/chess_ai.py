import numpy as np
import copy
import time
import sys
import random
from pathlib import Path
# print(sys.path)
# from chess.chess import Chess
# sys.path.append("..")
from game.ai.chess_ai.tree import Node
from game.ai.nn.neural_net import NeuralNet
# from chess.chess_util import efficient_copy

# Most of this could be implemented more generally, instead of being hardcoded for chess. Consider doing this (If I suddenly have a bunch of free time (lol))

count = 0  # Wtf?

# Very simple evaluation function, primarily for testing/comparison
def sum_eval(chess_content, nn=None):
    chess = chess_content["chess"]
    if not chess.is_in_progress:
        if chess.winner == 1:
            return 100
        elif chess.winner == -1:
            return -100
        else:
            return 0
    return np.sum(chess.board)

def nn_eval(chess_content, nn=None):
    chess = chess_content["chess"]
    if not chess.is_in_progress:
        result = 0 if chess.winner is None else chess.winner
        return result
    nn_input = chess_to_nn_input(chess)
    return nn.predict(nn_input)[0]

# TODO: Move to some util file
def chess_to_nn_input(chess):
    nn_input = np.zeros(386)  # 64 board position x 6 piece types + in_turn + draw_counter (include turn_num ?)
    board = chess.board
    for r in range(8):
        for c in range(8):
            piece = board[r, c]
            if piece == 0:
                continue
            val = 1 if piece > 0 else -1
            piece_type = abs(piece)
            if piece_type == 10:
                offset = 4
            elif piece_type == 100:
                offset = 5
            else:
                offset = piece_type - 1
            array_location = ((r * 8 + c) * 6) + offset
            nn_input[array_location] = val
    nn_input[384] = chess.in_turn
    nn_input[385] = chess.draw_counter
    return nn_input


#Alpha beta choice
# TODO: More efficient copy (Doesn't actually seem to be that much of a problem). No need to copy legal_moves (done)
# TODO: proper evaluation function argument structure/usage
def choose_move_ab(chess, depth=4, eval_fun=sum_eval, nn=None, return_tree=False, randomize=True):
    assert depth > 0
    legal_moves = chess.legal_moves
    if not legal_moves or not chess.is_in_progress:  # If empty list of moves, or game having ended (should always be the same situation except testing scenarios)
        return None
    root = Node(content={"chess": copy.deepcopy(chess), "move": None})
    maximizing = True if chess.in_turn == 1 else False
    time_dict = {"move": 0, "copy": 0, "eval": 0, "other": 0, "node_creation": 0}

    val = alpha_beta_prune(root, depth, maximizing, eval_fun=eval_fun, nn=nn, time_dict=time_dict)  # TODO fix eval function arg stuff here
    # print(time_dict)
    # print("Root node val: ", val)
    move = None
    # print("Children: ", len(root.children))
    if randomize:
        random.shuffle(root.children)
    for child in root.children:
        # print("child val: ", child.value)
        if child.value == val:
            if return_tree:
                return child.content["move"], root, time_dict
            return child.content["move"], child.value
    raise Exception("No children with the expected value")


# def choose_move_ab_nn(chess, depth=3, return_tree=False, nn=None):
#     if nn is None:
#         #TODO load/create nn
#         pass
#     pass


# TODO count branching factor and total number of nodes. Consider sorting moves based on heuristic
# TODO: Optimize (e.g. evaluate better looking branches first, iterative deepening)
# TODO: Consider: current approach does not lend itself easily to reusing tree next time. Only some branches are created, with no knowledge of which moves have corresponding nodes
# TODO: Generalize s.t. it can be used for other things than chess (probably wont do ? )
def alpha_beta_prune(node, depth, maximizing, alpha=-float('inf'), beta=float('inf'), eval_fun=sum_eval, nn=None, time_dict=None):
    # assert depth >= 0
    # print("depth: ", depth, "a: ", alpha, ", b: ", beta)
    # if time_dict is None:
        # time_dict = {"move": 0, "copy": 0, "other": 0}
    if depth == 0:
        # start_eval = time.clock()
        node.value = eval_fun(node.content, nn=nn)
        # end_eval = time.clock()
        # time_dict["eval"] += end_eval - start_eval
        return node.value
    value = -float('inf') if maximizing else float("inf")

    chess = node.content["chess"]
    for move in chess.legal_moves:
        # start_copy = time.clock()
        # chess_copy = copy.deepcopy(chess)
        chess_copy = chess._efficient_copy()
        # time_dict["copy"] += time.clock() - start_copy
        # start_move = time.clock()
        chess_copy.move(move)
        # time_dict["move"] += time.clock() - start_move
        # start_node = time.clock()
        child_node = Node(content={"chess": chess_copy, "move": move})
        node.children.append(child_node)
        # end_node = time.clock()
        # time_dict["node_creation"] += end_node - start_node
        # rec_start = time.clock()
        child_val = alpha_beta_prune(child_node, depth - 1, not maximizing, alpha=alpha, beta=beta, eval_fun=eval_fun, nn=nn, time_dict=time_dict)
        # rec_end = time.clock()
        # recursion_time += rec_end - rec_start
        # other_start = time.clock()
        child_node.value = child_val

        value = max(value, child_val) if maximizing else min(value, child_val)
        if maximizing:
            alpha = max(value, alpha)
        else:
            beta = min(value, beta)
        # other_end = time.clock()
        # time_dict["other"] += other_end - other_start
        if alpha >= beta:
            break
    # end_other = time.clock()
    # time_dict["other"] += end_other - start_other - recursion_time
    return value


def count_tree_size(node, count_dict, level):
    count_dict["count"] += 1
    if not node.children: # children is empty -> leaf node
        return
    if len(count_dict["branch"]) <= level > 0:
        count_dict["branch"].append([])
    count_dict["branch"][level].append(len(node.children))
    for child in node.children:
        count_tree_size(child, count_dict, level + 1)


def latest_nn_move(chess, depth=2):
    nn = load_nn("best")
    move, val = choose_move_ab(chess, depth=depth, eval_fun=nn_eval, nn=nn, randomize=False)
    return move, val


def load_nn(file_name):
    path = Path(__file__).parent.absolute()
    x = np.load(str(path) + "/saved_nns/" + file_name + ".npz")
    return NeuralNet(W=x["W"], b=x["b"])

# C:\Users\Jon\Documents\Uni\Git\chess\src\game\ai\nn\saved_nns
# TODO refactor big time. Especially default args in regards to sum_eval, nn_eval and nn
# TODO monte carlo