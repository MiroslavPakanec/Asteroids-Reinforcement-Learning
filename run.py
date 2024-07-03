import random
import pygame
from game import Asteroids 

game = Asteroids()
game.reset()
game.render()

def get_actions():
    actions = [None, None, None, None, None] # [W, D, A, SPACE, CTRL]
    keys = pygame.key.get_pressed()
    actions[0] = 1 if keys[pygame.K_w] else 0
    actions[1] = 1 if keys[pygame.K_d] else 0
    actions[2] = 1 if keys[pygame.K_a] else 0
    actions[3] = 1 if keys[pygame.K_SPACE] else 0
    actions[4] = 1 if keys[pygame.K_LCTRL] else 0
    return actions

def get_random_actions():
    actions = [None, None, None, None, None] # [W, D, A, SPACE, CTRL]
    actions[0] = random.randint(0,1)
    actions[1] = random.randint(0,1)
    actions[2] = random.randint(0,1)
    actions[3] = random.randint(0,1)
    actions[4] = random.randint(0,1)
    return actions

def handle_exit_events():
    for event in pygame.event.get():
        if event.type == 256:
            raise Exception('Game exit.')
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        raise Exception('Game exit.')

# GAMES LOOP
while True:
    done = False
    #GAME LOOP
    while not done:
        handle_exit_events()
        actions = get_actions()
        # actions = get_random_actions()
        
        state, reward, done, error, ticks, score = game.step(actions)
        print(f'SCORE: {score} | TICKS: {ticks}', end='\r')
        game.render()
    print(50*' ')
    game.reset()