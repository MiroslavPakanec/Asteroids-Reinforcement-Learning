import math
import random
import numpy as np
from scipy.spatial import ConvexHull, Delaunay
from game_objects.asteroid import Asteroid

SCREEN_X = 1000
SCREEN_Y = 1000
ASTEROID_SPEED_FACTOR = 0.00001
ASTTEROID_SPEED_RANDOM_MIN = 1
ASTTEROID_SPEED_RANDOM_MAX = 100

class AsteroidBuilder:
    @staticmethod
    def generate_asteroid(screen, level: int, position=None, direction=None, speed=None):
        size = level * 10
        points, position, direction = np.array(AsteroidBuilder.generate_asteroid_points(size, position, direction))
        hull = ConvexHull(points)
        corners = []
        for v in hull.vertices:
            p = points[v]
            corners.append((p[0], p[1]))
        if (speed is None):
            speed = random.randint(ASTTEROID_SPEED_RANDOM_MIN, ASTTEROID_SPEED_RANDOM_MAX) * ASTEROID_SPEED_FACTOR 
        return Asteroid(screen, position, corners, direction, speed, level)


    @staticmethod
    def generate_asteroid_points(size: int, position=None, direction=None):
        n = size
        spawn_dist = math.sqrt(SCREEN_X*SCREEN_X + SCREEN_Y*SCREEN_Y) * 0.7 # spawn / despawn circle

        if position is None:
            spawn_alpha = random.randint(0, 359)
            spawn_alpha_rad = spawn_alpha * math.pi / 180 # spawn angle rad
            spawn_circle_center = (SCREEN_X / 2, SCREEN_Y / 2)
            spawn_x = spawn_circle_center[0] + (spawn_dist * math.cos(spawn_alpha_rad))
            spawn_y = spawn_circle_center[1] + (spawn_dist * math.sin(spawn_alpha_rad))
            position = (spawn_x,spawn_y)

        if direction is None:
            direction_alpha_increment = 180  # random.randint(140, 220)
            direction_alpha_rad = (spawn_alpha-direction_alpha_increment) * math.pi / 180
            direction_x = spawn_circle_center[0] + (spawn_dist * math.cos(direction_alpha_rad))
            direction_y = spawn_circle_center[1] + (spawn_dist * math.sin(direction_alpha_rad))
            direction = (direction_x, direction_y)

        P = []
        orbits = np.random.normal(size/5, size, n)
        for o in orbits:
            alpha = random.randint(0, 359)
            alpha_rad = alpha * math.pi / 180
            px = round(position[0] - (o * math.cos(alpha_rad)))
            py = round(position[1] - (o * math.sin(alpha_rad)))
            P.append((px, py))
        return P, position, direction