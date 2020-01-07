from chess import Chess
import chess_util

#  TODO: Need major update if this is supposed to work. Made before Move class amongst other huge changes

class ChessGame:
    def __init__(self):
        self.chess = Chess()

    def start(self):
        while self.chess.is_in_progress:
            chess_util.print_board(self.chess.board)
            player = "White" if self.chess.in_turn == 1 else "Black"
            print("Player in turn : " + player)
            player_input = input("From: ")
            if player_input == "end":
                print("Game forcefully ended")
                break
            if player_input == "print":
                continue
            if player_input == "moves":
                print(self.chess.legal_moves)
                continue
            try:
                frm = tuple(map(int, player_input.split(' ')))
            except ValueError:
                print("Illegal Input. Example of legal input: '2 2' to make a move from (2, 2)")
                continue
            player_input = input("To: ")
            try:
                to = tuple(map(int, player_input.split(' ')))
            except ValueError:
                print("Illegal Input. Example of legal input: '2 2' to make a move to (2, 2). Restarting move stuff. redo from step")
                continue
            success, msg = self.chess.move(frm, to)
            if not success:
                print("Human move failed with message: " + msg)
                continue

        print("Game ended. Winner = " + str(self.chess.winner))
        chess_util.print_board(self.chess.board)


if __name__ == '__main__':  # Does not work from PyCharm python console. Use terminal
    game = ChessGame()
    game.start()
