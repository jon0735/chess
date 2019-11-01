import copy

import chess_util
import numpy as np


def _is_outside_board(pos):
    if pos[0] > 7 or pos[0] < 0 or pos[1] > 7 or pos[1] < 0:
        return True
    else:
        return False


def _is_legal_pawn_move(board, frm, to):
    if abs(board[frm]) != 1:
        return False, "This should never ever fucking happen. is_legal_pawn_move called for non-pawn"
    player = board[frm]
    dist = np.subtract(frm, to)
    vertical = dist[0]
    horizontal = dist[1]
    if vertical == player * -1:
        if horizontal == 0 and board[to] == 0:
            return True, "Standard pawn move"
        elif (horizontal == -1 or horizontal == 1) and board[to]/board[frm] < 0:
            return True, "Attacking pawn move"
        else:
            return False, "Illegal pawn move"
    elif vertical == player * -2 and ((player == 1 and frm[0] == 1) or (player == -1 and frm[0] == 6)):
        if horizontal == 0 and board[to] == 0 and board[frm[0] + player, frm[1]] == 0:
            return True, "Double pawn move"
        else:
            return False, "Illegal pawn move"
    return False, "Illegal pawn move"


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


def _is_legal_king_move(board, frm, to):
    if abs(frm[0] - to[0]) > 1 or abs(frm[1] - to[1]) > 1:
        return False, "Illegal king move"
    return True, "Legal king move"


def _is_legal_move(board, frm, to, in_turn):
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
    if in_turn != owner:
        return False, "Wrong player in turn"
    if board[to]/board[frm] > 0:
        # TODO Check for castling
        return False, "Illegal move; trying to move to own piece"
    # Specific piece type checks
    if piece_type == 1:
        return _is_legal_pawn_move(board, frm, to)
    elif piece_type == 2:
        return _is_legal_rook_move(board, frm, to)
    elif piece_type == 3:
        return _is_legal_knight_move(board, frm, to)
    elif piece_type == 4:
        return _is_legal_bishop_move(board, frm, to)
    elif piece_type == 10:
        return _is_legal_queen_move(board, frm, to)
    elif piece_type == 100:
        return _is_legal_king_move(board, frm, to)
    else:
        raise ValueError("Is_legal_move error: piece_type: ", piece_type, ", not recognised")


def _get_legal_pawn_moves(board, pos):
    player = board[pos]
    row = pos[0]
    column = pos[1]
    moves = []
    # TODO Handle that there weird move shit
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


def get_legal_moves(board, player):
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
    testing_board = copy.deepcopy(board)
    king_pos = _find_king(testing_board, player)
    for (frm, to) in moves:
        # TODO handle castling
        # TODO handle that weird pawn move
        old_to = board[to]
        old_frm = board[frm]
        testing_board[to] = old_frm
        testing_board[frm] = 0
        if old_frm * player == 100:
            self_in_check, _ = is_in_check(testing_board, player, king_pos=to)
        else:
            self_in_check, _ = is_in_check(testing_board, player, king_pos=king_pos)
        # self_in_check, _ = is_in_check(testing_board, player)
        if not self_in_check:
            legal_moves.append((frm, to))
        testing_board[frm] = old_frm
        testing_board[to] = old_to
    return legal_moves


def _find_king(board, player):
    king_pos = None
    for i, row in enumerate(board):
        for j, piece in enumerate(row):
            if piece * player == 100:
                king_pos = (i, j)
                break
    return king_pos


def is_in_check(board, player, king_pos=None):
    if king_pos is None:
        king_pos = _find_king(board, player)
    if king_pos is None:  # No king found -> no king in board -> big error or testing scenario
        return False, None
    for i, row in enumerate(board):
        for j, piece in enumerate(row):
            if piece * player < 0:  # This means the piece is the opponents.
                legal, msg = _is_legal_move(board, (i, j), king_pos, player * -1)
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
#                 # TODO Multi-thread
#                 # TODO Stuff!
#                 pass


class Chess:
    def __init__(self):
        self.board = chess_util.get_start_board()
        self.in_turn = 1
        self.winner = None
        self.is_in_progress = True
        self.legal_moves = get_legal_moves(self.board, self.in_turn)

    def move(self, frm, to, promote_to=None):
        if not self.is_in_progress:
            return False, "Game already concluded"
        legal, msg = _is_legal_move(self.board, frm, to, self.in_turn)
        if not legal:
            return False, msg
        old_frm = self.board[frm]
        old_to = self.board[to]
        # TODO Handle castling and that other move
        need_promotion = (to[0] == 7 and self.board[frm] == 1) or (to[0] == 0 and self.board[frm] == -1)
        if need_promotion:
            legal_promotions = [2, 3, 4, 10]
            if promote_to in legal_promotions:
                self.board[to] = promote_to * self.in_turn
            else:
                return False, "Illegal choice for pawn promotion. ust be in [2, 3, 4, 10]. \n2 = rook, 3 = knight, 4 = bishop, 10 = queen"
        else:
            self.board[to] = self.board[frm]
        self.board[frm] = 0

        is_checked, from_pos = is_in_check(self.board, self.in_turn)
        if is_checked:
            # TODO handle castling and other move
            self.board[to] = old_to
            self.board[frm] = old_frm
            return False, ("Illegal move due to check from pos " + str(from_pos))
        self.in_turn = self.in_turn * -1
        self.legal_moves = get_legal_moves(self.board, self.in_turn)
        checks, from_pos = is_in_check(self.board, self.in_turn)
        if checks:
            if len(self.legal_moves) == 0:  # Checkmate
                winner = self.in_turn * -1  # Already changed turn, so winner was player in last turn
                winner_string = "white" if winner == 1 else "black"
                msg += ", Checkmate. Winner is " + winner_string
                self.winner = winner
                self.is_in_progress = False
            else:
                msg += ", check from " + str(from_pos)
        elif len(self.legal_moves) == 0:
            msg += ", no legal moves this turn. Game is a draw"
            self.is_in_progress = False

        return True, msg

