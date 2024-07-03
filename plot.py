import numpy as np
import matplotlib.pyplot as plt 

EXPERIMENT_NAME = 'exp_7_ticks_reward'
PATH = f'./models/{EXPERIMENT_NAME}'

epsilon = np.load(f'{PATH}/epsilon.npy')
scores = np.load(f'{PATH}/scores.npy')
x = list(range(len(scores)))

figure, axis = plt.subplots(2, figsize=(8, 8))
plt.subplots_adjust(hspace=1)

axis[0].plot(x, scores)
axis[0].set_title("Reward")
axis[1].plot(x, epsilon)
axis[1].set_title("Epsilon") 
plt.show()