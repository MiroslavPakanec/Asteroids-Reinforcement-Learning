import pygame
import random
from typing import List
from game_objects.asteroid import Asteroid
from builders.asteroid_builder import AsteroidBuilder

class AsteroidController:
    def __init__(self, screen):
        self.screen = screen
        self.asteroids: List[Asteroid] = []
        self.respawn_freq_ms = 4000
        self.last_respawn_time = 0
        self.cleanup_count = 0
        self.limit = 20

    def hit(self, asteroid_idx: int, asteroid: Asteroid):
        self.asteroids.pop(asteroid_idx)
        if asteroid.level == 1:
            return
        else: 
            pass

    def step(self):
        current_time = pygame.time.get_ticks()
        for ai,asteroid in enumerate(self.asteroids):
            asteroid.step()
        
        if current_time < self.last_respawn_time + self.respawn_freq_ms or len(self.asteroids) >= self.limit:
            return
        
        self.last_respawn_time = current_time
        new_asteroid_level = random.randint(1,5)
        self.generate_asteroid(new_asteroid_level)

    def generate_asteroid(self, level, position=None, direction=None, speed=None):
        new_asteroid: Asteroid = AsteroidBuilder.generate_asteroid(self.screen, level, position, direction, speed)
        self.asteroids.append(new_asteroid)

    def render(self):
        for asteroid in self.asteroids:
            asteroid.render()