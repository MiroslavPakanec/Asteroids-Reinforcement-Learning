import sys
import torch
import traceback
import numpy as np
import matplotlib.image
from ml.memory import Memory
from ml.agent import DQN_Agent
from game import Asteroids
from ml.action_to_move_map import action_to_move

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

def train():
    EXPERIMENT_NAME = 'exp_8_ticks_reward_long'

    EPOCHS = 200000 # = number of games
    N_RENDER = 1000 # render each N games

    BUFFER_SIZE = 50000
    BATCH_SIZE = 32
    LR = 0.0001
    STATE_DIM = (128, 128) 
    ACTION_DIM = 18
    GAMMA = 0.99
    EPSILON = 1
    EPSILON_DECAY = 1e-6
    NETWORK_REPLACEMENT_FREQUENCY = 1000

    agent_memory = Memory(BUFFER_SIZE, STATE_DIM)
    agent = DQN_Agent(
        device=device,
        memory=agent_memory,
        gamma=GAMMA,
        lr=LR,
        epsilon=EPSILON,
        epsilon_decay=EPSILON_DECAY,
        replace_freq=NETWORK_REPLACEMENT_FREQUENCY,
        state_dim=STATE_DIM,
        action_dim=ACTION_DIM,
        batch_size=BATCH_SIZE
    )

    best_score = -np.inf
    scores, eps_history, game_losses = [], [], []
    print(f'--- TRAINING INITIALIZED with device {agent.network.device}')

    for i in range(EPOCHS):
        try:
            game = Asteroids()
            state = game.reset()
            
            score = 0
            done = False
            step = 0
            step_losses = []
            while not done:
                print(f'GAME {i+1}/{EPOCHS}, STEP: {step}, SCORE: {score}', end='\r')
                step += 1
                game.handle_exit_events()
                
                # step action selection and storing
                action = agent.choose_action(state)
                move = action_to_move(action)
                next_state, reward, done, error, ticks, _ = game.step(move)

                if error:
                    continue
                score += reward
                agent.store_transition(state, next_state, action, reward, done)
               
                # show game
                if i % N_RENDER == 0:
                    game.render()

                # step learning
                agent.learn()
                state = next_state
            
            scores.append(score)
            eps_history.append(agent.epsilon)
            avg_score = np.mean(scores[-20:])
            print(f'# game: {i+1}, score: {score}, avg score: {avg_score:.2f}, ticks: {ticks}, epsilon: {agent.epsilon:.2f}')

            if avg_score > best_score:
                best_score = avg_score if avg_score > best_score else best_score
                agent.save(EXPERIMENT_NAME, 'best_network')
            agent.save(EXPERIMENT_NAME, 'last_network')

            # save trining data
            np.save(f'./models/{EXPERIMENT_NAME}/scores.npy', np.array(scores))
            np.save(f'./models/{EXPERIMENT_NAME}/epsilon.npy', np.array(eps_history))
            np.save(f'./models/{EXPERIMENT_NAME}/game_losses.npy', np.array(game_losses))
        except Exception as e:
            print()
            print(e)
            print(traceback.format_exc())
            break


if __name__ == '__main__':
    train()