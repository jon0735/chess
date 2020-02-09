import random

import naught_util
# from ai import NaughtAI
import numpy as np
from naught_tree import Node
import copy
import nn_util

"""
Move Strats
"""


def deterministic_move(ai, rand):
    if ai.tree is None or not np.array_equal(ai.expected_board, naught_util.char_to_i1_board(ai.nc.board)):
        _build_state_tree(ai)  # ai.tree = _build_state_tree(ai)
    if ai.tree.score is None:
        _min_max_tree(ai, tree=ai.tree)
    best_moves = []
    best_score = -float("inf")
    for child in ai.tree.children:
        if child.score > best_score:
            best_score = child.score
    for i, child in enumerate(ai.tree.children):
        if child.score == best_score:
            best_moves.append(i)
    best = random.choice(best_moves)
    ai.tree = ai.tree.children[best]
    return ai.tree.move_from_parent


def random_move(ai, rand):
    moves = naught_util.get_free_tiles(ai.nc.board)
    move = random.choice(moves)
    return move, ai.player


def nn_move(ai, rand):
    if rand > 0 and rand > random.uniform(0, 1):
        return random_move(ai, 0)
    _build_state_tree(ai, depth=ai.depth, stop_function=depth_stop)
    _min_max_tree(ai, tree=ai.tree)
    ai.tree = ai.tree.children[ai.tree.best_child]
    return ai.tree.move_from_parent


def deterministic_stop(board, depth):
    won, _ = naught_util.check_winner(board)
    return won


def depth_stop(board, depth):
    return depth == 0


def _build_state_tree(ai, board=None, last_turn=None, depth=float("inf"), stop_function=deterministic_stop):
    if board is None:
        board = ai.nc.board
    if last_turn is None:
        last_turn = naught_util.to_i1(ai.nc.next)
    if board.dtype == np.dtype('<U1'):
        board = naught_util.char_to_i1_board(board)
    tree = __build_state_tree(ai, board, (None, last_turn * -1), depth, stop_function)
    ai.tree = tree
    return tree


def __build_state_tree(ai, board, move, depth, stop_function):  # Multi threading?
    # score = ai.score_board(board)
    this_node = Node(move=move, score=None, board=board)
    if stop_function(board, depth):
        return this_node
    moves = naught_util.get_free_tiles(board)
    if len(moves) == 0:
        return this_node
    player_last_turn = move[1]
    player_this_turn = player_last_turn * -1
    # for i in range(len(moves)):
    for m in moves:
        new_board = copy.deepcopy(board)
        new_board[m] = player_this_turn
        this_node.children.append(__build_state_tree(ai, new_board, (m, player_this_turn), depth - 1, stop_function))
    return this_node


def _min_max_tree(ai, tree, is_my_turn=True):  # Mutates tree
    if tree is None:
        raise EnvironmentError("Min max called for an ai which has no tree")
        # tree = _build_state_tree(ai)
    __min_max_tree(ai, is_my_turn, tree)
    return tree


def __min_max_tree(ai, maxing, node):
    # if node.score is not None:
    #     return node.score
    num_children = len(node.children)
    if num_children == 0:
        node.score = ai.score_board(node.board, node.move_from_parent[-1] * -1)
        # print("leaf score:", node.score)
        return node.score
    min_max_score = None
    best_child = None
    best_children = []
    for i in range(num_children):
        child_score = __min_max_tree(ai, (not maxing), node.children[i])
        if min_max_score is None:
            min_max_score = child_score
            best_children.append(i)
            # best_child = i
        elif maxing and child_score > min_max_score:
            # best_child = i
            best_children = [i]
            min_max_score = child_score
        elif maxing and child_score == min_max_score:
            best_children.append(i)
        elif not maxing and child_score < min_max_score:
            # best_child = i
            best_children = [i]
            min_max_score = child_score
        elif not maxing and child_score == min_max_score:
            best_children.append(i)
    if len(best_children) > 0:
        node.best_child = random.choice(best_children)
    else:
        node.best_child = None
    # node.best_child = best_child
    node.score = min_max_score
    return node.score


"""
Score Strats
"""


def deterministic_score(ai, board, is_my_turn):
    return naught_util.score_board(board, ai.i1_player)


def nn_score(ai, board, is_in_turn):
    if is_in_turn is None:
        raise ValueError("scoring state needs and argument for who's turn it is when using nn for scoring")
    x = nn_util.state_to_input(board, is_in_turn, ai.i1_player)
    return ai.nn.predict(x)[0]


"""
Inform Strats
"""


def inform_update(ai, move):
    new_expected = copy.deepcopy(ai.expected_board)
    new_expected[move] = ai.i1_player * -1
    if not np.array_equal(new_expected, naught_util.char_to_i1_board(ai.nc.board)):
        return False, "Nc board different from what the move would change it to"
    if ai.tree is None:
        return True, "Informed. No tree found"
    new_root_child_num = None
    for i, child in enumerate(ai.tree.children):  # in range(len(self.tree.children)):
        move_in_tree = child.move_from_parent
        if move == move_in_tree[0]:
            new_root_child_num = i
            break
    if new_root_child_num is None:
        return False, "Could not find a child state matching the move"
    ai.expected_board = new_expected
    ai.tree = ai.tree.children[new_root_child_num]
    return True, "Success"


def inform_no_update(ai, move):
    return True, "No update for this strategy"



