import torch
import torch.nn as nn
# import os

# import sys
# sys.path.append(os.getcwd())
# print(sys.path)

from game.ai.cnn_v1 import Chess_cnn_v1
from game.chess.chess import Chess



conv_nn = Chess_cnn_v1()

x = torch.randn(1, 12, 8, 8)

print(conv_nn(x))
