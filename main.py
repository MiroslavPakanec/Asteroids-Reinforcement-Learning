import ast
import enum
from os import stat
from turtle import position
from gym import Space
import pygame
from pygame import Surface
from typing import Tuple, List
import traceback
import math
import random
from scipy.spatial import ConvexHull, Delaunay
import numpy as np
import time


SCREEN_X = 1000
SCREEN_Y = 1000
FPS = 60

class Colors:
    BACKGROUND = (30,30,30)
    RED = (255,0,0)
    GREEN = (0,255,0)
    BLUE = (0,0,255)


class Projectile:
    def __init__(self, screen, spawn_position, rotation):
        self.screen: Surface = screen 
        self.position = spawn_position
        self.image_path = 'projectile_1'
        self.direction = self.get_projectile_vector(rotation)
        self.speed = 0.005
        self.w = 4
        self.h = 4
    
    def get_projectile_vector(self, rotation):
        radar_len = 2000
        x = self.position[0] + math.cos(math.radians(rotation - 90)) * radar_len * -1
        y = self.position[1] + math.sin(math.radians(rotation - 90)) * radar_len
        # pygame.draw.line(screen, Colors.GREEN, self.position, (x,y), 1)
        return (x,y)

    def set_position(self):
        inc_x = (self.position[0] - self.direction[0]) * self.speed 
        inc_y = (self.position[1] - self.direction[1]) * self.speed

        new_x = self.position[0] + inc_x * -1
        new_y = self.position[1] + inc_y * -1

        self.position = (new_x, new_y)    

    def is_out_of_window(self):
        return (
            self.position[0] < 0 or 
            self.position[0] > SCREEN_X or 
            self.position[1] < 0 or 
            self.position[1] > SCREEN_Y
        )

    def step(self):
        self.set_position()

    def render(self):
        file_path = get_image_path(self.image_path)
        img = pygame.image.load(file_path)
        img = pygame.transform.scale(img, (self.w, self.h))
        self.screen.blit(img, self.position)

