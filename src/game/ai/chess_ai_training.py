import easygui
import _thread as thread
import threading
import time
import sys
import numpy as np
import random
import copy
import json
import matplotlib.pyplot as plt
import csv 

sys.path.append("..")
from chess.chess import Chess
import chess.chess as chess_src
import chess.chess_util as chess_util

from neural_net import NeuralNet
import chess_ai


def train(continu=True, depth=1, rand_min=0.2, rand_max=1.0, lr_max=8e-5, lr_min=1e-6, reg = 0.005, num_threads=4): # add more parameters probably.
    if continu:
        nn = load_nn("latest")
        best_nn = load_nn("best")
    else:
        nn = NeuralNet()
        nn.init_net(input_size=386, output_size=1, hidden_size=1000, number_of_hidden=8)
        resets = 0
        while abs(nn.predict(chess_ai.chess_to_nn_input(Chess()))) > .1:
            nn = NeuralNet()
            nn.init_net(input_size=386, output_size=1, hidden_size=1000, number_of_hidden=8)
            resets += 1
        print("nn started. Start predict: ", nn.predict(chess_ai.chess_to_nn_input(Chess())), "after", resets, "resets")
        best_nn = copy.deepcopy(nn)
    # best_nn = load_nn("best") # crashes if no such nn is saved
    
    with open("logs/log.txt", "a") as log_file:
        log_file.write("\n=========== New Training Run ================\n")
    bool_dict = {"bool": True}
    ui_thread = threading.Thread(target=shutdown_gui_thread, args=(bool_dict, ))
    ui_thread.start()
    # thread.start_new_thread(shutdown_gui_thread, (bool_dict, )) # starts thread, which displays gui to allow for easy graceful shutdown.
    lr = lr_max

    result_counts = [1, 1, 1] 
    count = 0
    randomness = rand_max

    if continu:
        with open("saved_nns/progress.txt") as f:

            settings_dict = json.loads(f.read())
            result_counts = settings_dict["result_counts"]
            count = settings_dict["count"]
            lr = settings_dict["lr"]
            lr_min = settings_dict["lr_min"]
            randomness = settings_dict["rand"]
            rand_min = settings_dict["rand_min"]

            
    # else:
    #     result_counts = [1, 1, 1]  # index 0: counts of black wins, index 1: Ties, index 2: white wins
    #     count = 0

    while bool_dict["bool"]:  # This dict is given to the UI thread. This allows for stopping the training via UI

        result_list = [None] * num_threads
        threads = []
    
        for i in range(num_threads):
            # print("Starting thread", i)
            thread = threading.Thread(target=run_one_game, args=(nn, 
                                                                 randomness, 
                                                                 depth, 
                                                                 reg, 
                                                                 result_counts, 
                                                                 count + i, 
                                                                 i, 
                                                                 result_list,
                                                                 lr))
            threads.append(thread)
            thread.daemon = True
            thread.start()
        
        for thread in threads:
            thread.join()

        # print("All threads done")
        # print("TODO: merge thread results and update")  # TODO!
        
        avg_db = []  # Not actually taking the average. Just sum up (maybe reduce learning rate) 
        avg_dw = []
        for db, dw, res, print_string, cost_string in result_list:
            lr_factor = 1 - result_counts[res+1]/sum(result_counts)
            # print(res, lr_factor, result_counts)
            if not avg_db:
                avg_db = db
                avg_dw = dw
            else:
                for i in range(len(avg_db)):
                    avg_db[i] += db[i] * lr_factor
                    avg_dw[i] += dw[i] * lr_factor

            result_counts[res + 1] += 1
            if res == 1:
                cost_file_name = "logs/win_costs.csv"
            elif res == 0:
                cost_file_name = "logs/draw_costs.csv"
            else:
                cost_file_name = "logs/loss_costs.csv"

            print_string += ", lr_factor: " + str("{:.3f}".format(lr_factor)) 

            with open("logs/detailed_log.txt", "a") as log_file:
                log_file.write(print_string + "\n")
            with open(cost_file_name, "a") as cost_file:
                cost_file.write(cost_string)
            print(print_string)

        for i in range(len(avg_db)):
            avg_db[i] = avg_db[i] * (1/num_threads)
            avg_dw[i] = avg_dw[i] * (1/num_threads)

        nn.update_from_gradients(avg_db, avg_dw, lr=lr)
        
        count += num_threads
        if count > 200:
            randomness = max(rand_min, randomness * 0.995) # Reduce randomness a little each run, until it becomes less than rand_min
        if count > 400:
            lr = max(lr_min, lr * 0.995)
        # sum_val = np.sum(chess.board)
        # avg_cost = total_cost / chess.turn_num if count >= 200 else total_cost
        # print_string = ("Game " + str(count) 
        #                  + ", Avg Cost: " + str("{:.3f}".format(avg_cost[0])) 
        #                  + ", Last cost: " + str("{:.3f}".format(last_cost[0]))
        #                  + ", Turns: " + str(chess.turn_num) 
        #                  + ", Randomness:" + str("{:.2f}".format(randomness)) 
        #                  + ", lr:" + str("{:.5f}".format(lr)) 
        #                  + ", lr factor:" + str("{:.3f}".format(lr_factor)) 
        #                  + ", Win:" + str(result) 
        #                  + ", Sum: " + str(sum_val)
        #                  + ", Val:" + str("{:.4f}".format(val)) )
        
        # print(print_string)
        # with open("logs/detailed_log.txt", "a") as log_file:
        #     log_file.write(print_string + "\n")
        
        # if result == 1:
        #     cost_file_name = "logs/win_costs.csv"
        # elif result == 0:
        #     cost_file_name = "logs/draw_costs.csv"
        # else:
        #     cost_file_name = "logs/loss_costs.csv"

        # with open(cost_file_name, "a") as cost_file:
        #     cost_string = ( str(count) + "," 
        #                     + str(chess.turn_num) + "," 
        #                     + str(total_cost[0]) +  ","
        #                     + str(avg_cost[0]) + ","
        #                     + str(last_cost[0]) + "\n" )
        #     cost_file.write(cost_string)

        # TODO SAVE COSTS FOR GRAPHING LATER
        # print("Game", count, ", Total Cost:", "{:.2f}".format(total_cost[0]), "Last cost: ", cost, "Turns: ", chess.turn_num, ", Randomness:", "{:.2f}".format(randomness), ", lr:", "{:.4f}".format(lr), "lr factor:", "{:.3f}".format(lr_factor), ", Winner:", chess.winner, ", Val:", "{:.5f}".format(val))
        if count % 200 == 0: # every X games test and backup
            best_nn = test_and_backup(nn, best_nn, count)
    
    # test_and_backup(nn, best_nn, count)
    save_nn("latest", nn)
    with open("logs/log.txt", "a") as log_file:
        log_file.write("\n=========== Training Run Ended ================\n")
    settings = {"count": count, "result_counts": result_counts, "lr": lr, "lr_min": lr_min, "rand": randomness, "rand_min": rand_min}
    with open("saved_nns/progress.txt", "w") as f:
        f.write(json.dumps(settings))

    #     chess = Chess()
    #     states = []
    #     while chess.is_in_progress:
    #         val = None
    #         if chess.turn_num < 3 or random.random() < randomness:
    #             move = random.choice(chess.legal_moves)
    #         else:
    #             move, val = chess_ai.choose_move_ab(chess, depth=depth, eval_fun=chess_ai.nn_eval, nn=nn, randomize=False) # Consider saving val for later update (avoid redoing forward pass)
    #         chess.move(move)
    #         states.append(chess._efficient_copy())
    #     val = nn.predict(chess_ai.chess_to_nn_input(chess))[0]

    #     result = 0 if chess.winner is None else chess.winner 
    #     result_counts[result + 1] += 1

    #     total = sum(result_counts)
    #     # TODO reconsider this entire lr_factor approach
    #     lr_factor = (total - result_counts[result + 1]) / total
    #     total_cost = 0
    #     last_cost = None
    #     result_ = result
    #     avg_dw = None
    #     avg_db = None
    #     for i, state in enumerate(reversed(states)):
    #         if i > 0:
    #             result_ = result_ * .95  # TODO reconsider this
    #         nn_input = chess_ai.chess_to_nn_input(state)  
    #         cost, grad = nn.cost_grad(nn_input, result_, reg=reg)  # TODO reconsider weight decay (and check if it even works)
    #         if last_cost is None:
    #             last_cost = cost
    #         # lr2 = lr_factor * lr/(i+1) # TODO do this properly. 
    #         if avg_dw is None:
    #             avg_dw = grad["dw"]
    #             avg_db = grad["db"]
    #         else:
    #             avg_dw += [ grad_i / ((i+1)*(i+1)) for grad_i in grad["dw"] ]
    #             avg_db += [ grad_i / ((i+1)*(i+1)) for grad_i in grad["db"] ]
    #             # avg_db += grad["db"] / ((i+1)*(i+1))

    #         # nn.update_from_gradients(grad["db"], grad["dw"], lr2)
    #         # result_ = result_ * .95  # TODO reconsider this
    #         total_cost += cost
    #         if count < 200:
    #             break
    #     nn.update_from_gradients(avg_db, avg_dw, lr=lr*lr_factor) 

    #     avg_cost = total_cost / chess.turn_num if count >= 200 else total_cost
    #     count += 1
    #     if count > 200:
    #         randomness = max(rand_min, randomness * 0.995) # Reduce randomness a little each run, until it becomes less than rand_min
    #         lr = max(lr_min, lr * 0.995)
    #     sum_val = np.sum(chess.board)

    #     print_string = ("Game " + str(count) 
    #                      + ", Avg Cost: " + str("{:.3f}".format(avg_cost[0])) 
    #                      + ", Last cost: " + str("{:.3f}".format(last_cost[0]))
    #                      + ", Turns: " + str(chess.turn_num) 
    #                      + ", Randomness:" + str("{:.2f}".format(randomness)) 
    #                      + ", lr:" + str("{:.5f}".format(lr)) 
    #                      + ", lr factor:" + str("{:.3f}".format(lr_factor)) 
    #                      + ", Win:" + str(result) 
    #                      + ", Sum: " + str(sum_val)
    #                      + ", Val:" + str("{:.4f}".format(val)) )
        
    #     print(print_string)
    #     with open("logs/detailed_log.txt", "a") as log_file:
    #         log_file.write(print_string + "\n")
        
    #     if result == 1:
    #         cost_file_name = "logs/win_costs.csv"
    #     elif result == 0:
    #         cost_file_name = "logs/draw_costs.csv"
    #     else:
    #         cost_file_name = "logs/loss_costs.csv"

    #     with open(cost_file_name, "a") as cost_file:
    #         cost_string = ( str(count) + "," 
    #                         + str(chess.turn_num) + "," 
    #                         + str(total_cost[0]) +  ","
    #                         + str(avg_cost[0]) + ","
    #                         + str(last_cost[0]) + "\n" )
    #         cost_file.write(cost_string)

    #     # TODO SAVE COSTS FOR GRAPHING LATER
    #     # print("Game", count, ", Total Cost:", "{:.2f}".format(total_cost[0]), "Last cost: ", cost, "Turns: ", chess.turn_num, ", Randomness:", "{:.2f}".format(randomness), ", lr:", "{:.4f}".format(lr), "lr factor:", "{:.3f}".format(lr_factor), ", Winner:", chess.winner, ", Val:", "{:.5f}".format(val))
    #     if count % 200 == 0: # every X games test and backup
    #         best_nn = test_and_backup(nn, best_nn, count)
    
    # # test_and_backup(nn, best_nn, count)
    # save_nn("latest", nn)
    # with open("logs/log.txt", "a") as log_file:
    #     log_file.write("\n=========== Training Run Ended ================\n")
    # settings = {"count": count, "result_counts": result_counts}
    # with open("saved_nns/progress.txt", "w") as f:
    #     f.write(json.dumps(settings))


