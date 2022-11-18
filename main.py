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
from shapely.geometry import Polygon, Point

SCREEN_X = 1000
SCREEN_Y = 1000
FPS = 60

class Colors:
    BACKGROUND = (30,30,30)
    RED = (255,0,0)
    GREEN = (0,255,0)
    BLUE = (0,0,255)
    YELLOW = (255,255,0)


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
        pygame.draw.line(screen, Colors.GREEN, self.position, (x,y), 1)
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
        self.shooting_freq = 200
        self.last_shooting_time = 0

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
        current_time = pygame.time.get_ticks()
        if keys[pygame.K_LCTRL] and current_time > self.last_shooting_time + self.shooting_freq:
            self.last_shooting_time = current_time
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
    def __init__(self, screen, position, points, direction, level):
        self.screen = screen
        self.position = position
        self.original_position = position
        self.points = points # points of convex hull
        self.direction = direction
        self.rotation = random.uniform(0.1, 1) * math.pi / 180
        self.speed = 0.0001 # random.randint(1, 100) * 0.0001
        self.level = level

        self.t, self.b, self.l, self.r = False, False, False, False # is translation over edge
        self.transform_t = lambda p : (p[0], p[1] - SCREEN_Y + 100)
        self.transformed_points = []

        self.inc_x = (direction[0] - position[0]) * self.speed
        self.inc_y = (direction[1] - position[1]) * self.speed

        #temp
        self.H = (0,0)
        self.O = (0,0)
        self.C = (0,0)

    def rotate_point(self, center, point, angle):
        new_x = math.cos(angle) * (point[0]-center[0]) - math.sin(angle) * (point[1]-center[1]) + center[0]
        new_y = math.sin(angle) * (point[0]-center[0]) + math.cos(angle) * (point[1]-center[1]) + center[1]
        return (new_x, new_y)

    def get_center_of_mass(self):
        P = Polygon(self.points)
        return P.centroid.coords[0]

    def translate_asteroid(self, center, points, c_trans_func, p_trans_func):
        target_points = []        
        target_center = c_trans_func(center)
        for p in points:
            np = p_trans_func(center, p)
            target_points.append(np)
        return target_center, target_points


    def translate_over_edge(self, center, points):
        buffer = 100
        min_x, min_y = 0 - buffer, 0 - buffer
        max_x, max_y = SCREEN_X + buffer, SCREEN_Y + buffer
        if (center[1] < min_y):
            p_trans_func = lambda c, p: (p[0], max_y - (c[1] - p[1]))
            c_trans_func = lambda c: (c[0], max_y)
            return self.translate_asteroid(center, points, c_trans_func, p_trans_func)
        if (center[1] > max_y):
            p_trans_func = lambda c, p: (p[0], min_y - (c[1] - p[1]))
            c_trans_func = lambda c: (c[0], min_y)
            return self.translate_asteroid(center, points, c_trans_func, p_trans_func)
        if (center[0] < min_x):
            p_trans_func = lambda c, p: (max_x - (c[0] - p[0]), p[1])
            c_trans_func = lambda c: (max_x, c[1])
            return self.translate_asteroid(center, points, c_trans_func, p_trans_func)
        if (center[0] > max_x):
            p_trans_func = lambda c, p: (min_x - (c[0] - p[0]), p[1])
            c_trans_func = lambda c: (min_x, c[1])
            return self.translate_asteroid(center, points, c_trans_func, p_trans_func)

        return center, points

    def step(self):
        new_center_point = (self.position[0] + self.inc_x, self.position[1] + self.inc_y)
        new_points = []
        for p in self.points:
            np = (p[0] + self.inc_x, p[1] + self.inc_y)
            np = self.rotate_point(center=self.position, point=np, angle=self.rotation)
            new_points.append(np)

        new_center_point, new_points = self.translate_over_edge(new_center_point, new_points)
        self.position = new_center_point
        self.points = new_points


    def generate_hit_point(self):
        p1 = self.points[self.hit_vertex_idx-1]
        p2 = self.points[self.hit_vertex_idx]
        u = self.hit_point_percent
        x = (1-u)*p1[0] + u*p2[0]
        y = (1-u)*p1[1] + u*p2[1]
        return (x,y)

    def hit(self, hit_point, hit_direction):
        # compute Center C, hit point H and projectile origin O
        Hx, Hy = hit_point
        Dx, Dy = hit_direction
        dist_x, dist_y = (Hx-Dx) * 0.1, (Hy-Dy) * 0.1
        Ox, Oy = Hx+dist_x, Hy+dist_y
        Cx, Cy = self.get_center_of_mass()
        self.O, self.H, self.C = (Ox, Oy), (Hx, Hy), (Cx, Cy)
        d = (Hx - Cx, Hy - Cy)
        h = (Hx - Ox, Hy - Oy)

        # compute hit angle alha (direct hit adds no rotation, side hit rotates more)
        alpha = math.acos((d[0]*h[0]+d[1]*h[1])/(math.sqrt(d[0]*d[0]+d[1]*d[1])*math.sqrt(h[0]*h[0]+h[1]*h[1])))
        alpha_deg = alpha*180/math.pi
        hit_angle_factor = alpha_deg / 90 if alpha_deg <= 90 else abs(alpha_deg - 180) / 90
        
        # compute alhpa orientation - rotation clockwise and anti clockwise
        orientation = (Hy - Oy)*(Cx - Hx) - (Cy - Hy)*(Hx - Ox)
        hit_orientation_fac = -1 if (orientation > 0) else 0 if orientation == 0 else 1

        # compute distance from center of mass (linear with rotation increment)
        dist_from_center_of_mass = math.sqrt(d[0]*d[0]+d[1]*d[1])
        
        R = dist_from_center_of_mass * hit_angle_factor * hit_orientation_fac * 0.0001
        self.rotation += R

        # push 
        push_x, push_y = d[0] * 0.01, d[1] * 0.01
        self.inc_x -= push_x 
        self.inc_y -= push_y


    def render(self):
        pygame.draw.polygon(self.screen, Colors.GREEN, self.points)
        for i,p in enumerate(self.points):
            for j, p in enumerate(self.points):
                pygame.draw.line(self.screen, Colors.RED, self.points[i], self.points[j])

