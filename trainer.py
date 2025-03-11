# this class handles training the model with experience replay
import torch
import torch.nn as nn
import torch.optim as optim
import random 
import torch.nn.functional as F
import numpy as np


class QTrainer:
    def __init__(self, gamma, lr, model):
        self.gamma = gamma
        self.lr = lr
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.loss_function = nn.MSELoss()

    
    def experienced_learning(self, state, action, reward, next_state, done):
        # [n , x] n for batch size
        state = torch.tensor((state), dtype=torch.float)
        next_state = torch.tensor((next_state), dtype=torch.float)
        action = torch.tensor((action), dtype=torch.long)
        reward = torch.tensor((reward), dtype=torch.float)

        # [1,x]
        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )
        
        # Predict Q-value for the current state
        pred = self.model(state)

        # clone the prediction to update Q value 
        target = pred.clone()

        # loop over done because its a simple tuple 
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            # update correct q value in target 
            target[idx][torch.argmax(action[idx]).item()] = Q_new

        # Calculate loss and optimize
        self.optimizer.zero_grad()
        loss = self.loss_function(target, pred)
        loss.backward()
        self.optimizer.step()
