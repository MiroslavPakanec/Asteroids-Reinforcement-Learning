import numpy as np
import math
import pygame
import sys
import matplotlib.image
from game_objects.ship import SpaceShip
from controllers.asteroid_controller import AsteroidController
from shapely.geometry import Polygon, Point, LineString, LinearRing
from colors import Colors
from skimage.transform import resize

def get_state_img(screen):
    state = pygame.PixelArray(screen)
    state = np.array(np.array(state)) # 0 - 663070
    state = resize(state, (128, 128), preserve_range=True, anti_aliasing=True)
    state = state/16777215
    return state

def get_state(ship: SpaceShip, ac: AsteroidController, config):
    px, py = ship.position
    vx, vy = ship.direction
    r = ship.total_rotation % 360 / 360
    sensor_data = _get_sensor_data(ship, ac.asteroids)

    sensor_input = []
    for i,_ in enumerate(sensor_data):
        px_normilized = normilize_distance(sensor_data[i][0], config, with_none=True)
        py_normilized = normilize_distance(sensor_data[i][1], config, with_none=True)
        sensor_input.extend([px_normilized, py_normilized])

    px = normilize_distance(px, config)
    py = normilize_distance(py, config)
    vx = normilize_speed(vx)
    vy = normilize_speed(vy)

    x = [px, py, vx, vy, r] + sensor_input
    return np.array(x)
    

def normilize_distance(d, config, with_none=False):
    if with_none and d == -1:
        return -1
    max_d = max(config['screen']['x'], config['screen']['y'])
    min_d = 0
    n = (d - min_d) / (max_d - min_d) if d != -1 else -1
    return 0 if n < 0 else 1 if n > 1 else n

def normilize_speed(s):
    min = -20
    max = 20
    n = (s - min) / (max - min)
    return 0 if n < 0 else 1 if n > 1 else n


def _get_sensor_data(ship, asteroids):
        seonsor_readings = []
        for s in ship.sensors:
            p1 = ship.position
            p2 = s
            line = LineString([p1, p2])
            seonsor_reading = (-1, -1)
            for asteroid in asteroids:
                asteroid_polygon: Polygon = Polygon(asteroid.points)
                asteroid_ring = LinearRing(list(asteroid_polygon.exterior.coords))
                intersection = asteroid_ring.intersection(line)
                if intersection.is_empty is False:           
                    min_d = 10000 
                    min_p = None
                    intersection = [intersection] if isinstance(intersection, Point) else intersection
                    for p in intersection.geoms:
                        dx = p.x - p1[0]
                        dy = p.y - p1[1]
                        d = math.sqrt(dx**2 + dy**2)
                        if min_d > d:
                            min_d = d
                            min_p = (p.x, p.y)
                    seonsor_reading = min_p
            seonsor_readings.append(seonsor_reading)
        return seonsor_readings