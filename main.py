import json
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
    path = './config.json'
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
        ship.reset(config)
        asteroid_controller.reset(config)
        return 0, score, 0
    return score, last_score, ticks


def main():
    config = load_config()
    screen = initialize(config)   
    clock = pygame.time.Clock()
    font = pygame.freetype.Font('./fonts/atari.ttf', 15)
    ticks = 0
    score = 0
    last_score = 0
    hit = False
    
    try:
        ship: SpaceShip = SpaceShip(screen)
        asteroid_controller = AsteroidController(screen)

        while True:
            screen.fill(Colors.BACKGROUND)
            
            handle_exit_events()
            score, last_score, ticks = handle_reset_event(score, last_score, ticks, ship, asteroid_controller, hit)

            ship.step()
            asteroid_controller.step()
            ticks += 1

            score += ColisionController.check_asteroid_projectile(asteroid_controller, ship)
            hit = ColisionController.check_asteroid_ship(asteroid_controller, ship)
            state = get_state(ship, asteroid_controller, config)

            print(state.shape)

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