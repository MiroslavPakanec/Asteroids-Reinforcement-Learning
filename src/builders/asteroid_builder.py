import math
import random
import numpy as np
from scipy.spatial import ConvexHull, Delaunay
from game_objects.asteroid import Asteroid

class AsteroidBuilder:
    @staticmethod
    def generate_asteroid(screen, config, level: int, position=None, direction=None, speed=None):
        size = level * 10
        points, position, direction = AsteroidBuilder.generate_asteroid_points(config, size, position, direction)
        hull = ConvexHull(points)
        corners = []
        for v in hull.vertices:
            p = points[v]
            corners.append((p[0], p[1]))
        if (speed is None):
            speed_factor = config['asteroid']['speed_factor']
            speed_factor_rand_min = config['asteroid']['min_random_speed_factor']
            speed_factor_rand_max = config['asteroid']['max_random_speed_factor']
            speed = random.randint(speed_factor_rand_min, speed_factor_rand_max) * speed_factor 
        return Asteroid(screen, config, position, corners, direction, speed, level)


    @staticmethod
    def generate_asteroid_points(config, size: int, position=None, direction=None):
        n = size
        screen_x = config['screen']['x']
        screen_y = config['screen']['y']

        spawn_dist = math.sqrt(screen_x*screen_x + screen_y*screen_y) * 0.7 # spawn / despawn circle

        if position is None:
            spawn_alpha = random.randint(0, 359)
            spawn_alpha_rad = spawn_alpha * math.pi / 180 # spawn angle rad
            spawn_circle_center = (screen_x / 2, screen_y / 2)
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