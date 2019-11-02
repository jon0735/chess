# import sys
# sys.path.append("..")

import chess_util
import chess
from chess import Chess
from chess import Move
from naught_cross import NaughtCross
from ai import NaughtAI
from tree import Node
from nc_nn import NaughtCrossNeuralNet as NN

import unittest
import numpy as np
import naught_util
import copy
import nn_util
import ai_strats

empty_nc_board = naught_util.get_empty_char_board()
x_win_nc_board = np.array([['X', 'X', 'X'], ['O', 'O', ' '], [' ', ' ', ' ']])
o_win_nc_board = np.array([['X', 'X', ' '], ['O', 'O', 'O'], ['X', 'X', ' ']])
stale_mate_nc_board = np.array([['X', 'X', 'O'], ['O', 'O', 'X'], ['X', 'X', 'O']])
not_finished_nc_board1 = np.array([[' ', 'X', 'O'], ['O', 'X', 'O'], ['X', 'O', 'X']])


# noinspection PyTypeChecker
class TestNC(unittest.TestCase):

    def setUp(self):
        self.nc = NaughtCross()

    def test_empty_start_board(self):
        self.assertTrue(np.array_equal(self.nc.board, empty_nc_board))

    def test_legal_start_move(self):
        b, msg = self.nc.make_move((1, 2), 'X')
        self.assertTrue(b, "failed with msg: " + msg)
        self.assertEqual(self.nc.board[1, 2], 'X')

    def test_move_type(self):
        b, m = self.nc.make_move(2, 'X')
        self.assertFalse(b)
        self.assertEqual("Pos argument must be an integer tuple with values between 0-2", m)

    def test_out_of_bounds_move(self):
        b = [None] * 8
        b[0], m = self.nc.make_move((-1, -1), 'X')
        b[1], _ = self.nc.make_move((-1, 1), 'X')
        b[2], _ = self.nc.make_move((-1, 3), 'X')
        b[3], _ = self.nc.make_move((1, -1), 'X')
        b[4], _ = self.nc.make_move((1, 3), 'X')
        b[5], _ = self.nc.make_move((3, -1), 'X')
        b[6], _ = self.nc.make_move((3, 1), 'X')
        b[7], _ = self.nc.make_move((3, 3), 'X')
        for i in range(8):
            self.assertFalse(b[i])

        self.assertTrue(np.array_equal(self.nc.board, empty_nc_board))
        self.assertEqual(m, "Move outside of board")

    def test_move_on_occupied_spot(self):
        self.nc.make_move((0, 0), 'X')
        b, m = self.nc.make_move((0, 0), 'O')
        self.assertFalse(b)
        self.assertEqual(m, "Spot already occupied")

    def test_player_legal_turn(self):
        b1, _ = self.nc.make_move((1, 1), 'X')
        b2, _ = self.nc.make_move((1, 2), 'O')
        b3, _ = self.nc.make_move((2, 2), 'X')

        self.assertTrue(b1)
        self.assertTrue(b2)
        self.assertTrue(b3)

    def test_player_illegal_turn(self):
        b1, _ = self.nc.make_move((1, 1), 'X')
        b2, _ = self.nc.make_move((1, 2), 'X')
        b3, _ = self.nc.make_move((2, 2), 'O')
        self.assertTrue(b1)
        self.assertFalse(b2)
        self.assertTrue(b3)

    def test_winner1(self):
        self.nc.make_move((0, 0), 'X')
        self.nc.make_move((1, 0), 'O')
        self.nc.make_move((0, 1), 'X')
        self.nc.make_move((2, 0), 'O')
        self.nc.make_move((0, 2), 'X')

        self.assertEqual(self.nc.winner, 'X')

    def test_winner2(self):
        self.nc.make_move((0, 0), 'X')
        self.nc.make_move((1, 0), 'O')
        self.nc.make_move((1, 1), 'X')
        self.nc.make_move((2, 0), 'O')
        self.nc.make_move((2, 2), 'X')

        self.assertEqual(self.nc.winner, 'X')

    def test_winner3(self):
        self.nc.make_move((0, 0), 'X')
        self.nc.make_move((2, 0), 'O')
        self.nc.make_move((0, 1), 'X')
        self.nc.make_move((2, 1), 'O')
        self.nc.make_move((1, 2), 'X')
        self.nc.make_move((2, 2), 'O')

        self.assertEqual(self.nc.winner, 'O')

    def test_illegal_after_win(self):
        self.nc.make_move((0, 0), 'X')
        self.nc.make_move((1, 0), 'O')
        self.nc.make_move((1, 1), 'X')
        self.nc.make_move((2, 0), 'O')
        self.nc.make_move((2, 2), 'X')
        b, m = self.nc.make_move((0, 1), 'O')
        self.assertFalse(b)
        self.assertEqual(m, "Game over")

    def test_get_legal_moves_nc(self):
        all_moves = [(i, j) for i in range(3) for j in range(3)]
        legal_start, player = self.nc.get_legal_moves()
        self.assertEqual(sorted(all_moves), sorted(legal_start))
        self.assertEqual('X', player)

        self.nc.make_move((1, 1), 'X')

        legal, player = self.nc.get_legal_moves()
        all_moves.remove((1, 1))
        self.assertEqual(all_moves, legal)
        self.assertEqual('O', player)

    def test_board_constructor(self):
        board = np.full((3, 3), ' ')
        board[1, 1] = 'X'
        nc = NaughtCross(board=board)
        self.assertTrue(np.array_equal(nc.board, board))

    def test_player_constructor(self):
        nc = NaughtCross(starting_player='O')
        self.assertEqual(nc.next, 'O')