def run_one_game(nn, randomness, depth, reg, result_counts, count, thread_num, result_list, lr):
    chess = Chess()
    states = []
    while chess.is_in_progress:
        val = None
        if chess.turn_num < 3 or random.random() < randomness:
            move = random.choice(chess.legal_moves)
        else:
            move, val = chess_ai.choose_move_ab(chess, depth=depth, eval_fun=chess_ai.nn_eval, nn=nn, randomize=False) # Consider saving val for later update (avoid redoing forward pass)
        chess.move(move)
        states.append(chess._efficient_copy())
    val = nn.predict(chess_ai.chess_to_nn_input(chess))[0]

    result = 0 if chess.winner is None else chess.winner 
    # result_counts[result + 1] += 1

    total = sum(result_counts)
    # TODO reconsider this entire lr_factor approach
    # lr_factor = (total - result_counts[result + 1]) / total
    total_cost = 0
    last_cost = None
    result_ = result
    avg_dw = []
    avg_db = []
    for i, state in enumerate(reversed(states)):
        # if i > 0:
            # result_ = result_ * .95  # TODO reconsider this
        nn_input = chess_ai.chess_to_nn_input(state)  
        cost, grad = nn.cost_grad(nn_input, result_, reg=reg)  # TODO reconsider weight decay (and check if it even works (it does not right now. Disabled in neural_net.py))
        if last_cost is None:
            last_cost = cost
        # lr2 = lr_factor * lr/(i+1) # TODO do this properly. 
        total_cost += cost

        if not avg_dw:
            avg_dw = grad["dw"]
            avg_db = grad["db"]
        else:
            for j in range(len(avg_db)):
                avg_dw[j] += grad["dw"][j]/((i+1)*(i+1))
                avg_db[j] += grad["db"][j]/((i+1)*(i+1))

        if count < 200:
            break
    
    
    sum_val = np.sum(chess.board)
    avg_cost = total_cost / chess.turn_num if count >= 200 else total_cost
    print_string = ("Game " + str(count) 
                        + ", Avg Cost: " + str("{:.3f}".format(avg_cost[0])) 
                        + ", Last cost: " + str("{:.3f}".format(last_cost[0]))
                        + ", Turns: " + ((3-len(str(chess.turn_num))) * " ") + str(chess.turn_num) 
                        + ", Randomness: " + str("{:.2f}".format(randomness)) 
                        + ", lr: " + str("{:.3f}".format(lr*1e5)) + "e5" 
                        + ", Win: " + (str(result) if result < 0 else (" " + str(result)))
                        + ", Sum: " + ((2-len(str(abs(sum_val)))) * " ") + (str(sum_val)  if sum_val < 0 else (" " + str(sum_val)))
                        + ", Val: " + (str("{:.4f}".format(val))  if val < 0 else (" " + str("{:.4f}".format(val)))))
    
    # print(print_string)
    # with open("logs/detailed_log.txt", "a") as log_file:
    #     log_file.write(print_string + "\n")
    
    # if result == 1:
    #     cost_file_name = "logs/win_costs.csv"
    # elif result == 0:
    #     cost_file_name = "logs/draw_costs.csv"
    # else:
    #     cost_file_name = "logs/loss_costs.csv"

    # with open(cost_file_name, "a") as cost_file:
    cost_string = ( str(count) + "," 
                    + str(chess.turn_num) + "," 
                    + str(total_cost[0]) +  ","
                    + str(avg_cost[0]) + ","
                    + str(last_cost[0]) + "\n" )
        # cost_file.write(cost_string)


    result_list[thread_num] = (avg_db, avg_dw, result, print_string, cost_string)
    # print("Thread", thread_num, "done")
    


