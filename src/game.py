import sys
import json
import math
import pygame 
import matplotlib.image
from ml.state_controller import get_state, get_state_img
from game_objects.ship import SpaceShip
from controllers.asteroid_controller import AsteroidController
from controllers.colision_controller import ColisionController
from colors import Colors

class Asteroids:
    def __init__(self):
        self.init_config()
        self.init_screen() 
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.font = pygame.freetype.Font('./fonts/atari.ttf', 15)
    
        self.ship: SpaceShip = SpaceShip(self.screen, self.config)
        self.asteroid_controller = AsteroidController(self.screen, self.config)

    def init_config(self):
        path = './config.json'
        with open(path, 'r') as f:
            data = json.load(f)
        self.config = data

    def init_screen(self):
        assert self.config is not None, 'Config has not been initialized. Call init_config before calling init_screen'
        pygame.init()
        pygame.display.set_caption('MP Ateroids')
        screen_x = self.config['screen']['x']
        screen_y = self.config['screen']['y']
        screen = pygame.display.set_mode((screen_x, screen_y))
        self.screen = screen

    def reset(self):
        self.ticks = 0
        self.total_score = 0
        self.last_score = 0
        self.hit = False
        
        self.ship.reset()
        self.asteroid_controller.reset()
        
        state = get_state_img(self.ship.screen)
        return state


    def step(self, move): # -> state, reward, done
        try:
            self.ticks += 1
            self.ship.step(move, self.ticks)
            self.asteroid_controller.step(self.ticks)
            
            # reward: int = ColisionController.check_asteroid_projectile(self.asteroid_controller, self.ship)
            reward: int = self.ticks
            done: bool = ColisionController.check_asteroid_ship(self.asteroid_controller, self.ship)
            state = get_state_img(self.ship.screen)
            self.total_score += reward
            
            # if self.ticks % 100 == 0:
            #     matplotlib.image.imsave(f'run_images/new_{self.ticks}.png', state)

            return (
                state,
                reward,
                done,
                False,
                self.ticks,
                self.total_score
            )
        except Exception as e:
            print()
            print(e)
            return (
                None,
                0,
                True,
                True,
                0,
                self.total_score
            )


    def render(self):
        # display_score = f'_{abs(self.total_score)}' if self.total_score < 0 else self.total_score
        self.screen.fill(Colors.BACKGROUND)
        self.ship.render()
        self.asteroid_controller.render()
        # self.font.render_to(self.screen, (10, 10), f'Score: {display_score}', Colors.PINK)
        # self.font.render_to(self.screen, (10, 50), f'Ticks: {self.ticks}', Colors.PINK)

        pygame.display.flip()
        self.clock.tick(self.FPS)

    def handle_exit_events(self):
        for event in pygame.event.get():
            if event.type == 256:
                raise Exception('Game exit.')
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            raise Exception('Game exit.')        