class TestNaughtUtil(unittest.TestCase):

    def test_get_legal_moves(self):
        all_moves = [(i, j) for i in range(3) for j in range(3)]
        legal_start = naught_util.get_free_tiles(empty_nc_board)
        self.assertEqual(sorted(all_moves), sorted(legal_start))

    def test_get_winner(self):
        b1, w1 = naught_util.check_winner(empty_nc_board)
        self.assertFalse(b1)
        self.assertIsNone(w1)
        b2, w2 = naught_util.check_winner(x_win_nc_board)
        self.assertTrue(b2)
        self.assertEqual(w2, 'X')
        b3, w3 = naught_util.check_winner(o_win_nc_board)
        self.assertTrue(b3)
        self.assertEqual(w3, 'O')
        b4, w4 = naught_util.check_winner(not_finished_nc_board1)
        self.assertFalse(b4)
        self.assertIsNone(w4)

    def test_get_winner2(self):
        b1 = np.array([['X', 'O', 'X'], ['O', 'O', 'X'], ['O', 'X', 'X']])
        _, w1 = naught_util.check_winner(b1)
        self.assertEqual(w1, 'X')

    def test_winner_systematic(self):
        x_win_boards = [np.array([['X', 'X', 'X'], [' ', ' ', ' '], [' ', ' ', ' ']]),
                        np.array([[' ', ' ', ' '], ['X', 'X', 'X'], [' ', ' ', ' ']]),
                        np.array([[' ', ' ', ' '], [' ', ' ', ' '], ['X', 'X', 'X']]),
                        np.array([['X', ' ', ' '], ['X', ' ', ' '], ['X', ' ', ' ']]),
                        np.array([[' ', 'X', ' '], [' ', 'X', ' '], [' ', 'X', ' ']]),
                        np.array([[' ', ' ', 'X'], [' ', ' ', 'X'], [' ', ' ', 'X']]),
                        np.array([['X', ' ', ' '], [' ', 'X', ' '], [' ', ' ', 'X']]),
                        np.array([[' ', ' ', 'X'], [' ', 'X', ' '], ['X', ' ', ' ']])]

        o_win_boards = [np.array([['O', 'O', 'O'], [' ', ' ', ' '], [' ', ' ', ' ']]),
                        np.array([[' ', ' ', ' '], ['O', 'O', 'O'], [' ', ' ', ' ']]),
                        np.array([[' ', ' ', ' '], [' ', ' ', ' '], ['O', 'O', 'O']]),
                        np.array([['O', ' ', ' '], ['O', ' ', ' '], ['O', ' ', ' ']]),
                        np.array([[' ', 'O', ' '], [' ', 'O', ' '], [' ', 'O', ' ']]),
                        np.array([[' ', ' ', 'O'], [' ', ' ', 'O'], [' ', ' ', 'O']]),
                        np.array([['O', ' ', ' '], [' ', 'O', ' '], [' ', ' ', 'O']]),
                        np.array([[' ', ' ', 'O'], [' ', 'O', ' '], ['O', ' ', ' ']])]
        for i in range(8):
            _, x_winner = naught_util.check_winner(x_win_boards[i])
            self.assertEqual(x_winner, 'X')
            _, o_winner = naught_util.check_winner(o_win_boards[i])
            self.assertEqual(o_winner, 'O')

    def test_get_empty_char_board(self):
        self.assertTrue(np.array_equal(empty_nc_board, naught_util.get_empty_char_board()))
        self.assertTrue(np.array_equal(np.full((3, 3), ' '), naught_util.get_empty_char_board()))

    def test_get_empty_i1_board(self):
        self.assertTrue(np.array_equal(np.zeros((3, 3), dtype='i1'), naught_util.get_empty_i1_board()))

    def test_i1_to__char(self):
        i1_board = np.array([[1, 1, 1], [-1, -1, 0], [0, 0, 0]], dtype='i1')
        char_board = np.array([['X', 'X', 'X'], ['O', 'O', ' '], [' ', ' ', ' ']])
        self.assertTrue(np.array_equal(char_board, naught_util.i1_to_char_board(i1_board)))

    def test_char_to_i1(self):
        i1_board = np.array([[1, 1, 1], [-1, -1, 0], [0, 0, 0]], dtype='i1')
        char_board = np.array([['X', 'X', 'X'], ['O', 'O', ' '], [' ', ' ', ' ']])
        self.assertTrue(np.array_equal(i1_board, naught_util.char_to_i1_board(char_board)))

    def test_find_winner_i1_board(self):
        has_ended, winner = naught_util.check_winner(naught_util.char_to_i1_board(x_win_nc_board))
        self.assertTrue(has_ended)
        self.assertEqual(winner, 1)


# class TestTree(unittest.TestCase):
#
#     def test1(self):
#         self.assertTrue(False, "NO TESTS FOR NODE IMPLEMENTED")


