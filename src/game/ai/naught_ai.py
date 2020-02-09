import copy


import naught_util
import ai_strats
import numpy as np
from neural_net import NeuralNet
from naught_tree import Node


class NaughtAI:
    def __init__(self, nc, player=None, nn=None, strat="deterministic", depth=float("inf")):
        # self.best_moves = []
        self.nc = nc
        self.tree = None
        self.expected_board = naught_util.get_empty_i1_board()
        self.nn = nn
        self.depth = depth
        if strat == "deterministic":
            self.move_strat = ai_strats.deterministic_move
            self.score_strat = ai_strats.deterministic_score
            self.inform_strat = ai_strats.inform_update
        elif strat == "random":
            self.move_strat = ai_strats.random_move
            self.score_strat = ai_strats.deterministic_score
            self.inform_strat = ai_strats.inform_no_update
        elif strat == "nn":
            self.move_strat = ai_strats.nn_move
            self.score_strat = ai_strats.nn_score
            self.inform_strat = ai_strats.inform_no_update
            if nn is None:
                # print("No Neural net input. Creating new")
                self.nn = NeuralNet()
                self.nn.init_net(input_size=10, output_size=1, hidden_size=20, number_of_hidden=10)
            if depth == float("inf"):
                # print("No tree depth set. Setting to 4")
                self.depth = 4
            # raise NotImplemented("nn strats not implemented")
        if player is None:
            # print("No Player argument given. AI set to play as X")
            self.player = 'X'
            self.i1_player = 1
        else:
            if not (player == 'X' or player == 'O'):
                raise ValueError("Stop misusing my god damned code. X and O are the only legal players!")
            else:
                self.player = player
                if player == 'X':
                    self.i1_player = 1
                else:
                    self.i1_player = -1

    def make_move(self, rand=0.0):
        if self.player != self.nc.next:
            return False, None, "Not this players turn"
        if not self.nc.game_in_progress:
            return False, None, "Game already finished"
        move = self.move_strat(self, rand)
        success, msg = self.nc.make_move(move[0], self.player)
        if not success:
            raise EnvironmentError("Move unsuccessful. Something fucked up.", msg)
        self.expected_board = naught_util.char_to_i1_board(self.nc.board)
        if not np.array_equal(self.expected_board, naught_util.char_to_i1_board(self.nc.board)):
            raise EnvironmentError("Board expectation mixed up. Something fucked up.")
        return True, move, msg

    def inform_opponent_move(self, move):
        return self.inform_strat(self, move)

    def score_board(self, board, is_my_turn=None):
        if board is None:
            board = self.nc.board
        return self.score_strat(self, board, is_my_turn)

    # def reset_ai_state(self):
    #     is_in_turn = self.nc.next == self.player
    #     self.tree = ai_strats._build_state_tree(self, board=self.nc.board)
    #     ai_strats._min_max_tree(self, is_in_turn, tree=self.tree)
    #     # self.best_moves = self.find_best_moves(root=self.tree, is_my_turn=is_in_turn)
    #     self.expected_board = naught_util.char_to_i1_board(self.nc.board)

    # def find_best_moves(self, root=None, is_my_turn=True):
    #     if root is None:
    #         if self.tree is None:
    #             root = ai_strats._build_state_tree(self)
    #         else:
    #             root = self.tree
    #     if root.score is None:
    #         ai_strats._min_max_tree(self, is_my_turn, tree=root)
    #     node = root
    #     path = []
    #     while node.best_child is not None:
    #         path.append(node.best_child)
    #         node = node.children[node.best_child]
    #     self.best_moves = path
    #     return path

    # def build_state_tree(self, board=None, last_turn=None):
    #     if board is None:
    #         board = self.nc.board
    #     if last_turn is None:
    #         last_turn = naught_util.to_i1(self.nc.next)
    #     if board.dtype == np.dtype('<U1'):
    #         board = naught_util.char_to_i1_board(board)
    #     tree = self.__build_state_tree(board, (None, last_turn * -1))
    #     self.tree = tree
    #     return tree
    #
    # def __build_state_tree(self, board, move):  # Multi threading?
    #     score = self.score_board(board)
    #     this_node = Node(move=move, score=score, board=board)
    #     # if score is not None:
    #         # print("score = " + str(score))
    #         # return this_node
    #     moves = naught_util.get_free_tiles(board)
    #     if len(moves) == 0:
    #         return this_node
    #     player_last_turn = move[1]
    #     player_this_turn = player_last_turn * -1
    #     for i in range(len(moves)):
    #         new_board = copy.deepcopy(board)
    #         new_board[moves[i]] = player_this_turn
    #         this_node.children.append(self.__build_state_tree(new_board, (moves[i], player_this_turn)))
    #     return this_node
    #
    # def score_board(self, board=None):
    #     if board is None:
    #         board = self.nc.board
    #     return naught_util.score_board(board, self.i1_player)
    #
    # def find_best_moves(self, root=None, is_my_turn=True):
    #     if root is None:
    #         if self.tree is None:
    #             root = self.build_state_tree()
    #         else:
    #             root = self.tree
    #     if root.score is None:
    #         self.min_max_tree(is_my_turn, tree=root)
    #     node = root
    #     path = []
    #     while node.best_child is not None:
    #         path.append(node.best_child)
    #         node = node.children[node.best_child]
    #     self.best_moves = path
    #     return path
    #
    # def min_max_tree(self, is_my_turn, tree=None):  # Mutates tree
    #     if tree is None:
    #         tree = self.build_state_tree()
    #     self.__min_max_tree(is_my_turn, tree)
    #     return tree
    #
    # def __min_max_tree(self, maxing, node):
    #     if node.score is not None:
    #         return node.score
    #     num_children = len(node.children)
    #     min_max_score = None
    #     best_child = None
    #     for i in range(num_children):
    #         child_score = self.__min_max_tree((not maxing), node.children[i])
    #         if min_max_score is None:
    #             min_max_score = child_score
    #             best_child = i
    #         elif maxing and child_score > min_max_score:
    #             best_child = i
    #             min_max_score = child_score
    #         elif not maxing and child_score < min_max_score:
    #             best_child = i
    #             min_max_score = child_score
    #     node.best_child = best_child
    #     node.score = min_max_score
    #     return node.score
    #
    # def make_move(self):
    #     if self.player != self.nc.next:
    #         return False, None, "Not this players turn"
    #     msg = ""
    #     if self.tree is None:
    #         self.reset_ai_state()
    #         msg = msg + "Had to reset tree, due to no tree found. "
    #     actual_i1 = naught_util.char_to_i1_board(self.nc.board)
    #     if not np.array_equal(self.expected_board, actual_i1):  # self.expected_board != actual_i1:
    #         next_board = self.tree.children[self.best_moves[0]]
    #         if np.array_equal(actual_i1, next_board):  # == next_board:
    #             self.expected_board = next_board
    #             self.tree = self.tree.children[self.best_moves.pop(0)]
    #             msg = msg + "Discrepancy between actual board state and expected. Fixed by looking ahead. "
    #         else:
    #             self.reset_ai_state()
    #             msg = msg + "Discrepancy between actual board state and expected. Had to reset tree. "
    #     best_move = self.tree.children[self.best_moves[0]].move_from_parent
    #     success, msg_from_nc = self.nc.make_move(best_move[0], self.player)
    #     if not success:
    #         return False, None, msg_from_nc
    #     self.tree = self.tree.children[self.best_moves.pop(0)]
    #     self.expected_board = self.tree.board
    #     if not np.array_equal(self.expected_board, naught_util.char_to_i1_board(self.nc.board)):
    #         raise RuntimeError("FUCK")
    #     return True, best_move, "Move Successful. " + msg
    #
    # def reset_ai_state(self):
    #     is_in_turn = self.nc.next == self.player
    #     self.tree = self.build_state_tree(board=self.nc.board)
    #     self.min_max_tree(is_in_turn, tree=self.tree)
    #     self.best_moves = self.find_best_moves(root=self.tree, is_my_turn=is_in_turn)
    #     self.expected_board = naught_util.char_to_i1_board(self.nc.board)
    #
    # def inform_opponent_move(self, move):
    #     new_expected = copy.deepcopy(self.expected_board)
    #     new_expected[move] = self.i1_player * -1
    #     if not np.array_equal(new_expected, naught_util.char_to_i1_board(self.nc.board)):
    #         self.reset_ai_state()
    #         return False, "Nc board different from what the move would change it to"
    #     if self.tree is None:
    #         return True, "Informed. No tree found"
    #     new_root_child_num = None
    #     for i in range(len(self.tree.children)):
    #         move_in_tree = self.tree.children[i].move_from_parent
    #         if move == move_in_tree[0]:
    #             new_root_child_num = i
    #             break
    #     if new_root_child_num is None:
    #         self.reset_ai_state()
    #         return True, "Success, but tree had to be rebuilt"
    #     self.expected_board = new_expected
    #     self.tree = self.tree.children[new_root_child_num]
    #     self.find_best_moves(root=self.tree)
    #     return True, "Success"




