import torch
import torch.nn as nn

m = nn.AdaptiveAvgPool2d((5,7))
input = torch.randn(1, 64, 8, 9)
print(input.size())
output = m(input)
print(output.size())

# target output size of 7x7 (square)
m = nn.AdaptiveAvgPool2d(7)
input = torch.randn(1, 64, 10, 9)
print(input.size())
output = m(input)
print(output.size())

m = nn.AdaptiveAvgPool2d(1)
input = torch.randn(1, 64, 10, 9)
print(input.size())
output = m(input)
print(output.size())

# target output size of 10x7
m = nn.AdaptiveAvgPool2d((None, 7))
input = torch.randn(1, 64, 10, 9)
output = m(input)