class TestDeterministicAI(unittest.TestCase):
    skip = True
    if not skip:
        full_tree = ai_strats._build_state_tree(NaughtAI(NaughtCross()))  # NaughtAI(NaughtCross()).build_state_tree()
        full_tree_min_maxed = ai_strats._min_max_tree(NaughtAI(NaughtCross()), copy.deepcopy(full_tree))
        level_counts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # end_states = 0
    @unittest.skipIf(skip, "Building trees takes to fucking long")
    def setUp(self):
        self.ai = NaughtAI(NaughtCross(starting_player='X'))

    def test_player_default(self):
        self.assertEqual('X', self.ai.player)

    def test_player(self):
        ai = NaughtAI(NaughtCross(), player='X')
        ai2 = NaughtAI(NaughtCross(), player='O')
        self.assertEqual(ai.player, 'X')
        self.assertEqual(ai2.player, 'O')

        self.assertRaises(ValueError, NaughtAI, NaughtCross(), "Trololo")

    def test_evaluate_board(self):
        score = self.ai.score_board(board=x_win_nc_board)
        self.assertEqual(score, 1)
        score = self.ai.score_board(board=o_win_nc_board)
        self.assertEqual(score, -1)
        score = self.ai.score_board(board=empty_nc_board)
        self.assertEqual(score, None)
        score = self.ai.score_board(board=stale_mate_nc_board)
        self.assertEqual(score, 0)
        score = self.ai.score_board(board=not_finished_nc_board1)
        self.assertEqual(score, None)

    def test_build_state_tree(self):
        self.rec_test_build_state_tree(self.full_tree, 0)
        self.assertTrue(self.level_counts == [1, 9, 72, 504, 3024, 15120, 54720, 148176, 200448, 127872])

    def rec_test_build_state_tree(self, node, level):
        children_len = len(node.children)
        self.level_counts[level] = self.level_counts[level] + 1
        board_sum = np.sum(node.board)
        self.assertTrue(board_sum >= 0, str(board_sum))
        self.assertTrue(board_sum <= 1, str(board_sum))
        if level < 5:
            self.assertEqual(children_len, 9 - level)
        else:
            self.assertLessEqual(children_len, 9 - level)
        if children_len == 0:
            won, winner = naught_util.check_winner(node.board)
            self.assertTrue(won, "failed with winner: " + str(winner))
        #     # self.assertGreaterEqual(node.score, -1)
        # else:
        #     self.assertEqual(node.score, None)
        if level > 0:
            self.assertIsNotNone(node.move_from_parent[0])
        # for i in range(children_len):
        for child in node.children:
            self.rec_test_build_state_tree(child, level + 1)

    def test_min_max_tree(self):
        root = self.get_small_test_tree()

        ai_strats._min_max_tree(self.ai, root, is_my_turn=True)
        self.assertEqual(root.score, 0)
        self.assertEqual(root.children[0].score, 0)
        self.assertEqual(root.best_child, 0)

        root = self.get_small_test_tree()

        ai_strats._min_max_tree(self.ai, root, is_my_turn=False)
        self.assertEqual(root.score, -1)
        self.assertEqual(root.children[0].score, 1)
        self.assertEqual(root.best_child, 1)

    def test_make_next_move(self):
        self.ai.tree = self.full_tree_min_maxed
        # self.ai.best_moves = self.ai.find_best_moves(root=self.full_tree_min_maxed, is_my_turn=True)
        nc = self.ai.nc
        success, move, msg = self.ai.make_move()
        # print(success)
        self.assertTrue(success, "failed with msg: " + msg)
        # print("\n\n ", nc.board[move[0]], "\n\n")
        self.assertEqual(nc.board[move[0]], 'X')

    def test_moves(self):
        nc = NaughtCross()
        ai_x = NaughtAI(nc, player='X')
        ai_o = NaughtAI(nc, player='O')
        success, move, msg = ai_o.make_move()
        self.assertFalse(success, "Illegal move allowed. move: " + str(move))
        # naught_util.print_board(nc.board)
        success, move, msg = ai_x.make_move()
        self.assertTrue(success)
        # naught_util.print_board(nc.board)
        success, move, msg = ai_o.make_move()
        self.assertTrue(success)
        self.assertEqual(msg, "Move performed")
        # naught_util.print_board(nc.board)
        success, move, msg = ai_x.make_move()
        self.assertTrue(success)
        self.assertEqual(msg, "Move performed")
        # naught_util.print_board(nc.board)
        success, move, msg = ai_x.make_move()
        self.assertFalse(success)
        # naught_util.print_board(nc.board)

    def test_inform_opponent_move(self):
        self.ai.tree = self.full_tree_min_maxed
        # self.ai.best_moves = self.ai.find_best_moves(root=self.full_tree_min_maxed, is_my_turn=True)
        nc = self.ai.nc
        self.ai.make_move()
        success, msg = nc.make_move((1, 1), 'O')
        # print(msg)
        success, msg = self.ai.inform_opponent_move((1, 1))
        # print(msg)
        self.assertTrue(success)
        self.assertEqual(msg, "Success")
        success, move, msg = self.ai.make_move()
        self.assertTrue(success, "legal move disallowed. move = " + str(move))
        self.assertEqual(msg, "Move performed")
        self.assertTrue(np.array_equal(naught_util.char_to_i1_board(nc.board), self.ai.expected_board),
                        "Failed the expected stuff")

    def test_o_ai(self):
        nc = NaughtCross()
        ai_o = NaughtAI(nc, player='O')
        success, move, msg = ai_o.make_move()
        self.assertFalse(success, msg)
        success, msg = nc.make_move((0, 0), 'X')
        self.assertTrue(success, msg)
        # ai_o.reset_ai_state()
        ai_strats._build_state_tree(ai_o)
        ai_strats._min_max_tree(ai_o, ai_o.tree, True)
        tree = ai_o.tree
        self.assertIsNotNone(tree)
        self.traverse_tree_for_o_ai(tree, 8)

    def traverse_tree_for_o_ai(self, node, level):
        children = node.children
        # self.assertGreaterEqual(8-level, len(children))
        board_sum = np.sum(node.board)
        self.assertTrue(board_sum >= 0, str(board_sum))
        self.assertTrue(board_sum <= 1, str(board_sum))
        for i in range(len(children)):
            self.traverse_tree_for_o_ai(children[i], level + 1)

    @staticmethod
    def get_small_test_tree():
        root = Node()
        root.children.append(Node())
        root.children.append(Node(board=naught_util.char_to_i1_board(o_win_nc_board), move=(None, -1)))
        root.children[0].children.append(Node(board=naught_util.char_to_i1_board(stale_mate_nc_board), move=(None, -1)))
        root.children[0].children.append(Node(board=naught_util.char_to_i1_board(x_win_nc_board), move=(None, 1)))
        return root


