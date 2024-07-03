from pygame import Surface
import pygame
from colors import Colors

class Projectile:
    def __init__(self, screen, config, spawn_position, direction):
        self.screen: Surface = screen
        self.config = config
        self.position = spawn_position
        self.direction = direction
        self.speed = config['projectile']['speed_factor']

    def step(self):
        self.position = self.inc_position()

    def render(self):
        pygame.draw.line(self.screen, Colors.RED, self.position, self.inc_position())

    def inc_position(self):
        x = self.position[0] + self.direction[0] * self.speed
        y = self.position[1] + self.direction[1] * self.speed
        return x, y

    def get_position(self):
        return self.inc_position()