class SpaceShip:
    def __init__(self, 
        screen: Surface, 
        name: str, 
        spawn_position: Tuple[int, int]):
        self.w = 44
        self.h = 68
        self.acceleration_time = 0
        self.max_acceleration_time = 20
        self.min_acceleration_time = 0
        self.boost = False
        self.rotation = 0
        self.position = spawn_position
        self.set_image_path()
        self.screen = screen
        self.name = name
        self.speed: Tuple[int, int] = (0,0)
        self.speed_factor = 0.06
        self.boost_speec_factor = 0.36
        self.rotation_factor = 3
        self.projectiles: List[Projectile] = []

    def set_image_path(self):
        if self.boost:
            self.image_path = 'spaceship_4'
            return

        if self.acceleration_time == 0:
            self.image_path = 'spaceship_0'
        elif self.acceleration_time < 3:
            self.image_path = 'spaceship_1'
        elif self.acceleration_time < 9:
            self.image_path = 'spaceship_2'
        else:
            self.image_path = 'spaceship_3'

    def set_rotation(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rotation += 1 * self.rotation_factor
        if keys[pygame.K_d]:
            self.rotation -= 1 * self.rotation_factor

    def set_boost(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.acceleration_time > 15:
            self.boost = True
        else:
            self.boost = False

    def set_speed(self):
        keys = pygame.key.get_pressed()
        sx, sy = self.speed[0], self.speed[1]
        sx_inc, sy_inc = 0, 0
        
        rel_rot = self.rotation % 360
        x_from, x_to, y_from, y_to, r_from, r_to = -1, -1, -1, -1, -1, -1
        if rel_rot <= 90: # <0 - 90>  
            x_from, x_to = 0, -1
            y_from, y_to = -1, 0
            r_from, r_to = 0, 90
        elif rel_rot <= 180: # (90, 180>
            x_from, x_to = -1, 0
            y_from, y_to = 0, 1
            r_from, r_to = 91, 180
        elif rel_rot <= 270: # (180, 270>
            x_from, x_to = 0, 1
            y_from, y_to = 1, 0
            r_from, r_to = 181, 270
        else: # (270, 360)
            r_from, r_to = 271, 359
            x_from, x_to = 1, 0
            y_from, y_to = 0, -1

        if keys[pygame.K_w]:
            sx_inc = translate(rel_rot, r_from, r_to, x_from, x_to)
            sy_inc = translate(rel_rot, r_from, r_to, y_from, y_to)
        
        if self.boost:
            speed_factor = self.boost_speec_factor
        else:
            speed_factor = self.speed_factor
    
        self.speed = (sx + sx_inc * self.speed_factor, sy + sy_inc * speed_factor)
    
    def set_position(self):
        pos_x, pos_y = self.position[0], self.position[1]
        if pos_x < 0:
            pos_x = SCREEN_X
        if pos_x > SCREEN_X:
            pos_x = 0
        if pos_y < 0:
            pos_y = SCREEN_Y
        if pos_y > SCREEN_Y:
            pos_y = 0

        new_pos_x = pos_x + self.speed[0]
        new_pos_y = pos_y + self.speed[1]
        self.position = (new_pos_x, new_pos_y)

    def set_acceleration_time(self):
        keys = pygame.key.get_pressed()
        new_acc = 0
        if keys[pygame.K_w]:
            new_acc = min(self.acceleration_time + 1, self.max_acceleration_time)
        else:
            new_acc = max(self.acceleration_time - 1, self.min_acceleration_time)
        self.acceleration_time = new_acc
        

    def get_projectile_points(self, tx, ty):
        ox = self.position[0] + self.w - tx
        oy = self.position[1] + self.h - ty
        cx = self.position[0] + self.w / 2
        cy = self.position[1] + self.h / 2
        d_oc_x, d_oc_y = cx-ox, cy-oy
        d_oc = math.sqrt(d_oc_x*d_oc_x + d_oc_y*d_oc_y) 
        d_cp = d_oc
        alpha_rad = (360 * math.pi / 180) - (self.rotation * math.pi / 180)
        left_px = cx - (d_cp * math.cos(alpha_rad))
        left_py = cy - (d_cp * math.sin(alpha_rad))
        right_px = cx + (d_cp * math.cos(alpha_rad))
        right_py = cy + (d_cp * math.sin(alpha_rad))
        # pygame.draw.line(self.screen, Colors.RED, self.position, (ox, oy), 1)
        # pygame.draw.line(self.screen, Colors.RED, self.position, (cx, cy), 1)
        # pygame.draw.line(self.screen, Colors.RED, self.position, (left_px, right_py), 1)
        # pygame.draw.line(self.screen, Colors.RED, self.position, (right_px, right_py), 1)
        return [(left_px, left_py), (right_px, right_py)]

    def set_shooting(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LCTRL]:
            pygame.draw.circle(self.screen, Colors.BLUE, self.position, 1)
            left_p, right_p = self.get_projectile_points(20, 17)
            projectile_left = Projectile(self.screen, left_p, self.rotation)
            projectile_right = Projectile(self.screen, right_p, self.rotation)
            self.projectiles.append(projectile_left)
            self.projectiles.append(projectile_right)


    def step(self):
        self.set_acceleration_time()
        self.set_rotation()
        self.set_boost()
        self.set_image_path()
        self.set_speed()
        self.set_position()
        self.set_shooting()

        new_projectiles = []
        for projectile in self.projectiles:
            if projectile.is_out_of_window():
                continue
            projectile.step()
            new_projectiles.append(projectile)
        self.projectiles = new_projectiles
        
    def render(self):
        file_path = get_image_path(self.image_path)
        img = pygame.image.load(file_path)
        img = pygame.transform.scale(img, (self.w, self.h))

        img_rect_center = img.get_rect(topleft = (self.position[0],self.position[1])).center       
        img_rotated = pygame.transform.rotate(img, self.rotation)
        img_rotated_rect = img_rotated.get_rect(center=img_rect_center)
        self.screen.blit(img_rotated, img_rotated_rect)        
        
        for projectile in self.projectiles:
            projectile.render()

def initialize():
    pygame.init()
    pygame.display.set_caption('MP Ateroids')
    screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
    return screen

def handle_exit_events():
    for event in pygame.event.get():
        if event.type == 256:
            raise Exception('Game exit.')
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        raise Exception('Game exit.')


def translate(value, leftMin, leftMax, rightMin, rightMax):
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    valueScaled = float(value - leftMin) / float(leftSpan)
    return rightMin + (valueScaled * rightSpan)

def get_image_path(name):
    return f'./images/{name}.png'

def build_space_ship(screen):
    w = 44
    h = 56
    x = SCREEN_X / 2 - w / 2
    y = SCREEN_Y / 2 - h / 2
    return SpaceShip(
        screen, 
        'ship',
        (x, y)
    )

class Asteroid:
    def __init__(self, screen, position, points, direction):
        self.screen = screen
        self.position = position
        self.original_position = position
        self.points = points # points of convex hull
        self.direction = direction
        self.rotation = random.uniform(0.1, 1) * math.pi / 180
        self.speed = random.randint(1, 100) * 0.0001
        self.hits = 0
        self.durability = len(self.points) * 10

    def hit(self):
        self.hits += 1
        if self.hits >= self.durability:
            return True # destroy
        return False

    def rotate_point(self, center, point, angle):
        new_x = math.cos(angle) * (point[0]-center[0]) - math.sin(angle) * (point[1]-center[1]) + center[0]
        new_y = math.sin(angle) * (point[0]-center[0]) + math.cos(angle) * (point[1]-center[1]) + center[1]
        return (new_x, new_y)

    def get_trajectory_percentage(self):
        d_to_origin_x = self.position[0] - self.original_position[0]
        d_to_origin_y = self.position[1] - self.original_position[1]
        d_to_target_x = self.position[0] - self.direction[0]
        d_to_target_y = self.position[1] - self.direction[1]
        d_to_origin = math.sqrt((d_to_origin_x*d_to_origin_x)+(d_to_origin_y*d_to_origin_y))
        d_to_target = math.sqrt((d_to_target_x*d_to_target_x)+(d_to_target_y*d_to_target_y))
        d_total = d_to_origin + d_to_target
        return d_to_origin / d_total

    def step(self):
        new_x = self.position[0] + self.direction[0] * self.speed
        new_y = self.position[1] + self.direction[1] * self.speed
        self.position = (new_x, new_y)
        new_points = []
        for p in self.points:
            new_x = p[0]+self.direction[0]*self.speed
            new_y = p[1]+self.direction[1]*self.speed
            # new_rotated = self.rotate_point(center=self.position, point=(new_x, new_y), angle=self.rotation)
            new_rotated = (new_x, new_y)
            new_points.append(new_rotated)
        self.points = new_points
        return

    def render(self):
        pygame.draw.line(screen, Colors.RED, self.original_position, self.direction, 1)
        for i,_ in enumerate(self.points):
            pygame.draw.line(screen, Colors.GREEN, self.points[i], self.position, 1)
            if i == 0:
                pygame.draw.line(screen, Colors.GREEN, self.points[i], self.points[len(self.points) - 1], 1)
                continue
            pygame.draw.line(screen, Colors.GREEN, self.points[i-1], self.points[i], 1)
        pygame.draw.circle(screen, Colors.BLUE, self.position, 5)

class AsteroidBuilder:
    @staticmethod
    def generate_asteroid(screen):
        size = random.randint(5, 100)
        points, position, direction = np.array(AsteroidBuilder.generate_asteroid_points(size))
        hull = ConvexHull(points)
        corners = []
        for v in hull.vertices:
            p = points[v]
            corners.append((p[0], p[1]))
        return Asteroid(screen, position, corners, direction)


    @staticmethod
    def generate_asteroid_points(size: int):
        n = size
        spawn_d = math.sqrt(SCREEN_X*SCREEN_X + SCREEN_Y*SCREEN_Y) * 0.7 # spawn circle
        direction_d = math.sqrt(SCREEN_X*SCREEN_X + SCREEN_Y*SCREEN_Y) * 0.7 # direction circle

        spawn_alpha = random.randint(0, 359)
        spawn_alpha_rad = spawn_alpha * math.pi / 180 # spawn angle rad
        spawn_circle_center = (SCREEN_X / 2, SCREEN_Y / 2)
        spawn_x = spawn_circle_center[0] + (spawn_d * math.cos(spawn_alpha_rad))
        spawn_y = spawn_circle_center[1] + (spawn_d * math.sin(spawn_alpha_rad))
        
        direction_alpha_rad = (spawn_alpha-random.randint(175, 185)) * math.pi / 180
        direction_x = spawn_circle_center[0] + (direction_d * math.cos(direction_alpha_rad))
        direction_y = spawn_circle_center[1] + (direction_d * math.sin(direction_alpha_rad))

        P = []
        orbits = np.random.normal(size/5, size, n)
        for o in orbits:
            alpha = random.randint(0, 359)
            alpha_rad = alpha * math.pi / 180
            px = round(spawn_x - (o * math.cos(alpha_rad)))
            py = round(spawn_y - (o * math.sin(alpha_rad)))
            P.append((px, py))
        return P, (spawn_x, spawn_y), (direction_x, direction_y)

class AsteroidController:
    def __init__(self, screen):
        self.screen = screen
        self.asteroids: List[Asteroid] = []
        self.respawn_freq_ms = 200
        self.last_respawn_time = 0
        self.cleanup_count = 0

    def step(self, curent_time):
        for ai,asteroid in enumerate(self.asteroids):
            can_be_removed = asteroid.step()
            if can_be_removed:
                self.asteroids.pop(ai)
        
        if curent_time < self.last_respawn_time + self.respawn_freq_ms:
            return
        
        # clean up
        # for ai,asteroid in enumerate(self.asteroids):
        #     trajectory_percent = asteroid.get_trajectory_percentage()
        #     if trajectory_percent > 0.8:
        #         self.asteroids.pop(ai)
        #         self.cleanup_count += 1
        # print(f'{len(self.asteroids)} {self.cleanup_count}')

        # for i,asteroid in enumerate(self.asteroids):
        #     print(f'{i} {asteroid.direction}')
        # print('---')

        if len(self.asteroids) > 5:
            return

        self.last_respawn_time = curent_time
        new_asteroid: Asteroid = AsteroidBuilder.generate_asteroid(self.screen)
        self.asteroids.append(new_asteroid)


    def render(self):
        for asteroid in self.asteroids:
            asteroid.render()

class ColisionDetector:
    @staticmethod
    def asteroid_projectile(ac: AsteroidController, ship: SpaceShip):
        for ai,asteroid in enumerate(ac.asteroids):

            for pi, projectile in enumerate(ship.projectiles):
                if ColisionDetector.is_inside_polygon(asteroid.points, projectile.position):
                    ship.projectiles.pop(pi)
                    destroyed: bool = asteroid.hit()
                    if destroyed:
                        try:
                            ac.asteroids.pop(ai)
                        except:
                            pass
    
    @staticmethod
    def is_inside_polygon(vertices, point):
        orientation_left = None
        for i,_ in enumerate(vertices):
            if i == 0:
                continue
            left: bool = ColisionDetector.isLeft(vertices[i-1], vertices[i], point)
            if orientation_left is None:
                orientation_left = left
                continue
            if orientation_left != left:
                return False
        return True
    
    @staticmethod
    def isLeft(a, b, c):
     return ((b[0] - a[0])*(c[1] - a[1]) - (b[1] - a[1])*(c[0] - a[0])) > 0


def main(screen):
    try:
        clock = pygame.time.Clock()
        ship = build_space_ship(screen)
        asteroid_controller = AsteroidController(screen)

        while True:
            handle_exit_events()
            screen.fill(Colors.BACKGROUND)

            ship.step()
            asteroid_controller.step(pygame.time.get_ticks())

            ColisionDetector.asteroid_projectile(asteroid_controller, ship)

            ship.render()
            asteroid_controller.render()

            pygame.display.flip()
            clock.tick(FPS)

    except Exception as e:
        print(traceback.format_exc())
        print(e)
        pygame.quit()
        
    

if __name__ == '__main__':
    screen = initialize()   
    main(screen)