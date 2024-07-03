import sys
import torch
import numpy as np
from torch import nn
import torch.optim as optim

class DQN(nn.Module):
    def __init__(self, state_dim, action_dim, lr, device):
        super(DQN,self).__init__()
        
        self.conv1 = nn.Conv2d(1, 32, 8, stride=4)
        self.conv2 = nn.Conv2d(32, 64, 4, stride=2)
        self.conv3 = nn.Conv2d(64, 64, 3, stride=1)
        self.fc1 = nn.Linear(9216, 512)
        self.fc2 = nn.Linear(512, action_dim)

        self.optimizer = optim.RMSprop(self.parameters(), lr=lr)
        self.loss = nn.MSELoss()
        self.device = device
        self.to(self.device)

    # def calculate_conv_output_dims(self, input_dims):
    #     state = torch.zeros(1, *input_dims)
    #     dims = self.conv1(state)
    #     dims = self.conv2(dims)
    #     dims = self.conv3(dims)
    #     return int(np.prod(dims.size()))

    def preprocess(self, x):
        x = torch.tensor(x, dtype=torch.float)
        x = x.to(self.device)
        return x

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = torch.relu(self.conv3(x))
        x = torch.flatten(x, start_dim=1)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x



        # x = torch.relu(self.layer_1(x))
        # x = torch.relu(self.layer_2(x))
        # x = torch.relu(self.layer_3(x))
        # x = x.view(x.size()[0], -1)
        # return x