import numpy as np




def check_winner(board):
    """
    Function to check if game is over, and if it is who won.
    Args:
        board: board as used in NaughtCross or NaughtAI
    Returns:
        bool: True if game is over, False otherwise
        winner (char or int1): Winner. None if game is unfinished or it was a draw
    """
    empty = ' ' if board.dtype == np.dtype('<U1') else 0
    for i in range(3):
        # Checking Vertical
        if (not board[i, 0] == empty) and board[i, 0] == board[i, 1] and board[i, 1] == board[i, 2]:
            return True, board[i, 0]
        # Checking Horizontal
        if (not board[0, i] == empty) and board[0, i] == board[1, i] and board[1, i] == board[2, i]:
            return True, board[0, i]
    # Checking Diagonal (left top to right bottom)
    if (not board[0, 0] == empty) and board[0, 0] == board[1, 1] and board[1, 1] == board[2, 2]:
        return True, board[0, 0]
    # Checking Diagonal (right top to left bottom)
    if (not board[0, 2] == empty) and board[0, 2] == board[1, 1] and board[1, 1] == board[2, 0]:
        return True, board[0, 2]
    # No winner found. Checking if any squares are empty
    for i in range(3):
        for j in range(3):
            if board[i, j] == empty:
                return False, None  # Empty square found -> game still ongoing
    return True, None  # No empty square found & no winner found -> game is a draw


def get_free_tiles(board):
    """
    Args:
        board: NaughtCross board (2d array of char or int1)
    Returns:
        list of indices (as tuples) for which the board is empty
    """
    empty = ' ' if board.dtype == np.dtype('<U1') else 0
    moves = []
    for i in range(3):
        for j in range(3):
            if board[i, j] == empty:
                moves.append((i, j))
    return moves


def get_empty_char_board():
    return np.full((3, 3), ' ')


def get_empty_i1_board():
    return np.zeros((3, 3), dtype='i1')


def char_to_i1_board(board):
    new_board = get_empty_i1_board()
    new_board[board == 'X'] = 1
    new_board[board == 'O'] = -1
    new_board[board == ' '] = 0
    return new_board


def i1_to_char_board(board):
    new_board = get_empty_char_board()
    new_board[board == 1] = 'X'
    new_board[board == 0] = ' '
    new_board[board == -1] = 'O'
    return new_board


def to_i1(player):
    if player == 'X':
        return 1
    if player == 'O':
        return -1
    if player == 1 or player == -1 or player is None:
        return player
    else:
        raise ValueError("A player can only be \"X\", \"Y\" (1 or -1). Was: " + str(player))


def print_board(board):
    if board.dtype == np.dtype('i1'):
        board = i1_to_char_board(board)
    print("Board:")
    print(' ' + board[0, 0] + '|' + board[0, 1] + '|' + board[0, 2])
    print(" -----")
    print(' ' + board[1, 0] + '|' + board[1, 1] + '|' + board[1, 2])
    print(" -----")
    print(' ' + board[2, 0] + '|' + board[2, 1] + '|' + board[2, 2])
    print('')


def score_board(i1_board, i1_player):
    """
    Returns:
        1 if it is a winning board
        -1 if loosing board
        0 if a draw
        None if game is ongoing
    """
    if i1_board.dtype == np.dtype('<U1'):
        i1_board = char_to_i1_board(i1_board)
    has_ended, winner = check_winner(i1_board)
    if not has_ended:
        return None
    if winner is None:
        return 0
    if winner == to_i1(i1_player):
        return 1
    else:
        return -1


def get_boards():
    x_win_board1 = char_to_i1_board(np.array([['X', 'X', 'X'], ['O', 'O', ' '], [' ', ' ', ' ']]))
    x_win_board2 = char_to_i1_board(np.array([['X', 'X', 'O'], ['X', 'O', 'O'], ['X', ' ', ' ']]))
    x_win_board3 = char_to_i1_board(np.array([['X', ' ', 'O'], ['O', 'X', 'O'], ['X', ' ', 'X']]))

    o_win_board1 = char_to_i1_board(np.array([['X', 'X', ' '], ['O', 'O', 'O'], ['X', 'X', ' ']]))
    o_win_board2 = char_to_i1_board(np.array([['X', 'O', ' '], [' ', 'O', 'X'], ['X', 'O', ' ']]))
    o_win_board3 = char_to_i1_board(np.array([['X', 'X', 'O'], ['X', 'O', 'O'], ['O', 'X', ' ']]))

    tie_board = char_to_i1_board(np.array([['X', 'X', 'O'], ['O', 'O', 'X'], ['X', 'X', 'O']]))
    ongoing_board1 = char_to_i1_board(np.array([[' ', 'X', 'O'], ['O', 'X', 'O'], ['X', 'O', 'X']]))
    ongoing_board2 = char_to_i1_board(np.array([[' ', ' ', ' '], ['O', 'X', ' '], ['X', ' ', 'O']]))
    x_win_board4 = char_to_i1_board(np.array([[' ', ' ', 'X'], ['O', 'X', ' '], ['X', ' ', 'O']]))

    return [x_win_board1,
            x_win_board2,
            x_win_board3,
            o_win_board1,
            o_win_board2,
            o_win_board3,
            tie_board,
            ongoing_board1,
            ongoing_board2,
            x_win_board4]
