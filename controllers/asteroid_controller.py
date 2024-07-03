import pygame
import random
from typing import List
from game_objects.asteroid import Asteroid
from builders.asteroid_builder import AsteroidBuilder

class AsteroidController:
    def __init__(self, screen, config):
        self.screen = screen
        self.init_config(config)
        self.reset()

    def step(self, tick):
        for ai,asteroid in enumerate(self.asteroids):
            asteroid.step()   
        if tick < self.last_respawn_time + self.respawn_frequency_ticks or len(self.asteroids) >= self.limit:
            return
        self.last_respawn_time = tick
        new_asteroid_level = random.randint(1,5)
        self.generate_asteroid(new_asteroid_level)

    def reset(self):
        self.asteroids = []
        self.last_respawn_time = 0 - self.respawn_frequency_ticks
    
    def render(self):
        for asteroid in self.asteroids:
            asteroid.render()

    def init_config(self, config):
        self.respawn_frequency_ticks = config['asteroid']['respawn_frequency_ticks']
        self.limit = config['asteroid']['limit']
        self.config = config

    def hit(self, asteroid_idx: int, asteroid: Asteroid):
        self.asteroids.pop(asteroid_idx)
        if asteroid.level == 1:
            return
        else: 
            pass

    def generate_asteroid(self, level, position=None, direction=None, speed=None):
        new_asteroid: Asteroid = AsteroidBuilder.generate_asteroid(self.screen, self.config, level, position, direction, speed)
        self.asteroids.append(new_asteroid)