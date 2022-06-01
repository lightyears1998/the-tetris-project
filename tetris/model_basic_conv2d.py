import torch.nn as nn
import torch.nn.functional as F
from config import device


class DQNBasicConv2d(nn.Module):
    def __init__(self, h, w, out_size):
        super(DQNBasicConv2d, self).__init__()
        self.conv1 = nn.Conv2d(2, 8, kernel_size=3, stride=1)
        self.bn1 = nn.BatchNorm2d(8)
        self.conv2 = nn.Conv2d(8, 16, kernel_size=3, stride=1)
        self.bn2 = nn.BatchNorm2d(16)
        self.conv3 = nn.Conv2d(16, 16, kernel_size=3, stride=1)
        self.bn3 = nn.BatchNorm2d(16)

        def conv2d_out_size(size, kernel_size=3, stride=1):
            return (size - (kernel_size - 1) - 1) // stride + 1

        conv_w = conv2d_out_size(conv2d_out_size(conv2d_out_size(w)))
        conv_h = conv2d_out_size(conv2d_out_size(conv2d_out_size(h)))
        linear_input_size = conv_w * conv_h * 16
        self.head = nn.Linear(linear_input_size, out_size)

    def forward(self, x):
        x = x.to(device)
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.relu(self.bn3(self.conv3(x)))
        return self.head(x.view(x.size(0), -1))


if __name__ == "__main__":
    from game import *
    model = DQNBasicConv2d(GAME_ROWS, GAME_COLS, GAME_ACTIONS)
    print(model)