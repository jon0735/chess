import sys
# sys.path.append("..")

# print(sys.path)


import json
import numpy as np
import traceback
import random

# print(sys.path)

from chess import Chess
from chess import Move


# print("After imports")

start_chess = '{"board": [[2, 3, 4, 10, 100, 4, 3, 2], [1, 1, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [-1, -1, -1, -1, -1, -1, -1, -1], [-2, -3, -4, -10, -100, -4, -3, -2]], "in_turn": 1, "turn_num": 1, "is_in_progress": true, "winner": null, "legal_moves": [], "last_move": null, "legal_castles": {"(0, 2)": true, "(0, 6)": true, "(7, 2)": true, "(7, 6)": true} }'

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)

def unpack_chess(chess_json):
    try:
        chess_dict = json.loads(chess_json)
        chess_dict['board'] = np.array(chess_dict['board'], dtype='i1')

        if chess_dict['last_move'] is not None:
            chess_dict['last_move'] = Move(None, None, move_dict=chess_dict['last_move'])
            # last_move = Move((0, 0), (0, 0))
            # last_move.__dict__ = chess_dict['last_move']
        # else:
        #     last_move = None
        # chess_dict['last_move'] = last_move
        # TODO properly unpack legal moves
        chess_dict['legal_moves'] = [Move(None, None, move_dict=move_dict) for move_dict in chess_dict['legal_moves']]
        chess = Chess(chess_dict=chess_dict)
        return chess
        # chess.__dict__ = chess_dict
    except:
        traceback.print_exc()  # For debugging
        # print(e)
        return None

def pack_chess(chess):
    try:
        chess_dict = chess.__dict__
        chess_dict['board'] = chess_dict['board'].tolist()
        chess_dict['legal_moves'] = [move.__dict__ for move in chess_dict['legal_moves']] #[move.__dict__ for move in chess_dict['legal_moves']] # TODO Fix this (error due to legalmoves using np types. Should go away after legal_moves rework (Nope. Class objects cannot be converted to json))
        if chess_dict['last_move'] is not None:
            chess_dict['last_move'] = chess_dict['last_move'].__dict__
        # a = json.dumps(chess_dict['last_move'])
        # b = json.dumps(chess_dict['board'])
        # print(type(chess_dict['legal_moves'][0]['frm'][0]))
        # print(chess_dict['legal_moves'])
        # c = json.dumps(chess_dict['legal_moves'], cls=MyEncoder)
        return json.dumps(chess_dict, cls=MyEncoder)
    except:
        traceback.print_exc()  # For debugging
        # print(e)
        return None

def makeMove(chess_json, move, id):
    try:
        # chess_dict = json.loads(chess_json)
        # chess_dict['board'] = np.array(chess_dict['board'], dtype='i1')

        # if chess_dict['last_move'] is not None:
        #     last_move = Move((0, 0), (0, 0))
        #     last_move.__dict__ = chess_dict['last_move']
        # else:
        #     last_move = None
        # chess_dict['last_move'] = last_move
        # # TODO properly unpack legal moves

        # chess = Chess(chess_dict=chess_dict)
        chess = unpack_chess(chess_json)
        # chess.__dict__ = chess_dict

        success, msg = chess.move(move)
        status = 200 if success else 400

        # TODO properly pack legal moves
        # chess_result = chess.__dict__
        #  Change class based object to the dict of their states (To allow json load/dumping)
        # chess_result['board'] = chess_result['board'].tolist()
        # chess_result['legal_moves'] = [Move((0, 2), (2, 0)).__dict__, Move((0, 2), (2, 4)).__dict__, ]  #[move.__dict__ for move in chess_dict['legal_moves']] # TODO Fix this (error due to legalmoves using np types. Should go away after legal_moves rework (Nope. Class objects cannot be converted to json))
        # chess_result['last_move'] = chess_result['last_move'].__dict__
        chess_result = pack_chess(chess) # NOT TESTED
        return {"status" : status, "chess" : chess_result, "id" : id, "msg" : msg}

    except Exception as e:
        traceback.print_exc()  # For debugging
        # print(e)
        return {"status" : 500, "chess" : "None", "id" : id, "msg" : "Parsing input caused exception. either garbage was sent to the server, or server incompetently programmed"}

def makeAiMove(id, chess_json):
    try:
        # print(chess_json)
        chess = unpack_chess(chess_json) 
        # print("Stuff")
        move = random.choice(chess.legal_moves) # TODO Ai stuff
        success, msg = chess.move(move, debug=True) # TODO error here (The truth value of array is undefined.. use any all stuff)
        print("stuff 3")
        status = 200 if success else 400
        print(status)
        if status == 400:
            msg += ". This can only happen due to incompetent programming"
        chess_result = pack_chess(chess)
        return {"status" : status, "chess" : chess_result, "id" : id, "move": move.__dict__, "msg" : msg}
    except Exception as e:
        # traceback.print_exc()
        # print(e)
        return {"status" : 500, "chess" : "None", "id" : id, "msg" : "Parsing input caused exception. Server incompetently programmed"}


def getNewGame(id, print_instead_of_return=False):  # Considder just returning a string instead of all these operations
    chess = Chess()
    # chess_dict = chess.__dict__

    # chess_dict['board'] = chess.board.tolist()
    # chess_dict['legal_moves'] = [] #[move.__dict__ for move in chess_dict['legal_moves']] # TODO Fix this (error due to legalmoves using np types. Should go away after legal_moves rework)
    chess_dict = pack_chess(chess)
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
        result = makeMove(sys.argv[7], move, client_id)
        print(json.dumps(result))
        # print(json.dumps({"status" : 42, "chess" : "None", "id" : id, "msg" : "TEST"}))
    elif func == 'ai':
        result = makeAiMove(client_id, sys.argv[3])
        print(json.dumps(result))
    else:
        print(json.dumps({"status" : 500, "chess" : "None", "id" : id, "msg" : "Function " + func + ", not recognised"}))
        # print('dafuq')
# else:
    # print("WTF")
# else:
#     game_state = getNewGame('42')
#     print("Gamestate: ", game_state)
#     move = Move((1, 0), (3, 0))
#     print("jsonMove: ", move)
#     stuff = makeMove(start_chess, move, '42')
#     print("Return from move", stuff)

# TODO: Make sure in_turn stuff is checked properly


