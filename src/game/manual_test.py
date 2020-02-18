from chess.chess import Chess
from chess.chess import Move
# from ai.tree import Node
import ai.chess_ai as chess_ai
import time


def test_ab_prune_speed():
    chess = Chess()
    succes, msg = chess.move(chess.legal_moves[0])
    print(succes, msg)
    # print(len(chess.legal_moves))
    depth = 4

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
    for key in time_dict:
        time_dict[key] = (time_dict[key] / total) * 100
    print(time_dict)


if __name__ == "__main__":
    test_chess_move_speed()



# {'start': 0.026508933041276782, 
#  'is_legal': 0.1535875970098009, 
#  'copy': 0.10946078015084489, 
#  'mid1': 0.05928148123469133, 
#  'castleEnPassantCheck': 0.026673147670655928, 
#  'is_in_check1': 4.029522036899484, 
#  'get_legal_moves': 91.49283766164004, 
#  'is_in_check2': 4.102128362353205}