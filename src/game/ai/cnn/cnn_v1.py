import torch
import torch.nn as nn

class Chess_cnn_v1(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv_network = nn.Sequential(
            nn.Conv2d(in_channels=12, out_channels=64, kernel_size=5, padding=2),
            nn.LeakyReLU(0.1),
            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, padding=1),
            nn.LeakyReLU(0.1),
            nn.MaxPool2d(2),  # dimensions to 4x4
            nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, padding=1),
            nn.LeakyReLU(0.1),
            nn.MaxPool2d(2),  # dimensions to 2x2
            nn.Conv2d(in_channels=256, out_channels=510, kernel_size=3, padding=1),
            nn.LeakyReLU(0.1),
            nn.MaxPool2d(2),  # dimensions to 1x1
        )
        self.avg_pool = nn.AdaptiveAvgPool2d(1)  # In case other wierd input format has been used
        self.linear_network = nn.Sequential(
            nn.Linear(512, 512),
            nn.LeakyReLU(.1),
            nn.Linear(512, 512),
            nn.LeakyReLU(.1),
            nn.Linear(512, 1),
            nn.Tanh()
        )

    # x is representation of board. y is additional features (in_turn, draw_counter)
    def forward(self, x, y):
        x = self.conv_network(x)
        x = self.avg_pool(x)
        x = torch.flatten(x)
        x = torch.cat((x, y), 0)
        x = self.linear_network(x)
        return x