class TestRandomAi(unittest.TestCase):
    def setUp(self):
        self.nc = NaughtCross(starting_player='X')
        self.ai = NaughtAI(self.nc, strat="random")

    def test_make_random_move(self):
        success = self.ai.make_move()
        self.assertTrue(success)
        count_x = 0
        count_o = 0
        for r in self.nc.board:
            for i in r:
                if i == 'X':
                    count_x = count_x + 1
                elif i == 'O':
                    count_o = count_o + 1

        self.assertEqual(count_x, 1)
        self.assertEqual(count_o, 0)

    def test_inform_no_update(self):
        success, msg = self.ai.inform_opponent_move((0, 1))
        self.assertTrue(success)
        self.assertEqual(msg, "No update for this strategy")


class TestNNAi(unittest.TestCase):
    def setUp(self):
        self.nc = NaughtCross(starting_player='X')
        self.ai = NaughtAI(self.nc, strat="nn")

    def test_make_nn_move(self):
        success = self.ai.make_move()
        self.assertTrue(success)
        count_x = 0
        count_o = 0
        for r in self.nc.board:
            for i in r:
                if i == 'X':
                    count_x = count_x + 1
                elif i == 'O':
                    count_o = count_o + 1

        self.assertEqual(count_x, 1)
        self.assertEqual(count_o, 0)

    def test_game(self):
        nc = NaughtCross(starting_player='X')
        ai_x = NaughtAI(nc, player='X', strat="nn")
        ai_o = NaughtAI(nc, player='O', strat="nn")

        ongoing = True
        while ongoing:
            success, _,  msg = ai_x.make_move()
            if not success:
                print(msg)
            success, _, msg = ai_o.make_move()
            if not success:
                print(msg)
            ongoing = nc.game_in_progress
        self.assertFalse(ongoing)


class TestNNUtil(unittest.TestCase):
    def test_relu(self):
        X = np.array([-2.0, 4, 3])
        self.assertTrue(np.array_equal(np.array([0, 4.0, 3.0]), nn_util.relu(X)),
                        msg='relu([-2, 4, 3]) = ' + str(nn_util.relu(X)) + ', should be [0, 4, 3]')

    def test_d_relu(self):
        X = np.array([-2.0, 4, 3])
        self.assertTrue(np.array_equal(np.array([0, 1, 1]), nn_util.d_relu(X)),
                        msg='d_relu([-2, 4, 3]) = ' + str(nn_util.relu(X)) + ', should be [0, 1, 1]')

    def test_sigmoid(self):
        self.assertEqual(nn_util.tanh(0), 0)
        self.assertEqual(nn_util.tanh(np.array([0])), np.array([0]))
        self.assertLessEqual(nn_util.tanh(2), 0.965)
        self.assertGreaterEqual(nn_util.tanh(2), 0.964)

    def test_d_sigmoid(self):
        self.assertEqual(nn_util.d_tanh(0), 1)
        self.assertLess(nn_util.d_tanh(-20), 1e-8)
        self.assertLess(nn_util.d_tanh(20), 1e-8)

    def test_cross_entropy(self):
        self.assertEqual(np.log(.6), nn_util.cross_entropy(.4, 0))
        self.assertEqual(np.log(.4), nn_util.cross_entropy(.4, 1))

    def test_cross_entropy_error1(self):
        self.assertRaises(ValueError, nn_util.cross_entropy, 0, .5)

    def test_mse(self):
        self.assertEqual(np.square(2), nn_util.mse(1, 3))


class TestNN(unittest.TestCase):
    def setUp(self):
        self.nn = NN()

    def test_basic(self):
        self.assertEqual(self.nn.W, [])
        self.assertEqual(self.nn.b, [])

    def test_init(self):
        self.nn.init_net(input_size=7, output_size=1, hidden_size=3, number_of_hidden=4)
        w = self.nn.W
        b = self.nn.b
        self.assertEqual(len(w), 5)
        self.assertEqual(len(b), 5)
        self.assertEqual(w[0].shape, (7, 3))
        self.assertEqual(w[1].shape, (3, 3))
        self.assertEqual(w[4].shape, (3, 1))
        self.assertEqual(len(b[0]), 3)
        self.assertEqual(len(b[4]), 1)

    def test_predict(self):
        nn = self.get_simple_nn()
        a = nn.predict(np.array([3, -2]))
        aL = a[0]
        self.assertLessEqual(aL, 0.999)
        self.assertGreaterEqual(aL, 0.9987)

    def test_forward_for_error(self):
        self.nn.init_net(input_size=2, output_size=1, hidden_size=3, number_of_hidden=4)
        _ = self.nn.forward_pass(np.array([2, 3]))

    def test_forward_pass(self):
        nn = self.get_simple_nn()
        z, a = nn.forward_pass(np.array([3, -2]))
        zL = z[-1]
        aL = a[-1]
        self.assertEqual(zL, 3.7)
        self.assertLessEqual(aL, 0.999)
        self.assertGreaterEqual(aL, 0.99877)

    # @unittest.skip("Backprop not implemented yet")
    def test_back_prop_error(self):
        nn = self.get_simple_nn2()
        cost, grad_dist = nn.cost_grad(np.array([3, -2]), np.array([1]))
        out_error = grad_dist['db'][-1][0]
        self.assertEqual(out_error, 1)

    def test_back_prop_error2(self):
        nn = NN()
        nn.init_net(input_size=3, output_size=1, hidden_size=8, number_of_hidden=5)
        _ = nn.cost_grad(np.array([-2, 3, 1]), np.array([1]))
        #  Simply testing for shape errors

    @unittest.skip("Skipped because it fails sometimes")
    def test_update_from_gradients(self):
        nn = NN()
        nn.init_net(input_size=3, output_size=1, hidden_size=8, number_of_hidden=5)
        cost, grads = nn.cost_grad([-2, 3, 1], np.array([1]))
        nn.update_from_gradients(grads['db'], grads['dw'])
        cost2, grads2 = nn.cost_grad([-2, 3, 1], np.array([1]))
        self.assertLess(cost2, cost, "This one fails sometimes for some reason. Try retesting")

    def get_simple_nn(self):
        nn = NN()
        w1 = np.array([[2, -1], [1, 1]])
        w2 = np.array([[1], [2]])
        w = [w1, w2]
        nn.W = w
        b1 = np.array([-.5, .1])
        b2 = np.array([.2])
        nn.b = [b1, b2]
        nn.depth = 3
        return nn

    def get_simple_nn2(self):
        nn = NN()
        w1 = np.array([[1, 2], [2, 3]])
        w2 = np.array([[1], [-1]])
        w = [w1, w2]
        nn.W = w
        b1 = np.array([0, 0])
        b2 = np.array([0])
        nn.b = [b1, b2]
        nn.depth = 3
        return nn


