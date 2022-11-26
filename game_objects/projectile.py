from pygame import Surface
import pygame
import math
from colors import Colors
from window import Window

SCREEN_X = 1000
SCREEN_Y = 1000
PROJECTILE_LASERS = True

class Projectile:
    def __init__(self, screen, spawn_position, direction):
        self.screen: Surface = screen 
        self.position = spawn_position
        self.direction = direction
        self.speed = 0.005
        # self.position_inc = self.get_position_increment_vector(rotation, self.speed)
    
    # def get_position_increment_vector(self, rotation, speed):
    #     vector_len = 2000
    #     direction_x = self.position[0] + math.cos(math.radians(rotation - 90)) * vector_len * -1
    #     direction_y = self.position[1] + math.sin(math.radians(rotation - 90)) * vector_len
    #     direction = (direction_x, direction_y)
    #     if PROJECTILE_LASERS:
    #         pygame.draw.line(self.screen, Colors.GREEN, self.position, direction, 1)
        
        # inc_x = (self.position[0] - direction[0]) * speed 
        # inc_y = (self.position[1] - direction[1]) * speed
        # return (inc_x, inc_y)

    # def get_direction_vector(self):
    #     direction_x = self.position[0] - self.position_inc[0] / self.speed
    #     direction_y = self.position[1] - self.position_inc[1] / self.speed
    #     return (direction_x, direction_y)

    def inc_position(self):
        x = self.position[0] + self.direction[0]
        y = self.position[1] + self.direction[1]
        return x, y

    def get_position(self):
        return self.inc_position()

    def step(self):
        self.position = self.inc_position()

    def render(self):
        pygame.draw.line(self.screen, Colors.RED, self.position, self.inc_position())