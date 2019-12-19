import copy

import chess_util
import numpy as np

def _is_outside_board(pos):
    if pos[0] > 7 or pos[0] < 0 or pos[1] > 7 or pos[1] < 0:
        return True
    else:
        return False

def _is_legal_pawn_move(chess, move):
    board = chess.board
    frm = move.frm
    to = move.to
    if abs(board[frm]) != 1:
        return False, "This should never ever fucking happen. is_legal_pawn_move called for non-pawn"
    player = board[frm]
    dist = np.subtract(to, frm)  # dist = np.subtract(frm, to)
    vertical = dist[0]
    horizontal = dist[1]

    # Refactor to avoid duplicate computations. (small computational cost for more readable code?)
    abs_vertical = vertical * player  # This means a movement in correct direction gives abs_vertical > 0
    abs_horizontal = abs(horizontal)
    is_standard_move = abs_vertical == 1 and abs_horizontal == 0
    is_double_move = abs_vertical == 2 and abs_horizontal == 0
    is_attack_move = abs_vertical == 1 and abs_horizontal == 1
    if not (is_standard_move or is_double_move or is_attack_move):  # True of move is not within normal pawn move types
        return False, "Illegal pawn move"
    return_msg = "Legal pawn move"

    #  Beautiful mother of if-statements (sarcasm).
    if is_standard_move:  # standard pawn move
        if board[to] != 0:  #non-empty 'to' spot
            return False, "Pawn can only attack diagonally"

    elif is_double_move:  # Double move
        if ( player == 1 and frm[0] != 1) or (player == -1 and frm[0] != 6):  # Checks if correct rows for double moves (1 for white, 6 for black)
            return False, "Illegal pawn move"
        if board[to] != 0 or board[frm[0] + player, frm[1]] != 0:  # Checks if middle square is empty
            return False, "Illegal pawn move"

    elif is_attack_move:
        if player * board[to] > 0:  # Own or empty spot -> Illegal as this should be an attack move
            return False, "Diagonal pawn move must be a capture move"
        elif board[to] == 0:
            is_legal_en_passant, msg = _is_legal_en_passant(chess, move)
            if not is_legal_en_passant:
                return False, "Diagonal pawn move must be a capture move"
            else:
                return_msg = msg 
    else:
        return False, "This should never happen. This case should be caught earlier"

    to_row = to[0]
    if move.promote is not None:
        if to_row not in [0, 7]:  # Other checks make sure that if to_row in [0, 7] it is the correct player 
            return False, "Cannot promote pawn if pawn does not move to enemy backline"
        if move.promote not in [1, 2, 3, 4, 10]:
            return False, "Illegal choice for pawn promotion. Must be in [1, 2, 3, 4, 10]. \n1 = pawn, 2 = rook, 3 = knight, 4 = bishop, 10 = queen"
    else:
        if to_row in [0, 7]:
            return False, "Illegal choice for pawn promotion. Must be in [1, 2, 3, 4, 10]. \n1 = pawn, 2 = rook, 3 = knight, 4 = bishop, 10 = queen"
    return True, return_msg


