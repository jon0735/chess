from chess.chess import Chess
from chess.chess import Move
# from ai.tree import Node
import ai.chess_ai as chess_ai
import time
import chess.chess as chess_f
import chess.chess_util as chess_util

import random


def test_ab_prune_speed(depth=4):
    chess = Chess()
    succes, msg = chess.move(chess.legal_moves[0])
    print(succes, msg)
    # print(len(chess.legal_moves))
    # depth = 4

    start_time = time.time()
    move, root, time_dict = chess_ai.choose_move_ab(chess, depth=depth, return_tree=True)
    end_time = time.time()

    move_choise_time = end_time - start_time
    print("Time for depth ", depth, ": ", move_choise_time)

    analysis_dict = {"count": 0, "branch": [[]]}

    chess_ai.count_tree_size(root, analysis_dict, 0)

    print("nodes visited: ", analysis_dict["count"])


    for level, l in enumerate(analysis_dict["branch"]):
        print("Branching factor at level ", level, ": ", sum(l)/len(l))

    print(time_dict)

def test_chess_move_speed():
    time_dict = {"start": 0, 
                 "is_legal": 0, 
                 "copy": 0, 
                 "mid1": 0, 
                 "castleEnPassantCheck": 0, 
                 "is_in_check1": 0, 
                 "get_legal_moves": 0, 
                 "is_in_check2": 0}
    chess = Chess()
    for i in range(35):
        # print(i)
        chess.move(chess.legal_moves[0], time_dict=time_dict)
    total = 0
    for key in time_dict:
        total += time_dict[key]
    print(total)
    print(time_dict)
    for key in time_dict:
        time_dict[key] = (time_dict[key] / total) * 100
    print(time_dict)

def test_get_legal_moves_speed():
    time_dict = {"generate": 0,
                 "copy": 0,
                 "validate": 0,
                 "special": 0,
                 "full": 0,}
    for _ in range(5):
        chess = Chess()
        while chess.is_in_progress:
            chess.move(chess.legal_moves[1])
            # chess.move(random.choice(chess.legal_moves))
            chess_f.get_legal_moves(chess, chess.in_turn, time_dict=time_dict)
    # for i in range(50):
    #     chess_f.get_legal_moves(chess, chess.in_turn, time_dict=time_dict)
    #     chess.move(chess.legal_moves[1])
    
    total = time_dict["full"]
    # for key in time_dict:
    #     total += time_dict[key]
    print("Total time: ", total, "\n")
    print(time_dict, "\n")
    for key in time_dict:
        time_dict[key] = (time_dict[key] / total) * 100
    print(time_dict) 


def test_get_nn_input():
    chess = Chess()
    x = chess_ai.chess_to_nn_input(chess)
    board = chess.board
    for r in range(8):
        for c in range(8):
            arr_start = ((r * 8) + c) * 6
            array_fraction = x[arr_start:arr_start + 6]
            char = chess_util.get_unicode_char(board[r, c])
            print(array_fraction, char)
    # for i, val in enumerate(x):
    #     if i % 6 == 0:
    #         print("\n")

    # print(x)


if __name__ == "__main__":
    test_get_nn_input()
    # test_get_legal_moves_speed()
    # test_chess_move_speed()
    # test_ab_prune_speed(depth=3)

# Run 1
# Total time:  0.8770021999999998

# {'generate': 0.2166567999999979, 'copy': 0.010461300000001866, 'validate': 0.6129167000000024, 'special': 0.007957800000000487, 'full': 0.8770021999999998}

# {'generate': 24.704248176344134, 'copy': 1.1928476348180048, 'validate': 69.88770381647875, 'special': 0.9073865493154395, 'full': 100.0}

# Run 2
# Total time:  0.9118039999999998

# {'generate': 0.22173269999999887, 'copy': 0.010081999999998675, 'validate': 0.6420636999999999, 'special': 0.008518199999999448, 'full': 0.9118039999999998}

# {'generate': 24.31802229426488, 'copy': 1.1057200889663432, 'validate': 70.41685493812267, 'special': 0.9342139319414534, 'full': 100.0}

#Run 3
# Total time:  0.9094088000000032

# {'generate': 0.22170130000000032, 'copy': 0.009853199999998286, 'validate': 0.640083399999998, 'special': 0.008208900000001823, 'full': 0.9094088000000032}

# {'generate': 24.378618284758137, 'copy': 1.0834731311153192, 'validate': 70.3845619263851, 'special': 0.9026633566776342, 'full': 100.0}

# Old
# relative (%)
# {'start': 0.026508933041276782, 
#  'is_legal': 0.1535875970098009, 
#  'copy': 0.10946078015084489, 
#  'mid1': 0.05928148123469133, 
#  'castleEnPassantCheck': 0.026673147670655928, 
#  'is_in_check1': 4.029522036899484, 
#  'get_legal_moves': 91.49283766164004, 
#  'is_in_check2': 4.102128362353205}

# {'start': 0.00010589999999990884, 
# 'is_legal': 0.0006041000000001628, 
# 'copy': 0.00032890000000013186, 
# 'mid1': 0.0002599000000001461, 
# 'castleEnPassantCheck': 8.999999999989572e-05, 
# 'is_in_check1': 0.017824599999999857, 
# 'get_legal_moves': 0.4014494999999999, 
# 'is_in_check2': 0.017032600000000175}

# New
# %
# {'start': 0.08975238338312, 
# 'is_legal': 0.7465186390389861, 
# 'copy': 0.3305099615575094, 
# 'mid1': 0.28786694528192774, 
# 'castleEnPassantCheck': 0.08411627399998778, 
# 'is_in_check1': 6.614771923668, 
# 'get_legal_moves': 85.10918632658576, 
# 'is_in_check2': 6.737277546484711}

# {'start': 8.440000000006775e-05, 
# 'is_legal': 0.0007019999999998972, 
# 'copy': 0.0003108000000000277, 
# 'mid1': 0.00027070000000004035, 
# 'castleEnPassantCheck': 7.909999999999862e-05, 
# 'is_in_check1': 0.0062203000000000674, 
# 'get_legal_moves': 0.08003369999999993, 
# 'is_in_check2': 0.006335500000000105}

# {'generate': 0.014822500000000016, 'copy': 0.0004522999999999888, 'validate': 0.024494300000000052, 'special': 0.0005140999999999063}
# {'generate': 36.79573618779052, 'copy': 1.1228005719505632, 'validate': 60.805248838225545, 'special': 1.2762144020333706}