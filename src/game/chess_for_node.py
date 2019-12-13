from chess import Chess
from chess import Move
import json
import numpy as np
from pandas import Series
import sys


def makeMove(chess_json, move_json, id):
    # move_dict = json.loads(move_json)
    # chess_dict = json.loads(chess_json)
    # chess = Chess(set_start_params=False)
    # print('\n', chess)
    # #  Set chess state
    # # chess_info.board = np.array(chess_info.board, dtype='i1')
    
    # print('\n', chess_dict)
    # chess_dict['board'] = np.array(chess_dict['board'], dtype='i1')
    # chess.__dict__ = chess_dict
    # # Make move(s)

    # # Moves done
    # # If illegal move -> return error
    # chess_result = chess.__dict__
    # chess_result['board'] = chess_result['board'].tolist()
    # chess_result['legal_moves'] = [] # TODO Fix this (error due to legalmoves using np types. Should go away after legal_moves rework)
    # print(json.dumps({"status" : 200, "chess" : chess_result, "id" : id}))
    # return
    try:
        move_dict = json.loads(move_json)
        chess_dict = json.loads(chess_json)
        chess = Chess(set_start_params=False)
        print('\n', chess)
        #  Set chess state
        # chess_info.board = np.array(chess_info.board, dtype='i1')
    
        print('\n', chess_dict)
        chess_dict['board'] = np.array(chess_dict['board'], dtype='i1')
        chess.__dict__ = chess_dict
        # Make move(s)

        # Moves done
        # If illegal move -> return error
        chess_result = chess.__dict__
        chess_result['board'] = chess_result['board'].tolist()
        chess_result['legal_moves'] = [] # TODO Fix this (error due to legalmoves using np types. Should go away after legal_moves rework)
        print(json.dumps({"status" : 200, "chess" : chess_result, "id" : id}))
        return
    except Exception as e:
        # print(e)
        print(json.dumps({"status" : 500, "chess" : "None", "id" : id}))
        return

def getNewGame(id, return_instead_of_print=False):
    chess = Chess()
    chess_dict = chess.__dict__
    # print(chess_dict)
    # print(type(chess.board.tolist()[2][2]))

    chess_dict['board'] = chess.board.tolist()
    chess_dict['legal_moves'] = [] # TODO Fix this (error due to legalmoves using np types. Should go away after legal_moves rework)
    # print(chess_dict['board'][0][0])
    # boolean = type(chess_dict['board'][0][0]) == type(2)
    # print(boolean)
    result = json.dumps({"status" : 201, "chess" : chess_dict, 'id' : id})
    # result = Series({"status" : 201, "chess" : chess_dict, 'id' : id}).to_json() # {"status" : 201, "chess" : chess_dict, 'id' : id})
    if return_instead_of_print:
        return result
    else:
        print(result)
    # print(json.dumps({"status" : 201, "chess" : "None", 'id' : id}))


if (len(sys.argv) > 1):
    func = sys.argv[1]
    if func == 'create':
        print('create')
    elif func == 'move':
        print('move')
    else:
        print('dafuq')


# result = getNewGame(2, return_instead_of_print=True)
# print(result)
# result_dict = json.loads(result)
# chess_json = json.dumps(result_dict['chess'])
# makeMove(chess_json, json.dumps(Move((0, 2), (2, 0)).__dict__), 22)
# print(x)
