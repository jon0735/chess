import sys

import json
import numpy as np
import traceback
import random

if __name__ == '__main__': # hacky shit to allow both testing via game/test.py and to call it as a script via server/server.js
    from chess import Chess
    from chess import Move
else:
    from chess.chess import Chess
    from chess.chess import Move

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

        chess_dict['legal_moves'] = [Move(None, None, move_dict=move_dict) for move_dict in chess_dict['legal_moves']]
        chess = Chess(chess_dict=chess_dict)
        return chess
    except:
        # traceback.print_exc()  # For debugging
        # print(e)
        return None

def pack_chess(chess):
    try:
        chess_dict = chess.__dict__
        chess_dict['board'] = chess_dict['board'].tolist()
        chess_dict['legal_moves'] = [move.__dict__ for move in chess_dict['legal_moves']] #[move.__dict__ for move in chess_dict['legal_moves']] # TODO Fix this (error due to legalmoves using np types. Should go away after legal_moves rework (Nope. Class objects cannot be converted to json))
        if chess_dict['last_move'] is not None:
            chess_dict['last_move'] = chess_dict['last_move'].__dict__

        return json.dumps(chess_dict, cls=MyEncoder)
    except:
        # traceback.print_exc()  # For debugging
        # print(e)
        return None

def makeMove(chess_json, move, id):
    try:
        chess = unpack_chess(chess_json)

        success, msg = chess.move(move)
        status = 200 if success else 400

        chess_result = pack_chess(chess) 
        return {"status" : status, "chess" : chess_result, "id" : id, "msg" : msg}
    except Exception as e:
        traceback.print_exc()  # For debugging
        # print(e)
        return {"status" : 500, "chess" : "None", "id" : id, "msg" : "Parsing input caused exception. either garbage was sent to the server, or server incompetently programmed"}

def makeAiMove(id, chess_json):
    try:
        chess = unpack_chess(chess_json) 
        move = random.choice(chess.legal_moves) # TODO Ai stuff
        success, msg, move_info = chess.move(move, return_extra=True) # TODO error here (The truth value of array is undefined.. use any all stuff)
        status = 210 if success else 400
        if status == 400:
            msg += ". This can only happen due to incompetent programming"
        chess_result = pack_chess(chess)
        move_info['frm'] = move.frm
        move_info['to'] = move.to
        return {"status" : status, "chess" : chess_result, "id" : id, "move": move_info, "msg" : msg}
    except Exception as e:
        # traceback.print_exc()
        # print(e)
        return {"status" : 500, "chess" : "None", "id" : id, "move": None, "msg" : "Parsing input caused exception. Server incompetently programmed"}


def getNewGame(id):  # Considder just returning a string instead of all these operations
    try:
        chess_dict = pack_chess(Chess())
        result = {"status" : 201, "chess" : chess_dict, 'id' : id}
        return result
    except Exception as e:
        # print(e)
        return {"status" : 500, "chess" : "None", "id" : id, "msg" : "Parsing input caused exception. Server incompetently programmed"}


if __name__ == '__main__' and (len(sys.argv) > 1):
    client_id = sys.argv[1]
    func = sys.argv[2]
    if func == 'create':
        result = getNewGame(client_id)
        print(json.dumps(result))
    elif func == 'move':
        move = Move((int(sys.argv[3]), int(sys.argv[4])), (int(sys.argv[5]), int(sys.argv[6])))
        result = makeMove(sys.argv[7], move, client_id)
        print(json.dumps(result))
    elif func == 'ai':
        result = makeAiMove(client_id, sys.argv[3])
        print(json.dumps(result))
    else:
        print(json.dumps({"status" : 500, "chess" : "None", "id" : id, "msg" : "Function " + func + ", not recognised"}))


# TODO: Make sure in_turn stuff is checked properly