class TestChess(unittest.TestCase):
    def setUp(self):
        self.chess = Chess()
        self.no_pawn_chess = Chess()
        no_pawn_board = chess_util.get_start_board()
        no_pawn_board[1] = np.zeros(8, dtype='i1')
        no_pawn_board[6] = np.zeros(8, dtype='i1')
        self.no_pawn_chess.board = no_pawn_board
        self.empty_chess = Chess()
        self.empty_chess.board = chess_util.get_empty_board()

    def test_start_board(self):
        self.assertTrue(np.array_equal(self.chess.board, chess_util.get_start_board()))

    def test_not_in_turn_move(self):
        success, _ = self.chess.move(Move((6, 0), (5, 0)))
        self.assertFalse(success)
        self.chess.move(Move((1, 0), (2, 0)))
        success, _ = self.chess.move(Move((1, 1), (2, 1)))
        self.assertFalse(success)

    def test_illegal_move_to_own(self):
        board = chess_util.get_empty_board()
        board[0, 0] = 1
        board[1, 0] = 3
        chess = Chess()
        chess.board = board
        success, _ = chess.move(Move((0, 0), (0, 1)))
        self.assertFalse(success)
        self.assertEqual(chess.board[0, 0], 1)
        self.assertEqual(chess.board[1, 0], 3)

    # Pawn tests beneath
    def test_white_pawn_move(self):
        success, msg = self.chess.move(Move((1, 0), (2, 0)))
        self.assertTrue(success, msg)
        self.assertEqual(self.chess.board[1, 0], 0)
        self.assertEqual(self.chess.board[2, 0], 1)

    def test_black_pawn_move(self):
        self.chess.move(Move((1, 0), (2, 0)))
        success, msg = self.chess.move(Move((6, 3), (5, 3)))
        self.assertTrue(success, msg)
        self.assertEqual(self.chess.board[6, 3], 0)
        self.assertEqual(self.chess.board[5, 3], -1)

    def test_pawn_double(self):
        # chess_util.print_board(self.chess.board)
        # print("legal moves:")
        # print(self.chess.legal_moves)
        success, msg = self.chess.move(Move((1, 2), (3, 2)))
        # chess_util.print_board(self.chess.board)
        # print("legal moves:")
        # print(self.chess.legal_moves)
        self.assertTrue(success, msg)
        success, msg = self.chess.move(Move((6, 2), (4, 2)))
        # chess_util.print_board(self.chess.board)
        # print("legal moves:")
        # print(self.chess.legal_moves)
        # print(self.chess.winner)
        self.assertTrue(success, msg)

    def test_illegal_white_pawn_move(self):
        success, _ = self.chess.move(Move((1, 0), (4, 2)))
        self.assertFalse(success)

    def test_illegal_black_pawn_move(self):
        self.chess.in_turn = -1
        success, msg = self.chess.move(Move((6, 2), (3, 2)))
        self.assertFalse(success)
        self.assertEqual(msg, "Illegal pawn move")
        success, msg = self.chess.move(Move((6, 7), (5, 6)))
        self.assertFalse(success)
        self.assertEqual(msg, "Illegal pawn move")
        success, msg = self.chess.move(Move((6, 3), (3, 2)))
        self.assertFalse(success)
        self.assertEqual(msg, "Illegal pawn move")
        success, msg = self.chess.move(Move((6, 2), (3, 2)))
        self.assertFalse(success)
        self.assertEqual(msg, "Illegal pawn move")

    def test_backwards_pawn_move(self):
        self.chess.board = chess_util.get_empty_board()
        self.chess.board[3, 3] = 1
        self.chess.board[5, 4] = -1
        success, msg = self.chess.move(Move((3, 3), (2, 3)))
        self.assertFalse(success)
        self.assertEqual(msg, "Illegal pawn move")
        self.chess.in_turn = -1
        success, msg = self.chess.move(Move((5, 4), (5, 4)))
        self.assertFalse(success)
        self.assertEqual(msg, "Illegal move; trying to move to own piece")

    def test_pawn_attack(self):
        self.chess.board = chess_util.get_empty_board()
        self.chess.board[2, 3] = 1
        self.chess.board[3, 4] = -1
        success, msg = self.chess.move(Move((2, 3), (3, 4)))
        self.assertTrue(success, "failed with msg: " + msg)
        self.assertEqual(self.chess.board[2, 3], 0)
        self.assertEqual(self.chess.board[3, 4], 1)

    def test_pawn_illegal_2move(self):
        self.chess.board = chess_util.get_empty_board()
        self.chess.board[3, 3] = 1
        success, msg = self.chess.move(Move((3, 3), (5, 3)))
        self.assertFalse(success, "failed with msg: " + msg)
        self.chess.board[5, 7] = -1
        self.chess.in_turn = -1
        success, msg = self.chess.move(Move((5, 3), (3, 7)))
        self.assertFalse(success)

    def test_pawn_illegal_2move_blocked(self):
        self.chess.board[2, 1] = 1
        success, msg = self.chess.move(Move((1, 1), (3, 1)))
        self.assertFalse(success, "failed with msg: " + msg)
        self.chess.board[3, 3] = -1
        success, msg = self.chess.move(Move((1, 3), (3, 3)))
        self.assertFalse(success)

    # Test Knights beneath
    def test_white_knight_move(self):
        success, msg = self.chess.move(Move((0, 1), (2, 0)))
        self.assertTrue(success, msg)
        self.assertEqual(self.chess.board[0, 1], 0)
        self.assertEqual(self.chess.board[2, 0], 3)

    def test_black_knight_move(self):
        self.chess.move(Move((1, 0), (2, 0)))
        success, msg = self.chess.move(Move((7, 1), (5, 0)))
        self.assertTrue(success, msg)
        self.assertEqual(self.chess.board[7, 1], 0)
        self.assertEqual(self.chess.board[5, 0], -3)

    def test_illegal_knight_moves(self):
        self.empty_chess.board[3, 3] = 3
        test_moves = [(4, 3), (3, 4), (4, 4), (5, 3), (5, 5), (2, 2), (0, 0), (7, 7)]
        for move in test_moves:
            success, _ = self.empty_chess.move(Move((3, 3), move))
            self.assertFalse(success)

    def test_knight_move_outside_board(self):
        self.empty_chess.board[0, 7] = 3
        self.empty_chess.board[7, 7] = 3
        self.empty_chess.board[0, 0] = 3
        self.empty_chess.board[7, 0] = 3
        success, msg = self.empty_chess.move(Move((0, 7), (2, 8)))
        self.assertFalse(success, msg)
        self.assertEqual(msg, "\"to\" pos outside board")
        success, msg = self.empty_chess.move(Move((7, 7), (9, 6)))
        self.assertFalse(success, msg)
        self.assertEqual(msg, "\"to\" pos outside board")
        success, msg = self.empty_chess.move(Move((7, 0), (5, -1)))
        self.assertFalse(success, msg)
        self.assertEqual(msg, "\"to\" pos outside board")
        success, msg = self.empty_chess.move(Move((0, 0), (-2, -1)))
        self.assertFalse(success, msg)
        self.assertEqual(msg, "\"to\" pos outside board")
        success, msg = self.empty_chess.move(Move((8, 0), (5, -1)))
        self.assertFalse(success, msg)
        self.assertEqual(msg, "\"frm\" pos outside board")

    def test_knight_attack(self):
        self.empty_chess.board[1, 2] = 3
        self.empty_chess.board[0, 0] = -1
        success, msg = self.empty_chess.move(Move((1, 2), (0, 0)))
        self.assertTrue(success, msg)
        self.assertEqual(self.empty_chess.board[1, 2], 0, "knight still at start pos")
        self.assertEqual(self.empty_chess.board[0, 0], 3, "knight not at end pos")

    # Test Rook
    def test_bishop_move_legal(self):
        self.empty_chess.board[1, 1] = 4  # Rook = 2
        self.empty_chess.board[7, 7] = -4  # enemy rook, to prevent game ending
        success, msg = self.empty_chess.move(Move((1, 1), (2, 2)))
        self.assertTrue(success, "failed with msg: " + msg)
        self.empty_chess.in_turn = 1
        success, msg = self.empty_chess.move(Move((2, 2), (6, 6)))
        self.assertTrue(success)
        self.empty_chess.in_turn = 1
        success, msg = self.empty_chess.move(Move((6, 6), (5, 7)))
        self.assertTrue(success)
        self.empty_chess.in_turn = 1
        success, msg = self.empty_chess.move(Move((5, 7), (1, 3)))
        self.assertTrue(success)

    def test_rook_bishop_move(self):
        self.empty_chess.board[2, 2] = -4
        self.empty_chess.in_turn = -1
        success, msg = self.empty_chess.move(Move((2, 2), (4, 2)))
        self.assertFalse(success, "failed with msg: " + msg)
        self.empty_chess.board[3, 3] = 1
        success, msg = self.empty_chess.move(Move((2, 2), (4, 4)))
        self.assertFalse(success)

    # Test Bishop
    def test_rook_legal_move(self):
        self.empty_chess.board[1, 1] = 2  # Bishop = 4
        self.empty_chess.board[7, 7] = -1  # enemy piece to prevent game ending
        success, msg = self.empty_chess.move(Move((1, 1), (1, 2)))
        self.assertTrue(success, "failed with msg: " + msg)
        self.empty_chess.in_turn = 1
        success, msg = self.empty_chess.move(Move((1, 2), (1, 5)))
        self.assertTrue(success)
        self.empty_chess.in_turn = 1
        success, msg = self.empty_chess.move(Move((1, 5), (5, 5)))
        self.assertTrue(success)
        self.empty_chess.in_turn = 1
        success, msg = self.empty_chess.move(Move((5, 5), (2, 5)))
        self.assertTrue(success)

    def test_rook_illegal_move(self):
        self.empty_chess.board[2, 2] = -2
        self.empty_chess.in_turn = -1
        success, msg = self.empty_chess.move(Move((2, 2), (4, 3)))
        self.assertFalse(success, "failed with msg: " + msg)
        self.empty_chess.board[2, 4] = 1
        success, msg = self.empty_chess.move(Move((2, 2), (2, 5)))
        self.assertFalse(success)

    # Test Queen
    def test_queen_legal(self):
        self.empty_chess.board[2, 3] = -10
        self.empty_chess.board[7, 7] = 10  # enemy piece to prevent game ending
        self.empty_chess.in_turn = -1
        success, msg = self.empty_chess.move(Move((2, 3), (5, 3)))
        self.assertTrue(success, "failed with msg: " + msg)
        self.empty_chess.in_turn = -1
        success, msg = self.empty_chess.move(Move((5, 3), (3, 1)))
        self.assertTrue(success)

    def test_queen_illegal(self):
        self.empty_chess.board[2, 3] = 10
        success, msg = self.empty_chess.move(Move((2, 3), (5, 4)))
        self.assertFalse(success, "failed with msg: " + msg)
        self.empty_chess.board[2, 5] = -3
        success, msg = self.empty_chess.move(Move((2, 3), (2, 6)))
        self.assertFalse(success)

    # Test King
    def test_king_legal(self):
        self.empty_chess.board[2, 3] = -100
        self.empty_chess.board[1, 7] = 1  # enemy piece to prevent game ending
        self.empty_chess.in_turn = -1
        success, msg = self.empty_chess.move(Move((2, 3), (3, 3)))
        self.assertTrue(success, "failed with msg: " + msg)
        self.empty_chess.in_turn = -1
        success, msg = self.empty_chess.move(Move((3, 3), (2, 2)))
        self.assertTrue(success)

    def test_king_illegal(self):
        self.empty_chess.board[2, 3] = 100
        success, msg = self.empty_chess.move(Move((2, 3), (5, 4)))
        self.assertFalse(success, "failed with msg: " + msg)
        success, msg = self.empty_chess.move(Move((2, 3), (2, 5)))
        self.assertFalse(success)

    # Test check
    def test_illegal_to_own_check_move(self):
        self.empty_chess.board[1, 0] = 100
        self.empty_chess.board[1, 1] = 1
        self.empty_chess.board[1, 7] = -10
        success, msg = self.empty_chess.move(Move((1, 1), (2, 1)))
        self.assertFalse(success, "failed with msg: " + msg)

    def test_illegal_in_check_move(self):
        self.empty_chess.board[1, 0] = 100
        self.empty_chess.board[0, 1] = 1
        self.empty_chess.board[1, 7] = -10
        success, msg = self.empty_chess.move(Move((1, 1), (2, 1)))
        self.assertFalse(success, "failed with msg: " + msg)

    # Test check mate
    def test_check_mate(self):
        self.empty_chess.board[0, 0] = -100
        self.empty_chess.board[1, 7] = 10
        self.empty_chess.board[2, 6] = 10
        in_progress = self.empty_chess.is_in_progress
        winner = self.empty_chess.winner
        self.assertTrue(in_progress)
        self.assertIsNone(winner)
        success, msg = self.empty_chess.move(Move((2, 6), (0, 6)))
        self.assertTrue(success, "failed with msg: " + msg)
        in_progress = self.empty_chess.is_in_progress
        winner = self.empty_chess.winner
        self.assertFalse(in_progress)
        self.assertEqual(winner, 1)

    # Test Get legal moves
    def test_get_legal_pawn_moves(self):
        self.empty_chess.board[2, 0] = 1
        moves_list = chess.get_legal_moves(self.empty_chess.board, 1)
        self.assertEqual(len(moves_list), 1)
        self.assertEqual(moves_list[0], ((2, 0), (3, 0)))

    def test_get_legal_pawn_moves_attack_double(self):
        self.empty_chess.board[6, 2] = -1
        self.empty_chess.board[5, 1] = 1
        moves_list = sorted(chess.get_legal_moves(self.empty_chess.board, -1))
        self.assertEqual(len(moves_list), 3)
        real_move_list = sorted([((6, 2), (5, 1)), ((6, 2), (5, 2)), ((6, 2), (4, 2))])
        self.assertTrue(moves_list == real_move_list, "Wrong move list: " + str(moves_list) + " != " + str(real_move_list))

    # def test_get_legal_pawn_moves_promotion(self):
    #     self.empty_chess.board[6, 1] = 1
    #     self.empty_chess.board[7, 2] = -1
    #     moves_list = sorted(chess.get_legal_moves(self.empty_chess.board, 1))
    #     real_move_list = sorted([((6, 2), (5, 1)), ((6, 2), (5, 2)), ((6, 2), (4, 2))])

    def test_get_legal_knight_moves(self):
        self.empty_chess.board[3, 3] = 3
        self.empty_chess.board[2, 1] = 1
        self.empty_chess.board[4, 5] = -1
        moves_list = sorted(chess.get_legal_moves(self.empty_chess.board, 1))
        real_move_list = sorted([((2, 1), (3, 1)),
                                 ((3, 3), (4, 5)),
                                 ((3, 3), (5, 4)),
                                 ((3, 3), (5, 2)),
                                 ((3, 3), (4, 1)),
                                 ((3, 3), (1, 2)),
                                 ((3, 3), (1, 4)),
                                 ((3, 3), (2, 5))])
        self.assertTrue(moves_list == real_move_list, "Wrong move list: " + str(moves_list) + " != " + str(real_move_list))

    def test_get_legal_rook_moves(self):
        self.empty_chess.board[0, 2] = 2
        self.empty_chess.board[2, 2] = 1
        self.empty_chess.board[0, 3] = -1
        moves_list = sorted(chess.get_legal_moves(self.empty_chess.board, 1))
        real_move_list = sorted([((0, 2), (1, 2)),
                                 ((0, 2), (0, 3)),
                                 ((0, 2), (0, 1)),
                                 ((0, 2), (0, 0)),
                                 ((2, 2), (3, 2))])
        self.assertTrue(moves_list == real_move_list, "Wrong move list: " + str(moves_list) + " != " + str(real_move_list))

    def test_get_legal_bishop_moves(self):
        self.empty_chess.board[0, 2] = 4
        self.empty_chess.board[2, 0] = 1
        self.empty_chess.board[2, 4] = -1
        moves_list = sorted(chess.get_legal_moves(self.empty_chess.board, 1))
        real_move_list = sorted([((2, 0), (3, 0)),
                                 ((0, 2), (1, 1)),
                                 ((0, 2), (1, 3)),
                                 ((0, 2), (2, 4))])
        self.assertTrue(moves_list == real_move_list, "Wrong move list: " + str(moves_list) + " != " + str(real_move_list))

    def test_get_legal_queen_moves(self):
        self.empty_chess.board[0, 2] = 10
        self.empty_chess.board[2, 0] = 1
        self.empty_chess.board[1, 2] = -1
        self.empty_chess.board[2, 4] = -1
        self.empty_chess.board[0, 3] = -4
        moves_list = sorted(chess.get_legal_moves(self.empty_chess.board, 1))
        real_move_list = sorted([((2, 0), (3, 0)),
                                 ((0, 2), (1, 2)),
                                 ((0, 2), (1, 3)),
                                 ((0, 2), (2, 4)),
                                 ((0, 2), (0, 3)),
                                 ((0, 2), (0, 1)),
                                 ((0, 2), (0, 0)),
                                 ((0, 2), (1, 1))])
        self.assertTrue(moves_list == real_move_list, "Wrong move list: " + str(moves_list) + " != " + str(real_move_list))

    def test_get_legal_king_moves(self):
        self.empty_chess.board[0, 2] = 100
        self.empty_chess.board[0, 3] = -1
        self.empty_chess.board[1, 3] = 1
        moves_list = sorted(chess.get_legal_moves(self.empty_chess.board, 1))
        real_move_list = sorted([((1, 3), (2, 3)),
                                 ((1, 3), (3, 3)),
                                 ((0, 2), (1, 2)),
                                 ((0, 2), (0, 3)),
                                 ((0, 2), (1, 1)),
                                 ((0, 2), (0, 1))])
        self.assertTrue(moves_list == real_move_list, "Wrong move list: " + str(moves_list) + " != " + str(real_move_list))

    def test_get_legal_moves_check_stuff(self):
        self.empty_chess.board[1, 0] = 100
        self.empty_chess.board[1, 1] = 1
        self.empty_chess.board[0, 7] = -2
        self.empty_chess.board[1, 7] = -2
        moves_list = sorted(chess.get_legal_moves(self.empty_chess.board, 1))
        real_move_list = sorted([((1, 0), (2, 0)),
                                 ((1, 0), (2, 1))])
        self.assertTrue(moves_list == real_move_list,
                        "Wrong move list: " + str(moves_list) + " != " + str(real_move_list))

    def test_promote_to_queen(self):
        self.empty_chess.board[6, 0] = 1
        self.empty_chess.board[0, 7] = -2
        self.empty_chess.move(Move((6, 0), (7, 0), promote=10))
        self.assertEqual(10, self.empty_chess.board[7, 0])

    def test_promote_to_rook(self):
        self.empty_chess.board[6, 0] = 1
        self.empty_chess.board[0, 7] = -2
        self.empty_chess.move(Move((6, 0), (7, 0), promote=2))
        self.assertEqual(2, self.empty_chess.board[7, 0])

    def test_promote_to_knight(self):
        self.empty_chess.board[6, 0] = 1
        self.empty_chess.board[0, 7] = -2
        self.empty_chess.move(Move((6, 0), (7, 0), promote=3))
        self.assertEqual(3, self.empty_chess.board[7, 0])

    def test_promote_to_bishop(self):
        self.empty_chess.board[6, 0] = 1
        self.empty_chess.board[0, 7] = -2
        self.empty_chess.move(Move((6, 0), (7, 0), promote=4))
        self.assertEqual(4, self.empty_chess.board[7, 0])

    def test_promotion_black(self):
        self.empty_chess.board[1, 0] = -1
        self.empty_chess.board[6, 7] = 2
        self.empty_chess.in_turn = -1
        self.empty_chess.move(Move((1, 0), (0, 0), promote=10))
        self.assertEqual(-10, self.empty_chess.board[0, 0])

    def test_illegal_promotion(self):
        self.empty_chess.board[6, 0] = 1
        success, _ = self.empty_chess.move(Move((6, 0), (7, 0)))
        self.assertFalse(success, "Promotion move allowed without promotion argument")


    # TODO Castling
    # TODO Other weird move - En Passent
    # TODO Pawn Promotion
    # TODO Draw rules


if __name__ == '__main__':  # Does not work from PyCharm python console. Use terminal
    unittest.main()
    # chess = Chess()
    # chess_util.print_board(chess.board)
    # print(chess.board[0, 0])
    # print(u'\u2654')
