from chess import Chess
from chess import Move
import json
import numpy as np
# from pandas import Series
import sys
import traceback

# print("MEHHHHHH")

start_chess = '{"board": [[2, 3, 4, 10, 100, 4, 3, 2], [1, 1, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [-1, -1, -1, -1, -1, -1, -1, -1], [-2, -3, -4, -10, -100, -4, -3, -2]], "in_turn": 1, "turn_num": 1, "is_in_progress": true, "winner": null, "legal_moves": [], "last_move": null, "legal_castles": {"(0, 2)": true, "(0, 6)": true, "(7, 2)": true, "(7, 6)": true} }'

def makeMove(chess_json, move, id):
    try:
        chess_dict = json.loads(chess_json)
        chess_dict['board'] = np.array(chess_dict['board'], dtype='i1')

        if chess_dict['last_move'] is not None:
            last_move = Move((0, 0), (0, 0))
            last_move.__dict__ = chess_dict['last_move']
        else:
            last_move = None
        chess_dict['last_move'] = last_move

        chess = Chess(set_start_params=False)
        chess.__dict__ = chess_dict

        success, msg = chess.move(move)
        status = 200 if success else 400
  
        chess_result = chess.__dict__
        #  Change class based object to the dict of their states (To allow json load/dumping)
        chess_result['board'] = chess_result['board'].tolist()
        chess_result['legal_moves'] = [] # TODO Fix this (error due to legalmoves using np types. Should go away after legal_moves rework (Nope. Class objects cannot be converted to json))
        chess_result['last_move'] = chess_result['last_move'].__dict__
        return {"status" : status, "chess" : chess_result, "id" : id, "msg" : msg}

    except Exception as e:
        # traceback.print_exc()  # For debugging
        # print(e)
        return {"status" : 500, "chess" : "None", "id" : id, "msg" : "Parsing input caused exception. either garbage was sent to the server, or server incompetently programmed"}

def getNewGame(id, print_instead_of_return=False):  # Considder just returning a string instead of all these operations
    chess = Chess()
    chess_dict = chess.__dict__

    chess_dict['board'] = chess.board.tolist()
    chess_dict['legal_moves'] = [] # TODO Fix this (error due to legalmoves using np types. Should go away after legal_moves rework)
    result = {"status" : 201, "chess" : chess_dict, 'id' : id}
    # print(result)
    if print_instead_of_return:
        print(result)
    else:
        return result


if (len(sys.argv) > 1):
    client_id = sys.argv[1]
    func = sys.argv[2]
    if func == 'create':
        result = getNewGame(client_id)
        print(json.dumps(result))
    elif func == 'move':
        move = Move((int(sys.argv[3]), int(sys.argv[4])), (int(sys.argv[5]), int(sys.argv[6])))
        result = makeMove(sys.argv[7], move, sys.argv[1])
        print(json.dumps(result))
    else:
        print('dafuq')
else:
    game_state = getNewGame('42')
    print("Gamestate: ", game_state)
    move = Move((1, 0), (3, 0))
    print("jsonMove: ", move)
    stuff = makeMove(start_chess, move, '42')
    print("Return from move", stuff)


