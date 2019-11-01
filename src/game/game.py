from naught_cross import NaughtCross
from ai import NaughtAI
import naught_util


class Game:
    def __init__(self, x=None, o=None):
        self.nc = NaughtCross()
        if x is None:
            self.x = None
        elif x == "Human":
            self.x = None
        elif x == "AI":
            self.x = NaughtAI(self.nc, player="X")
        else:
            raise ValueError("Input must be \"AI\" or \"Human\"")
        if o is None:
            self.o = None
        elif o == "Human":
            self.o = None
        elif o == "AI":
            self.o = NaughtAI(self.nc, player="O")
        else:
            raise ValueError("Input must be \"AI\" or \"Human\"")

    def start(self):
        start_string = "Game started. "
        if self.x is None:
            start_string = start_string + "X is played by a human. "
        else:
            start_string = start_string + "X is played by AI. "
        if self.o is None:
            start_string = start_string + "O is played by a human. "
        else:
            start_string = start_string + "O is played by AI. "
        print(start_string)

        turn = 1
        while self.nc.winner is None:
            player_symbol = self.nc.next
            print("Turn " + str(turn) + ". Next player: " + player_symbol)
            self.nc.print_board()
            if player_symbol == "X":
                in_turn = self.x
                other = self.o
            else:
                in_turn = self.o
                other = self.x
            if isinstance(in_turn, NaughtAI):
                success, move_with_player, msg = in_turn.make_move()
                move = move_with_player[0]
                if not success:
                    raise RuntimeError("For some reason the ai couldn't make a move. Message: " + msg)
                print("AI made move " + str(move) + " with message: " + msg)
                print("Expected board: ")
                naught_util.print_board(in_turn.expected_board)
                print("Actual board: ")
                naught_util.print_board(self.nc.board)
            else:
                player_input = input("Move: ")
                # move_tuple = None
                try:
                    move = tuple(map(int, player_input.split(' ')))
                except ValueError:
                    print("Illegal Input for move. Example of legal input: '2 2' to make the move (2, 2)")
                    continue
                success, msg = self.nc.make_move(move, player_symbol)
                if not success:
                    print("Human move failed with message: " + msg)
                    continue
            if isinstance(other, NaughtAI):
                success, msg = other.inform_opponent_move(move)
                if success:
                    print("Opponent ai informed of move with message: " + msg)
                else:
                    print("informing failed with message: " + msg)
                print("Expected board: ")
                naught_util.print_board(other.expected_board)
                print("Actual board: ")
                naught_util.print_board(self.nc.board)
            turn = turn + 1
            done, _ = naught_util.check_winner(self.nc.board)
            if done:
                break
        print("Game ended with winner: " + str(self.nc.winner))
        self.nc.print_board()


if __name__ == '__main__':
    game = Game(x="AI", o="AI")
    game.start()






