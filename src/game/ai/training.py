from nc_nn import NaughtCrossNeuralNet
from ai import NaughtAI
from naught_cross import NaughtCross
import naught_util
import nn_util
import ai_strats
import numpy as np


def train(rounds, nn=None, lr=0.02, test_rounds=10):

    if nn is None:
        nn = NaughtCrossNeuralNet()
        nn.init_net(input_size=10, number_of_hidden=40, hidden_size=50, output_size=1)

    # test_stuff(nn)
    test_ai = NaughtAI(NaughtCross(), player='X')
    start_tree = ai_strats._build_state_tree(test_ai)
    ai_strats._min_max_tree(test_ai, start_tree)

    for r in range(rounds):
        if r % 2 == 0:
            nc = NaughtCross(starting_player='X')
            ai1 = NaughtAI(nc, player='X', nn=nn, strat="nn", depth=2)
            ai2 = NaughtAI(nc, player='O', nn=nn, strat="nn", depth=2)
            starting = 1
        else:
            nc = NaughtCross(starting_player='O')
            ai1 = NaughtAI(nc, player='O', nn=nn, strat="nn", depth=2)
            ai2 = NaughtAI(nc, player='X', nn=nn, strat="nn", depth=2)
            starting = -1

        ongoing = True
        states = []
        rand = 1.0 - r / rounds
        if rand < .2:
            rand = .2
        moves = []
        while ongoing:
            ai_in_turn = ai1 if nc.next == ai1.player else ai2
            _, move, _ = ai_in_turn.make_move(rand=rand)
            moves.append(move[0])
            states.append(naught_util.char_to_i1_board(nc.board))
            ongoing = nc.game_in_progress

        winner = nc.winner
        in_turn = naught_util.to_i1(winner) if winner is not None else starting  # Gives wrong. Is changed in for loop
        loss = 0
        p = 1
        score_before = nn.predict(nn_util.state_to_input(naught_util.char_to_i1_board(nc.board), not(in_turn == p), p))

        if r / rounds < .3:
            lr2 = lr
        else:
            lr2 = lr * (1 - r/rounds)

        for j, state in enumerate(reversed(states)):  #reversed(list(enumerate(states))):
            in_turn = in_turn * -1

            x = nn_util.state_to_input(state, in_turn == p, p)
            if winner is None:
                real = 0
            elif naught_util.to_i1(winner) == p:
                real = 1
            else:
                real = -1
            cost, result = nn.cost_grad(x, real)
            loss = loss + cost
            new_db = result['db']
            new_dw = result['dw']
            db = new_db * 1 / np.square(j + 1)
            dw = new_dw * 1 / np.square(j + 1)
            nn.update_from_gradients(db, dw, lr=lr2)  # (1 - r / rounds) * 0.2

            # if db is None:
            #
            # else:
            #     for k in range(len(dw)):
            #         dw[k] = dw[k] + new_dw[k]  # * 1/np.square(j + 1)
            #         db[k] = db[k] + new_db[k]  # * 1/np.square(j + 1)
            # break
                    # db = db + result['db'] * 1/(j + 1)
                    # dw = dw + result['dw'] * 1/(j + 1)
        # lr2 = lr
        in_turn = naught_util.to_i1(winner) if winner is not None else starting
        score_after = nn.predict(nn_util.state_to_input(naught_util.char_to_i1_board(nc.board), not(in_turn == p), p))
        # if r % 500 == 0:
        #     print()
        #     naught_util.print_board(nc.board)
        #     print("Round", r, ", Before score: ", score_before, ", After score: ", score_after)

        # nn.update_from_gradients(db, dw, lr=lr2)  # (1 - r / rounds) * 0.2
        winner2 = winner if winner is not None else 'N'
        tie = 'T' if winner is None else 'F'
        if r % 1000 == 0:
            print("winner at round ", r, ":", winner2, ", started: ", 'X' if starting == 1 else 'O', ", Tie = ", tie, "Loss:", loss, "moves:", moves)

        # if r % 100 == 0:
        #     test_against_deterministic(nn, start_tree)


    test_stuff(nn)
    test_against_deterministic(nn, start_tree, times=test_rounds)
        # print("lr = ", 0.5 * 1/(r+1), "Loss:", loss)
        # print("Loss:", loss)


def test_stuff(nn):
    nc = NaughtCross(starting_player='X')
    ai1 = NaughtAI(nc, player='X', nn=nn, strat="nn", depth=2)
    ai2 = NaughtAI(nc, player='O', nn=nn, strat="nn", depth=2)
    for board in naught_util.get_boards():
        won, winner = naught_util.check_winner(board)
        if won:
            x_in_turn = naught_util.to_i1(winner) == -1
        else:
            x_in_turn = True
        # winner = naught_util.to_i1(naught_util.check_winner(board))
        x_score = ai_strats.nn_score(ai1, board, x_in_turn)
        y_score = ai_strats.nn_score(ai2, board, not x_in_turn)
        naught_util.print_board(board)
        print("x score: ", x_score, ", o score: ", y_score, ", winner:", winner, ", x in turn:", x_in_turn)


def test_against_deterministic(nn, tree, times=10):
    print("Test starting")
    losses = 0
    ties = 0
    for i in range(times):
        nc = NaughtCross(starting_player='X')
        if i % 2 == 0:
            print("NN playing first as X")
            ai1 = NaughtAI(nc, player='X', nn=nn, strat="nn", depth=2)
            ai2 = NaughtAI(nc, player='O')
        else:
            print("NN playing second as O")
            ai1 = NaughtAI(nc, player='X')
            ai2 = NaughtAI(nc, player='O', nn=nn, strat="nn", depth=2)
            ai1.tree = tree
        while nc.game_in_progress:
            if nc.next == 'X':
                # print("X making move")
                current_ai = ai1
                other_ai = ai2
            else:
                # print("O making move")
                current_ai = ai2
                other_ai = ai1
            success, move, msg = current_ai.make_move()
            if not success:
                raise ValueError("Fuck")
            other_ai.inform_opponent_move(move)
        print("Winner " + str(i) + " = ", nc.winner)
        if nc.winner is None:
            ties = ties + 1
        else:
            losses = losses + 1
    print("Test: Ties = ", ties, ", losses = ", losses)

if __name__ == "__main__":
    train(50000, test_rounds=100)

# TODO Normalize gradients. Right now more moves leads to larger gradient + error


