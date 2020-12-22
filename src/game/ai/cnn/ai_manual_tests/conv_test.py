import torch
import torch.nn as nn
import numpy as np
# import os

# import sys
# sys.path.append(os.getcwd())
# print(sys.path)

from game.ai.cnn.cnn_v1 import Chess_cnn_v1
from game.chess.chess import Chess
import game.ai.chess_ai.chess_ai as chess_ai



conv_nn = Chess_cnn_v1()

conv_nn.cuda()

x1 = torch.randn(1, 12, 8, 8)
x3 = torch.randn(1, 12, 8, 8)

# print(x1)
# print(x1[0][3])
x2 = torch.randn(2)
x1 = x1.cuda()
x2 = x2.cuda()
x3 = x3.cuda()
# x5 = torch.randn(4)
# x6 = torch.randn(2)
# x7 = torch.cat((x5, x6), 0)
# print(x1)
# print(x6)
# print(x7)

# print("cuda available", torch.cuda.is_available())
# print("input cuda: ", x.is_cuda)

# print(type(x1))

# print(conv_nn(x1, x2))

# r1 = conv_nn(x1, x2)
# r2 = conv_nn(x3, x2)
# print("r1:", r1, "r2:", r2)
# print("r1 < r2 ?: ", r1 < r2)

# if r1 < r2:
#     print("true")
# else:
#     print("false")

chess = Chess()

cnn_input, lin_input = chess_ai.chess_to_cnn_input(chess)

# print(cnn_input)
# print(lin_input)

cnn_input = cnn_input.cuda()
lin_input = lin_input.cuda()

print(conv_nn(cnn_input, lin_input))