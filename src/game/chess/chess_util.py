import numpy as np


# def get_start_board(efficient=True):
#     board = np.zeros((8, 8))
#     board[7] = np.array([-2, -3, -4, -10, -100, -4, -3, -2])
#     board[6] = np.ones(8) * -1
#     board[1] = np.ones(8)
#     board[0] = np.array([2, 3, 4, 10, 100, 4, 3, 2])
#     # if not efficient:
#     #     return board.tolist()
#     return board

def get_start_board(efficient=True):
    board = np.zeros((8, 8), dtype='i1')
    board[7] = np.array([-2, -3, -4, -10, -100, -4, -3, -2], dtype='i1')
    board[6] = np.ones(8, dtype='i1') * -1
    board[1] = np.ones(8, dtype='i1')
    board[0] = np.array([2, 3, 4, 10, 100, 4, 3, 2], dtype='i1')
    if not efficient:
        return board.tolist()
    return board


def get_empty_board():
    return np.zeros((8, 8), dtype='i1')


def print_board(board):
    print("")
    print("  |0 |1 |2 |3 |4 |5 |6 |7 |")
    row_num = 7
    for row in reversed(board):
        v_line = str(row_num) + ' |'
        for val in row:
            char = get_unicode_char(val)
            v_line += char + ' |'
        print(v_line)
        row_num = row_num - 1
    # print(h_line)


def get_unicode_char(val):
    if val == 0:
        s = ' '
    elif val == -1:
        s = u'\u2659'
    elif val == -2:
        s = u'\u2656'
    elif val == -3:
        s = u'\u2658'
    elif val == -4:
        s = u'\u2657'
    elif val == -10:
        s = u'\u2655'
    elif val == -100:
        s = u'\u2654'
    elif val == 1:
        s = u'\u265F'
    elif val == 2:
        s = u'\u265C'
    elif val == 3:
        s = u'\u265E'
    elif val == 4:
        s = u'\u265D'
    elif val == 10:
        s = u'\u265B'
    elif val == 100:
        s = u'\u265A'
    else:
        raise ValueError("Value ", val, ", not recognised")
    return s

def move_list_to_string(move_list):
    res = "["
    for move in move_list:
        res += str(move)
    res += "]"
    return res