def test_and_backup(new_nn, best_nn, count, repetitions=4, save_to_files=True):
    print("test and backup started")
    t = time.time()
    string = str(t)
    save_nn("latest", new_nn)
    save_nn(string, new_nn)
    new_wins = 0
    best_wins = 0
    draws = 0

    for i in range(repetitions):
        chess = Chess()

        newest_starting = True if i % 2 == 0 else False
        newest_in_turn = True if newest_starting else False

        while chess.is_in_progress:
            nn = new_nn if newest_in_turn else best_nn  # Set the nn used in this round
            newest_in_turn = not newest_in_turn  # change bool value of if newest nn is in turn
            if chess.turn_num < 5: # random opening
                move = random.choice(chess.legal_moves)
            else:
                move, val = chess_ai.choose_move_ab(chess, depth=1, eval_fun=chess_ai.nn_eval, nn=nn, randomize=True)
            
            chess.move(move)
        
        if (newest_starting and chess.winner == 1) or (not newest_starting and chess.winner == -1):
            new_wins += 1
            win_string = "New"
        elif (newest_starting and chess.winner == -1) or (not newest_starting and chess.winner == 1):
            best_wins += 1
            win_string = "Best"
        else:
            draws += 1
            win_string = "None"

        print("Winner: ", win_string, ", Last value: ", val)
    
    print("New wins:", new_wins, ", Best wins:", best_wins, ", Draws:", draws)


    new_wins_sum = 0
    sum_wins = 0
    draws = 0

    for i in range(repetitions):
        chess = Chess()
        newest_starting = True if i % 2 == 0 else False
        newest_in_turn = True if newest_starting else False

        while chess.is_in_progress:
            if chess.turn_num < 5: #Random opening
                move = random.choice(chess.legal_moves)
            else:
                if newest_in_turn:
                    move, val = chess_ai.choose_move_ab(chess, depth=1, eval_fun=chess_ai.nn_eval, nn=nn, randomize=True) # TODO increase depth?
                else:
                    move, val = chess_ai.choose_move_ab(chess, depth=1, randomize=True)
            
            newest_in_turn = not newest_in_turn
            chess.move(move)

        if (newest_starting and chess.winner == 1) or (not newest_starting and chess.winner == -1):
            new_wins_sum += 1
            win_string = "New"
        elif (newest_starting and chess.winner == -1) or (not newest_starting and chess.winner == 1):
            sum_wins += 1
            win_string = "Sum"
        else:
            draws += 1
            win_string = "None"

        print("Winner: ", win_string, ", Last value: ", val)
    
    print("New wins:", new_wins_sum, ", Sum wins:", sum_wins, ", Draws:", draws)
    
    if save_to_files:
        with open("logs/log.txt", "a") as log_file:
            log_file.write("\n")
            log_file.write("Time: " + str(time.time()) + ", Count: " + str(count) + ", Repetitions: " + str(repetitions))
            log_file.write("\nNew Wins: " + str(new_wins) + ", Best Wins: " + str(best_wins))
            log_file.write("\nNew Wins: " + str(new_wins_sum) + ", Sum Wins: " + str(sum_wins))
            log_file.write("\n")

    # print("new wins: ", new_wins, ", best wins: ", best_wins)
    # print("new wins: ", new_wins_sum, ", sum wins: ", sum_wins)
    if new_wins > best_wins:
        save_nn("best", new_nn)
        return new_nn
    else:
        return copy.deepcopy(best_nn)


