import random
import numpy as np

class MemoryController:
    def __init__(self, size=10000):
        self.size = size
        self._idx = 0
        self.storage = []

    def add(self, state, next_state, action, reward, done):
        if self._idx >= self.size:
            self._idx = 0
        self.storage[self._idx] = [state, next_state, action, reward, done]
        self._idx += 1

    def sample(self, batch_size):
        sample_indexes = self._get_sample_indexes(batch_size)
        b_states, b_next_states, b_actions, b_rewards, b_dones = [], [], [], [], []
        for i in sample_indexes:
            state, next_state, action, reward, done = self._storage[i]
            b_states.append(np.array(state, copy=False))
            b_next_states.append(np.array(next_state, copy=False))
            b_actions.append(np.array(action, copy=False))
            b_rewards.append(np.array(reward, copy=False))
            b_dones.append(np.array(done, copy=False))
        return np.array(b_states), np.array(b_next_states), np.array(b_actions), np.array(b_rewards), np.array(b_dones).reshape(-1,1)

    
    def _get_sample_indexes(self, batch_size):
        if self.size <= batch_size:
            raise 'You are trying to sample more than you have...'
        sample_idxs = []
        while len(sample_idxs) < batch_size:
            idx = random.randint(0, self.size-1)
            if idx in sample_idxs or self._storage[idx] == None:
                continue
            sample_idxs.append(idx)
        return sample_idxs