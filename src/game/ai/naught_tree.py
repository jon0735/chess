import naught_util


class Node:
    def __init__(self, move=None, score=None, board=None):
        self.children = []
        self.best_child = None
        if move is None:
            self.move_from_parent = None
        else:
            self.move_from_parent = move  # (move, by_player)
        if board is None:
            self.board = naught_util.get_empty_i1_board()
        else:
            self.board = board
        if score is None:
            self.score = None
        else:
            self.score = score

    def print_node(self):
        print("========================")
        print("Node Info:")
        print("Children length = " + str(len(self.children)))
        print("Best child = " + str(self.best_child))
        print("Move_from_parent = " + str(self.move_from_parent))
        print("Score = " + str(self.score))
        naught_util.print_board(self.board)
        print("========================")

    def get_all_boards(self):
        boards = []
        self.__add_boards(boards)
        return boards

    def __add_boards(self, boards, only_winner=False):
        boards.append(self.board)
        if self.score > -2:
            naught_util.print_board(self.board)
            print("With score: " + str(self.score))
        for i in range(len(self.children)):
            self.children[i].__add_boards(boards, only_winner=only_winner)