def _is_legal_bishop_move(board, frm, to):
    dist = (to[0] - frm[0], to[1] - frm[1])
    if abs(dist[0]) != abs(dist[1]):
        return False, "Illegal rook move"
    direction = (dist[0]//abs(dist[0]), dist[1]//abs(dist[1]))
    mid_pos = (frm[0] + direction[0], frm[1] + direction[1])
    while mid_pos != to:
        if board[mid_pos] != 0:
            return False, "Illegal rook move; path blocked"
        mid_pos = (mid_pos[0] + direction[0], mid_pos[1] + direction[1])
    return True, "Legal rook move"


def _is_legal_rook_move(board, frm, to):
    dist = (to[0] - frm[0], to[1] - frm[1])
    if not (dist[0] == 0 or dist[1] == 0):
        return False, "Illegal bishop move"
    axis = 0 if dist[0] != 0 else 1
    parity = 1 if dist[axis] > 0 else -1
    direction = (0, parity) if axis else (parity, 0)
    mid_pos = (frm[0] + direction[0], frm[1] + direction[1])
    while mid_pos != to:
        # print(mid_pos)
        if board[mid_pos] != 0:
            return False, "Illegal bishop move; path blocked"
        mid_pos = (mid_pos[0] + direction[0], mid_pos[1] + direction[1])
    return True, "Legal bishop move"


def _is_legal_knight_move(board, frm, to):
    dist = (abs(to[0] - frm[0]), abs(to[1] - frm[1]))
    if not (dist == (1, 2) or dist == (2, 1)):
        return False, "Illegal knight move"
    return True, "Legal knight move"


def _is_legal_queen_move(board, frm, to):
    success, _ = _is_legal_rook_move(board, frm, to)
    if success:
        return True, "Legal queen move"
    success, _ = _is_legal_bishop_move(board, frm, to)
    if success:
        return True, "Legal queen move"
    return False, "Illegal queen move"


def _is_legal_king_move(chess, move):
    frm = move.frm
    to = move.to
    board = chess.board
    if abs(frm[0] - to[0]) > 1 or abs(frm[1] - to[1]) > 1:  
        is_legal_castle, msg = _is_legal_castling(chess, move)
        if not is_legal_castle:
            return False, msg
        else:
            msg = "Legal castling move"
    else:
        msg =  "Legal king move"
    return True, msg

def _is_legal_castling(chess, move):
    frm = move.frm
    to = move.to
    board = chess.board
    player = board[frm] / abs(board[frm])
    if frm == (0, 4) or frm == (7, 4):
        row = frm[0]  # 0 if white move, 7 if black. Using this variable allows using same code for both colors below
        if to == (row, 2):  # If castling left
            if not (board[row, 1] == 0 and board[row, 3] == 0): #  If board[0, 2] != 0 it will fail on a check for same piece on 'to' location
                return False, "Castling blocked by piece(s) between rook and king"
            is_attacked, _ = is_in_check(chess, player, king_pos=(row, 3))
            if is_attacked:
                return False, "King moves through attacked pos"
        elif to == (row, 6):  # If castling right
            if not (board[row, 5] == 0):  #  If board[0, 6] != 0 it will fail on a check for same piece on 'to' location
                return False, "Castling blocked by piece(s) between rook and king"
            is_attacked, _ = is_in_check(chess, player, king_pos=(row, 5))
            if is_attacked:
                return False, "King moves through attacked pos"
        else:
            return False, "Illegal 'to' position for castling move"
    else:
        return False, "Illegal king location for castling"
    
    if (not chess.legal_castles[str(to)]):
        return False, "Illegal castle due to previous rook or king movement"
    in_check, pos = is_in_check(chess, player, king_pos=frm)
    if in_check:
        return False, "Cannot castle if king is in check. Check from " + str(pos)
    return True, "Legal"

def _is_legal_en_passant(chess, move): # Asumes it is called from '_is_legal_pawn_move' and therefore doesn't check standard pawn things
    frm  = move.frm
    to = move.to

    player = chess.in_turn  # Inconsistent with how I do it other places
    if player == 1 and frm[0] != 4:  # For white en passant can only happen at row 4 
        return False, "Illegal En Passant"
    elif player == -1 and frm[0] != 3: # For black en passant can only happen at row 3
        return False, "Illegal En Passant"
    
    last_move = chess.last_move
    if not (last_move.frm == (to[0] + player, to[1]) and last_move.to == (to[0] - player, to[1])):
        return False, "Illegal En Passant"
    if chess.board[chess.last_move.to] * player != -1:
        return False, "Illegal En Passant"
    return True, "Legal En Passant"


def _is_legal_move(chess, move, in_turn):
    board = chess.board
    frm = move.frm
    to = move.to

    # General checks
    if _is_outside_board(frm):
        return False, "\"frm\" pos outside board"
    if _is_outside_board(to):
        return False, "\"to\" pos outside board"
    piece = board[frm]
    if piece == 0:
        return False, "Empty square selected"
    piece_type = abs(piece)
    owner = piece / piece_type
    # print("Owner: ", owner)
    # print("In turn: ", in_turn)
    # in_turn = chess.in_turn
    if in_turn != owner:
        return False, "Wrong player in turn"
    if board[to]/board[frm] > 0:
        return False, "Illegal move; trying to move to own piece"

    # Specific piece type checks
    # TODO: Inconsistant function args for different piece types
    if piece_type == 1:
        return _is_legal_pawn_move(chess, move)
    elif piece_type == 2:
        return _is_legal_rook_move(board, frm, to)
    elif piece_type == 3:
        return _is_legal_knight_move(board, frm, to)
    elif piece_type == 4:
        return _is_legal_bishop_move(board, frm, to)
    elif piece_type == 10:
        return _is_legal_queen_move(board, frm, to)
    elif piece_type == 100:
        return _is_legal_king_move(chess, move)
    else:
        raise ValueError("Is_legal_move error: piece_type: ", piece_type, ", not recognised")


def _get_legal_pawn_moves(board, pos):
    player = board[pos]
    row = pos[0]
    column = pos[1]
    moves = []
    # TODO Handle En passant
    if not _is_outside_board((row + player, column)) and board[row + player, column] == 0:
        moves.append((pos, (row + player, column)))
        if (player == 1 and row == 1) or (player == -1 and row == 6):
            if board[row + 2 * player, column] == 0:
                moves.append((pos, (row + 2 * player, column)))
    left_attack = (row + player, column - 1)
    right_attack = (row + player, column + 1)
    if not _is_outside_board(left_attack) and board[left_attack] * player < 0:
        moves.append((pos, left_attack))
    if not _is_outside_board(right_attack) and board[right_attack] * player < 0:
        moves.append((pos, right_attack))
    return moves


def _get_legal_rook_moves(board, pos):
    player = 1 if board[pos] > 0 else -1
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    moves = []
    for d in directions:
        dist = 1
        while True:
            p = (pos[0] + dist * d[0], pos[1] + dist * d[1])
            dist = dist + 1
            if _is_outside_board(p):
                break
            elif board[p] == 0:
                moves.append((pos, p))
            elif board[p] * player < 0:
                moves.append((pos, p))
                break
            elif board[p] * player > 0:
                break
    return moves


def _get_legal_knight_moves(board, pos):
    # if abs(board[pos]) != 3:
    #     raise EnvironmentError("Non-knight found at what was supposed to be knight pos")
    player = 1 if board[pos] > 0 else -1
    pos_list = [(1, 2), (1, -2), (2, 1), (2, -1), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]
    moves = []
    for p in pos_list:
        to = (p[0] + pos[0], p[1] + pos[1])
        if not _is_outside_board(to) and board[to] * player <= 0:
            moves.append((pos, to))
    return moves


def _get_legal_bishop_moves(board, pos):
    player = 1 if board[pos] > 0 else -1
    directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
    moves = []
    for d in directions:
        dist = 1
        while True:
            p = (pos[0] + dist * d[0], pos[1] + dist * d[1])
            dist = dist + 1
            if _is_outside_board(p):
                break
            elif board[p] == 0:
                moves.append((pos, p))
            elif board[p] * player < 0:
                moves.append((pos, p))
                break
            elif board[p] * player > 0:
                break
    return moves


def _get_legal_queen_moves(board, pos):
    rook_moves = _get_legal_rook_moves(board, pos)
    bishop_moves = _get_legal_bishop_moves(board, pos)
    return rook_moves + bishop_moves

# Does NOT handle castling
def _get_legal_king_moves(board, pos):
    player = 1 if board[pos] > 0 else -1
    moves = []
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0:
                continue
            # TODO Handle castling
            p = (pos[0] + i, pos[1] + j)
            if _is_outside_board(p):
                continue
            if board[p] * player <= 0:
                moves.append((pos, p))
    return moves


def get_legal_moves(chess, player):
    board = chess.board
    moves = []
    for i, row in enumerate(board):
        for j, piece in enumerate(row):
            if player * piece > 0:
                piece_type = piece * player
                if piece_type == 1:
                    moves = moves + _get_legal_pawn_moves(board, (i, j))
                elif piece_type == 2:
                    moves = moves + _get_legal_rook_moves(board, (i, j))
                elif piece_type == 3:
                    moves = moves + _get_legal_knight_moves(board, (i, j))
                elif piece_type == 4:
                    moves = moves + _get_legal_bishop_moves(board, (i, j))
                elif piece_type == 10:
                    moves = moves + _get_legal_queen_moves(board, (i, j))
                elif piece_type == 100:
                    moves = moves + _get_legal_king_moves(board, (i, j))
                else:
                    raise ValueError("Is_legal_move error: piece_type: ", piece_type, ", not recognised")
    legal_moves = []
    testing_chess = copy.deepcopy(chess)
    # testing_board = copy.deepcopy(board)
    king_pos = _find_king(testing_chess.board, player)
    for (frm, to) in moves:
        # TODO handle castling
        # TODO handle that weird pawn move
        old_to = board[to]
        old_frm = board[frm]
        testing_chess.board[to] = old_frm
        testing_chess.board[frm] = 0
        if old_frm * player == 100:
            self_in_check, _ = is_in_check(testing_chess, player, king_pos=to)
        else:
            self_in_check, _ = is_in_check(testing_chess, player, king_pos=king_pos)
        # self_in_check, _ = is_in_check(testing_board, player)
        if not self_in_check:
            legal_moves.append((frm, to))
        testing_chess.board[frm] = old_frm
        testing_chess.board[to] = old_to
    return legal_moves


def _find_king(board, player):
    king_pos = None
    for i, row in enumerate(board):
        for j, piece in enumerate(row):
            if piece * player == 100:
                king_pos = (i, j)
                break
    return king_pos


def is_in_check(chess, player, king_pos=None):
    board = chess.board
    if king_pos is None:
        king_pos = _find_king(board, player)
    if king_pos is None:  # No king found -> no king in board -> big error or testing scenario
        return False, None
    for i, row in enumerate(board):
        for j, piece in enumerate(row):
            if piece * player < 0:  # This means the piece is the opponents.
                legal, msg = _is_legal_move(chess, Move((i, j), king_pos), player * -1)
                if legal:
                    return True, (i, j)
    return False, None


# def is_checkmated(board, player, king_pos=None):
#     if king_pos is None:
#         king_pos = _find_king(board, player)
#     if king_pos is None:  # No king found -> no king in board -> big error or testing scenario
#         return False
#     testing_board = copy.deepcopy(board)
#     for i, row in enumerate(board):
#         for j, piece in enumerate(row):
#             if piece * player > 0:
#                 # TODO Multi-thread <- wtf did I mean by this
#                 # TODO Stuff! <- Well that's a fucking useless message
#                 pass

class Move:
    def __init__(self, frm, to, promote=None):
        self.frm = frm
        self.to = to
        self.promote = promote

class Chess:
    def __init__(self, set_start_params=True):
        if set_start_params:
            self.board = chess_util.get_start_board()
            self.in_turn = 1
            self.turn_num = 1
            self.is_in_progress = True
            self.winner = None
            self.legal_moves = get_legal_moves(self, self.in_turn) # Make function just for start, to reduce init time
            self.last_move = None
            self.legal_castles = {'(0, 2)' : True, '(0, 6)' : True, '(7, 2)' : True, '(7, 6)' : True}
        else: # Low cost init if one needs to reset everything anyway
            self.board = None
            self.in_turn = None
            self.turn_num = None
            self.is_in_progress = None
            self.winner = None
            self.legal_moves = None
            self.last_move = None
            self.legal_castles = None

    def move(self, move):
        frm = move.frm
        to = move.to
        if not self.is_in_progress:
            return False, "Game already concluded"
        legal, msg = _is_legal_move(self, move, self.in_turn)
        if not legal:
            return False, msg

        backup_board = copy.deepcopy(self.board)  # backup to rollback if move puts player in check

        self.board[to] = self.board[frm]
        self.board[frm] = 0

        if move.promote is not None and move.promote in [1, 2, 3, 4, 10]:
            self.board[to] = move.promote * self.in_turn
        if msg == "Legal castling move":  # move.castle:
            if to == (0, 2):
                self.board[0, 3] = 2
                self.board[0, 0] = 0
            elif to == (0, 6):
                self.board[0, 5] = 2
                self.board[0, 7] = 0
            elif to == (7, 2):
                self.board[7, 3] = -2
                self.board[7, 0] = 0
            elif to == (7, 6):
                self.board[7, 5] = -2
                self.board[7, 7] = 0
        if msg == "Legal En Passant":
            self.board[to[0] - self.in_turn, to[1]] = 0

        is_checked, from_pos = is_in_check(self, self.in_turn)
        if is_checked:
            # TODO handle castling and other move
            # self.board[to] = old_to
            # self.board[frm] = old_frm
            self.board = backup_board
            return False, ("Illegal move due to check from pos " + str(from_pos))

        self.turn_num += 1
        self.in_turn = self.in_turn * -1
        self.legal_moves = get_legal_moves(self, self.in_turn)
        checks, from_pos = is_in_check(self, self.in_turn)
        if checks:
            if len(self.legal_moves) == 0:  # No legal moves for player + in check -> Checkmate
                winner = self.in_turn * -1  # Already changed turn, so winner was player in last turn
                winner_string = "white" if winner == 1 else "black"
                msg += ", Checkmate. Winner is " + winner_string
                self.winner = winner
                self.is_in_progress = False
            else:
                msg += ", check from " + str(from_pos)
        elif len(self.legal_moves) == 0:  # No legal moves + not in check -> Game is a draw. Weird fucking rule. Forced into a no move position = draw -.-
            msg += ", no legal moves this turn. Game is a draw"
            self.is_in_progress = False
        self.last_move = move
        # Feels ugly and shitty
        if frm == (0, 4):
            self.legal_castles['(0, 2)'] = False
            self.legal_castles['(0, 6)'] = False
        elif frm == (0, 0):
            self.legal_castles['(0, 2)'] = False
        elif frm == (0, 7):
            self.legal_castles['(0, 6)'] = False
        elif frm == (7, 4):
            self.legal_castles['(7, 2)'] = False
            self.legal_castles['(7, 6)'] = False
        elif frm == (7, 0):
            self.legal_castles['(7, 2)'] = False
        elif frm == (7, 7):
            self.legal_castles['(7, 6)'] = False
        return True, msg

