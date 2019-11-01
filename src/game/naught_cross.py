import numpy as np
import naught_util


class NaughtCross:
    # noinspection PyTypeChecker
    def __init__(self, board=None, starting_player=None):
        if board is None:
            self.board = naught_util.get_empty_char_board()
        else:
            self.board = board
        if starting_player is None:
            self.next = 'X'
        else:
            self.next = starting_player
        self.winner = None
        self.game_in_progress = True

    def make_move(self, pos, symbol):
        if not self.game_in_progress:
            return False, "Game over"

        if not isinstance(pos, tuple):
            return False, "Pos argument must be an integer tuple with values between 0-2"

        for i in pos:
            if not isinstance(i, int):
                return False, "Pos argument must be an integer tuple with values between 0-2"
            if i < 0 or i > 2:
                return False, "Move outside of board"

        if not (symbol == 'X' or symbol == 'O'):
            return False, "Symbol must be X or O"

        if not symbol == self.next:
            return False, "Wrong player turn"

        if self.board[pos] != ' ':
            return False, "Spot already occupied"

        self.board[pos] = symbol

        if symbol == 'X':
            self.next = 'O'
        else:
            self.next = 'X'
        w = self._check_and_set_winner()
        if w:
            return True, "Move Performed, Winner found: " + str(self.winner)

        return True, "Move performed"

    def _check_and_set_winner(self):
        has_won, winner = self.check_winner()
        if has_won:
            self.game_in_progress = False
            self.winner = winner
            return True
        else:
            return False

    def check_winner(self):
        if self.winner is not None:
            return True, self.winner
        return naught_util.check_winner(self.board)

    def get_legal_moves(self):
        return naught_util.get_free_tiles(self.board), self.next

    def print_board(self):
        naught_util.print_board(self.board)