class AsteroidBuilder:
    @staticmethod
    def generate_asteroid(screen):
        size = 50 #random.randint(5, 100)
        points, position, direction = np.array(AsteroidBuilder.generate_asteroid_points(size))
        hull = ConvexHull(points)
        corners = []
        for v in hull.vertices:
            p = points[v]
            corners.append((p[0], p[1]))
        return Asteroid(screen, position, corners, direction, level=size/10)


    @staticmethod
    def generate_asteroid_points(size: int):
        n = size
        spawn_dist = math.sqrt(SCREEN_X*SCREEN_X + SCREEN_Y*SCREEN_Y) * 0.2 # spawn / despawn circle

        spawn_alpha = random.randint(0, 359)
        spawn_alpha_rad = spawn_alpha * math.pi / 180 # spawn angle rad
        spawn_circle_center = (SCREEN_X / 2, SCREEN_Y / 2)
        spawn_x = spawn_circle_center[0] + (spawn_dist * math.cos(spawn_alpha_rad))
        spawn_y = spawn_circle_center[1] + (spawn_dist * math.sin(spawn_alpha_rad))

        direction_alpha_increment = 180  # random.randint(140, 220)
        direction_alpha_rad = (spawn_alpha-direction_alpha_increment) * math.pi / 180
        direction_x = spawn_circle_center[0] + (spawn_dist * math.cos(direction_alpha_rad))
        direction_y = spawn_circle_center[1] + (spawn_dist * math.sin(direction_alpha_rad))

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
        self.respawn_freq_ms = 2000
        self.last_respawn_time = 0
        self.cleanup_count = 0
        self.limit = 1

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
        new_asteroid: Asteroid = AsteroidBuilder.generate_asteroid(self.screen)
        self.asteroids.append(new_asteroid)


    def render(self):
        for asteroid in self.asteroids:
            asteroid.render()

class ColisionDetector:
    @staticmethod
    def asteroid_projectile(ac: AsteroidController, ship: SpaceShip):
        for ai,asteroid in enumerate(ac.asteroids):
            polygon = Polygon(asteroid.points)
            for pi, projectile in enumerate(ship.projectiles):
                projectile_point = Point(projectile.position[0],projectile.position[1])
                if polygon.contains(projectile_point):
                    ship.projectiles.pop(pi)
                    # ac.hit(ai, asteroid)
                    asteroid.hit(projectile.position, projectile.direction)
    
    # @staticmethod
    # def is_inside_polygon(vertices, point):
    #     orientation_left = None
    #     for i,_ in enumerate(vertices):
    #         if i == 0:
    #             continue
    #         left: bool = ColisionDetector.isLeft(vertices[i-1], vertices[i], point)
    #         if orientation_left is None:
    #             orientation_left = left
    #             continue
    #         if orientation_left != left:
    #             return False
    #     return True
    
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
            asteroid_controller.step()

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