def save_nn(file_name, nn): 
    np.savez("saved_nns/" + file_name, W=nn.W, b=nn.b)


def load_nn(file_name):
    x = np.load("saved_nns/" + file_name + ".npz")
    return NeuralNet(W=x["W"], b=x["b"])


def shutdown_gui_thread(bool_dict):
    easygui.msgbox("Press \"OK\" to stop training (after completing current game)")
    bool_dict["bool"] = False # The infinite while lopp in train() is based on this bool


def plot_costs(points=100, use_all=False):
    win_costs = None
    loss_costs = None
    draw_costs = None
    with open("logs/win_costs.csv") as win_file:
        win_data = csv.reader(win_file, quoting=csv.QUOTE_NONNUMERIC)
        win_costs = np.array(list(win_data))
    with open("logs/loss_costs.csv") as loss_file:
        loss_data = csv.reader(loss_file, quoting=csv.QUOTE_NONNUMERIC)
        loss_costs = np.array(list(loss_data))
    with open("logs/draw_costs.csv") as draw_file:
        draw_data = csv.reader(draw_file, quoting=csv.QUOTE_NONNUMERIC)
        draw_costs = np.array(list(draw_data))
    titles = ["Win", "Loss", "Draw"]
    titles2 = ["total", "Avg", "Last"]
    figure_count = 1

    # print(win_costs)
    win_costs_reduced = []
    loss_costs_reduced = []
    draw_costs_reduced = []

    win_num_points = int(len(win_costs) / points)
    loss_num_points = int(len(loss_costs) / points)
    draw_num_points = int(len(draw_costs) / points)

    for i in range(points):
        win_costs_reduced.append(np.average(win_costs[i*win_num_points:(i+1)*win_num_points], axis=0))
        # print(win_costs[i*points:(i+1)*points])
        # print(np.average(win_costs[i*points:(i+1)*points], axis=0))
        # exit()
        loss_costs_reduced.append(np.average(loss_costs[i*loss_num_points:(i+1)*loss_num_points], axis=0))
        draw_costs_reduced.append(np.average(draw_costs[i*draw_num_points:(i+1)*draw_num_points], axis=0))
    
    win_costs_reduced = np.array(win_costs_reduced)
    loss_costs_reduced = np.array(loss_costs_reduced)
    draw_costs_reduced = np.array(draw_costs_reduced)

    # print(np.array(win_costs).shape, np.array(win_costs_reduced).shape)
    # print(type(win_costs), type(win_costs_reduced))
    if use_all:
        win_costs_reduced = win_costs
        loss_costs_reduced = loss_costs
        draw_costs_reduced = draw_costs


    for i, costs in enumerate([win_costs_reduced, loss_costs_reduced, draw_costs_reduced]):
        plt.figure(i+1)
        for j in range(3):
            ax = plt.subplot(1, 3, j+1)
            # plt.figure(3 * i + j)
            ax.scatter(costs[:, 0], costs[:, j + 2], s=1)
            ax.set_title(titles[i] + ", " + titles2[j])

    plt.show()

if __name__ == "__main__":
    # start training
    # train(continu=False)
    plot_costs(use_all=True)
    # print("FIX TESTING")
    # new_nn = load_nn("latest")
    # best_nn = load_nn("best")
    # test_and_backup(new_nn, best_nn, 0, repetitions=6, save_to_files=False)
    # TODO save settings: counts, lr, distribution and so on. 
    # TODO Save costs, s.t. it can be visualized*