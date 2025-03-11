import torch
import torch.nn as nn
import torch.optim as optim
import random 
import torch.nn.functional as F

class QNet(nn.Module):
    def __init__(self, input_size,hidden_size,output_size):
        # initialize super class
        super().__init__()
        # initialize layers 
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))  # activation function for hidden layers
        x = self.fc3(x)  # no activation in the final layer since we need raw Q-values
        return x


