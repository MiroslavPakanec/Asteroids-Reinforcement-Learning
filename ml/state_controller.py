import numpy as np
import math
from game_objects.ship import SpaceShip
from controllers.asteroid_controller import AsteroidController
from shapely.geometry import Polygon, Point, LineString, LinearRing


def get_state(ship: SpaceShip, ac: AsteroidController, config):
    px, py = ship.position
    vx, vy = ship.direction
    r = ship.total_rotation % 360 / 360
    
    sensor_data = _get_sensor_data(ship, ac.asteroids)
    for i,_ in enumerate(sensor_data):
        sensor_data[i] = normilize_distance(sensor_data[i], config)

    px = normilize_distance(px, config)
    py = normilize_distance(py, config)
    vx = normilize_speed(vx)
    vy = normilize_speed(vy)

    
    x = [px, py, vx, vy, r] + sensor_data
    return np.array(x)
    

def normilize_distance(d, config):
    max_d = max(config['screen']['x'], config['screen']['y'])
    min_d = 0
    return (d - min_d) / (max_d - min_d) if d != -1 else -1

def normilize_speed(s):
    return (s - (-10)) / (10 - (-10))

def normilize_rotation(r):
    return 

def _get_sensor_data(ship, asteroids):
        seonsor_readings = []
        for s in ship.sensors:
            p1 = ship.position
            p2 = s
            line = LineString([p1, p2])
            seonsor_reading = -1
            for asteroid in asteroids:
                asteroid_polygon: Polygon = Polygon(asteroid.points)
                asteroid_ring = LinearRing(list(asteroid_polygon.exterior.coords))
                intersection = asteroid_ring.intersection(line)
                if intersection.is_empty is False:           
                    min_d = 10000 
                    intersection = [intersection] if isinstance(intersection, Point) else intersection
                    for p in intersection:
                        dx = p.x - p1[0]
                        dy = p.y - p1[1]
                        d = math.sqrt(dx**2 + dy**2)
                        min_d = min(min_d, d)
                    seonsor_reading = min_d
            seonsor_readings.append(seonsor_reading)
        return seonsor_readings