import numpy as np


def relu(x):
    zeros = np.zeros(x.shape)
    res = np.maximum(x, zeros)
    return res


def d_relu(x):
    return np.where(x > 0, 1, 0)


def tanh(x):
    return (np.exp(x) - np.exp(-x)) / (np.exp(x) + np.exp(-x))


def d_tanh(x):
    return 1 - np.square(tanh(x))


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def d_sigmoid(x):
    sig = tanh(x)
    return sig * (1 - sig)


def cross_entropy(y, y_real):  # Only use when real values are 0 or 1
    if y_real == 0:
        if y > 1 - 1e-7:
            y = 1 - 1e-7
        return np.log(1-y)
    elif y_real == 1:
        if y < 1e-7:
            y = 1e-7
        return np.log(y)
    else:
        raise ValueError("Real values must be 0 or 1. Otherwise use different cost function")


def mse(y, real):
    return np.square(real - y)


def d_mse(y, real):
    return y-real








def state_to_input(i1_board, is_in_turn, player):
    x = np.reshape(i1_board, i1_board.size)
    if player == -1 or player == 'O':  # Assumes nn is trained with 1 meaning "my piece" and -1 meaning "opponent piece"
        x = x * -1
    x = np.append(x, 1 if is_in_turn else 0)
    return x

