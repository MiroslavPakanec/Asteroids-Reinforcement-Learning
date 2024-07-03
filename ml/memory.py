import sys
import random
import numpy as np

class Memory:
    def __init__(self, max_size, state_dim):
        self.size = max_size
        self.count = 0
        self.state_memory = np.zeros((self.size, *state_dim), dtype=np.float32)
        self.next_state_memory = np.zeros((self.size, *state_dim), dtype=np.float32)
        self.action_memory = np.zeros(self.size, dtype=np.int32)
        self.reward_memory = np.zeros(self.size, dtype=np.int32)
        self.terminal_memory = np.zeros(self.size, dtype=np.bool)

    def add(self, state, next_state, action, reward, done):
        index = self.count % self.size
        self.state_memory[index] = state
        self.next_state_memory[index] = next_state
        self.action_memory[index] = action
        self.reward_memory[index] = reward
        self.terminal_memory[index] = done
        self.count += 1

    def sample(self, batch_size):
        max_memory = min(self.count, self.size)
        batch = np.random.choice(max_memory, batch_size, replace=False)
        states = self.state_memory[batch]
        next_states = self.next_state_memory[batch]
        actions = self.action_memory[batch]
        rewards = self.reward_memory[batch]
        dones = self.terminal_memory[batch]
        return states, next_states, actions, rewards, dones