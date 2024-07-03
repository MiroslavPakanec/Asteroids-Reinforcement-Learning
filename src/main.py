import sys
import json
import torch
import pygame
import traceback

from colors import Colors
from game_objects.ship import SpaceShip
from controllers.asteroid_controller import AsteroidController
from controllers.colision_controller import ColisionController
from ml.state_controller import get_state

FPS = 60

def initialize(config):
    pygame.init()
    pygame.display.set_caption('MP Ateroids')
    screen_x = config['screen']['x']
    screen_y = config['screen']['y']
    screen = pygame.display.set_mode((screen_x, screen_y))
    return screen

def load_config():
    path = '/workspace/src/config.json'
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def handle_exit_events():
    for event in pygame.event.get():
        if event.type == 256:
            raise Exception('Game exit.')
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        raise Exception('Game exit.')

def handle_reset_event(score: int, last_score: int, ticks: int, ship: SpaceShip, asteroid_controller: AsteroidController, hit: bool):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_p] or ticks == 0 or hit:
        config = load_config()
        ship.reset()
        asteroid_controller.reset()
        return 0, score, 0
    return score, last_score, ticks

def get_actions():
    actions = [None, None, None, None, None] # [W, D, A, SPACE, CTRL]
    keys = pygame.key.get_pressed()
    actions[0] = 1 if keys[pygame.K_w] else 0
    actions[1] = 1 if keys[pygame.K_d] else 0
    actions[2] = 1 if keys[pygame.K_a] else 0
    actions[3] = 1 if keys[pygame.K_SPACE] else 0
    actions[4] = 1 if keys[pygame.K_LCTRL] else 0
    return actions

def main():
    config = load_config()
    screen = initialize(config)   
    clock = pygame.time.Clock()
    font = pygame.freetype.Font('/workspace/src/fonts/atari.ttf', 15)
    ticks = 0
    score = 0
    last_score = 0
    hit = False
    
    try:
        ship: SpaceShip = SpaceShip(screen, config)
        asteroid_controller = AsteroidController(screen, config)

        while True:
            screen.fill(Colors.BACKGROUND)
            
            handle_exit_events()
            score, last_score, ticks = handle_reset_event(score, last_score, ticks, ship, asteroid_controller, hit)

            actions = get_actions()
            ship.step(actions, ticks)
            asteroid_controller.step(tick=ticks)
            ticks += 1

            score += ColisionController.check_asteroid_projectile(asteroid_controller, ship)
            hit = ColisionController.check_asteroid_ship(asteroid_controller, ship)
            state = get_state(ship, asteroid_controller, config)

            ship.render()
            asteroid_controller.render()
            font.render_to(screen, (10, 10), f'Score: {score}', Colors.PINK)
            font.render_to(screen, (10, 30), f'Last Score: {last_score}', Colors.PINK)
            font.render_to(screen, (10, 50), f'Ticks: {ticks}', Colors.PINK)

            pygame.display.flip()
            clock.tick(FPS)

    except Exception as e:
        print(traceback.format_exc())
        print(e)
        pygame.quit()
        
    

if __name__ == '__main__':
    main()  