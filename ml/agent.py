import os
import sys
import torch
import random
import matplotlib
import numpy as np
from ml.model import DQN

class DQN_Agent:
    def __init__(self, memory, device, gamma, epsilon, lr, state_dim, action_dim, batch_size, replace_freq, epsilon_min=0.01, epsilon_decay=5e-7):
        assert 0 <= epsilon <= 1

        self.device = device
        self.memory = memory
        self.gamma=gamma
        self.lr=lr
        self.state_dim=state_dim
        self.action_dim=action_dim
        self.batch_size=batch_size
        self.replace_freq=replace_freq
        self.epsilon=epsilon
        self.epsilon_min=epsilon_min
        self.epsilon_decay=epsilon_decay

        self.network: DQN = DQN(state_dim, action_dim, self.lr, self.device)
        self.network_next: DQN = DQN(state_dim, action_dim, self.lr, self.device)
        self.learn_step_counter = 0

    def choose_action(self, state):
        predict_action: bool = np.random.random() > self.epsilon
        if predict_action:
            return self._predict_action(state)
        else:
            return np.random.choice(self.action_dim)

    # def _choose_random_action(self):
    #     actions = [None, None, None, None, None] # [W, D, A, SPACE, CTRL]
    #     actions[0] = random.randint(0,1)
    #     actions[1] = random.randint(0,1)
    #     actions[2] = random.randint(0,1)
    #     actions[3] = random.randint(0,1)
    #     actions[4] = random.randint(0,1)
    #     return np.array(actions)

    # def _predict_action(self, state):
    #     x = np.array([state])
    #     x = self.network.preprocess(x)
    #     ys = self.network.forward(x)[0] # all actions (excluding batch dim)
    #     ys = torch.round(ys)
    #     ys = ys.to(torch.int)
    #     ys = ys.to('cpu')
    #     ys = ys.detach().numpy()
    #     return ys

    def _predict_action(self, state):
        x = np.array([state])
        x = self.network.preprocess(x)
        x = torch.unsqueeze(x, 0)
        actions = self.network.forward(x) # all actions (excluding batch dim)
        actions = actions[0] # exclude batch dim
        action = torch.argmax(actions).item()
        return action

    def store_transition(self, state, next_state, actions, reward, done):
        self.memory.add(state, next_state, actions, reward, done)

    def _replace_target_network(self):
        if self.learn_step_counter % self.replace_freq == 0:
            self.network_next.load_state_dict(self.network.state_dict())
    
    def _decrement_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon -= self.epsilon_decay
        else:
            self.epsilon = self.epsilon_min
    
    def save(self, experiment_name, name):
        path = f'models/{experiment_name}'
        if os.path.exists(path) is False:
            os.makedirs(path)
        torch.save(self.network.state_dict(), f'{path}/{name}.pt')
        torch.save(self.network_next.state_dict(), f'{path}/{name}_next')

    def learn(self):
        if self.memory.count < self.batch_size:
            return

        self.network.optimizer.zero_grad()
        self._replace_target_network()

        states, next_states, actions, rewards, dones = self.memory.sample(self.batch_size)
        actions = torch.as_tensor(actions, dtype=torch.long).to(self.device)
        rewards = torch.as_tensor(rewards, dtype=torch.long).to(self.device)
        dones = torch.as_tensor(dones, dtype=torch.bool).to(self.device)

        states = self.network.preprocess(states)
        states = states.unsqueeze(dim=1)
        q_pred = self.network.forward(states)
        indices = torch.arange(self.batch_size)
        q_pred = q_pred[indices, actions]
        
        next_states = self.network_next.preprocess(states)
        q_next = self.network_next.forward(next_states).max(dim=1)[0]
        q_next[dones] = 0.0

        q_target = rewards + self.gamma*q_next
        loss = self.network.loss(q_target, q_pred).to(self.device)
        loss.backward()
        self.network.optimizer.step()
        self.learn_step_counter += 1
        self._decrement_epsilon()