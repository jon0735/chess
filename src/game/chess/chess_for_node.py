
# print("MEH")
import sys
import os
import json
import numpy as np
import traceback
import random

# from game.chess.chess import Chess, Move
# from game.ai.chess_ai.chess_ai import choose_move_ab, latest_nn_move

try:
    from game.chess.chess import Chess, Move
    from game.ai.chess_ai.chess_ai import choose_move_ab, latest_nn_move
except Exception as e:
    trace = traceback.format_exc()
    print(json.dumps({"status": 500, "msg": "Import error. Error: " + str(e) + ", trace: " + str(trace) + "\nPath: " + str(sys.path)}))
    sys.exit()

# try:
#     if __name__ == '__main__': # hacky shit to allow both testing via game/test.py and to call it as a script via server/server.js
#         from chess import Chess
#         from chess import Move
#         sys.path.insert(1, os.path.join(sys.path[0], '..'))
#         from ai.chess_ai import choose_move_ab, latest_nn_move
#         # import studd
#     else:
#         from chess.chess import Chess
#         from chess.chess import Move
# except Exception as e:
#     trace = traceback.format_exc()
#     print(json.dumps({"status": 500, "msg": "Import error. Error: " + str(e) + ", trace: " + str(trace) + "\nPath: " + str(sys.path)}))
#     sys.exit()

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

        return json.dumps(chess_dict, cls=MyEncoder)
    except:
        # traceback.print_exc()  # For debugging
        # print(e)
        return None

def makeMove(id, chess_json, move=None):
    try:
        chess = unpack_chess(chess_json)
        if chess is None:
            return {"status" : 500, "chess" : "None", "id" : id, "msg" : "Parsing input caused exception (unpacking). Either garbage was sent to the server, or server incompetently programmed"}
        success, extra = chess.move(move, return_extra=True)
        if success:
            msg = extra["msg"]
            move_info = extra["extra"]
        else:
            msg = extra
            move_info = dict()
        status = 200 if success else 400
        if status == 400 and msg.startswith('Illegal choice for pawn promotion'):
            status = 220
        move_info['rFrom'] = move.frm[0]
        move_info['cFrom'] = move.frm[1]
        move_info['rTo'] = move.to[0]
        move_info['cTo'] = move.to[1]
        chess_result = pack_chess(chess)
        if chess is None:
            return {"status" : 500, "chess" : "None", "id" : id, "msg" : "Parsing input caused exception (packing). Either garbage was sent to the server, or server incompetently programmed"}
        
        result = {"status" : status, "chess" : chess_result, "id" : id, "move": move_info, "msg" : msg}
        if not chess.is_in_progress:
            result["status"] = 203
            result["winner"] = chess.winner
        return result
        # return {"status" : status, "chess" : chess_result, "id" : id, "move": move_info, "msg" : msg}
    except Exception as e:
        trace = traceback.format_exc()  # For debugging
        # print(e)
        return {"status" : 500, "chess" : "None", "id" : id, "msg" : "Error while performing move. either garbage was sent to the server, or server incompetently programmed. Error: " + str(e) + ", Trace: " + str(trace)}

def makeAiMove(id, chess_json):
    string = "none"
    try:
        chess = unpack_chess(chess_json)
        # string += "unpacked"
        # TODO Handle 
        # move = random.choice(chess.legal_moves) # TODO Ai stuff
        # move, value = choose_move_ab(chess, depth=3)
        move, value = latest_nn_move(chess)
        # string += "\nrandomMove"
        string = str(move)

        success, extra = chess.move(move, return_extra=True)

        if isinstance(extra, str):
            return {"status" : 500, "chess" : "None", 
                    "id" : id, 
                    "move": None, 
                    "msg" : "Extra returned as string -> error in move " + str(move) + str(success) + extra}


        msg = extra["msg"]
        move_info = extra["extra"]
        status = 210 if success else 400
        if status == 400:
            msg += ". This can only happen due to incompetent programming"
        

        # string += "\nSuccess determined"
        chess_result = pack_chess(chess)
        move_info['rFrom'] = move.frm[0]
        move_info['cFrom'] = move.frm[1]
        move_info['rTo'] = move.to[0]
        move_info['cTo'] = move.to[1]
        # string += "\nJust before return"
        result = {"status" : status, "chess" : chess_result, "id" : id, "move": move_info, "msg" : msg + ", with value: " + str(value)}
        if not chess.is_in_progress:
            result["status"] = 203
            result["winner"] = chess.winner
        return result
    except Exception as e:
        # traceback.print_exc()
        # print(str(e))
        trace = traceback.format_exc() 
        return {"status" : 500, "chess" : "None", "id" : id, "move": None, "msg" : "Parsing input caused exception. Server incompetently programmed. error: " + str(e) + ", Trace: " + str(trace) + ", move = " + string}


def getNewGame(id):  # Consider just returning a string instead of all these operations
    try:
        chess_dict = pack_chess(Chess())
        result = {"status" : 201, "chess" : chess_dict, 'id' : id}
        return result
    except Exception as e:
        # print(e)
        return {"status" : 500, "chess" : "None", "id" : id, "msg" : "Parsing input caused exception. Server incompetently programmed"}


if __name__ == '__main__' and (len(sys.argv) > 1):
    
    try:
        client_id = sys.argv[1]
        func = sys.argv[2]
        if func == 'create':
            result = getNewGame(client_id)
            print(json.dumps(result))
        elif func == 'move':
            promote_arg = int(sys.argv[9])
            # if promote_arg != 0:
            #     print(move)
            promote = None if promote_arg == 0 else promote_arg
            move = Move((int(sys.argv[3]), int(sys.argv[4])), (int(sys.argv[5]), int(sys.argv[6])), promote=promote)
            # if promote is not None:
            #     print(move)
            result = makeMove(client_id, sys.argv[7], move=move)
            print(json.dumps(result))
        elif func == 'ai':
            result = makeAiMove(client_id, sys.argv[3])
            if result['status'] == 200:
                result['status'] = 210
            print(json.dumps(result))
        else:
            print(json.dumps({"status" : 500, "chess" : "None", "id" : id, "msg" : "Function " + func + ", not recognised"}))
    except Exception as e:
        print(json.dumps({"status" : 500, "chess" : "None", "id" : id, "msg" : e}))

# TODO: Make sure in_turn stuff is checked properly


