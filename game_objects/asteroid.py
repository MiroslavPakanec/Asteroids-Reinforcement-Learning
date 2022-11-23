import random
import math
from shapely.geometry import Polygon
import pygame
from colors import Colors

SCREEN_X = 1000
SCREEN_Y = 1000

class Asteroid:
    def __init__(self, screen, position, points, direction, speed, level):
        self.screen = screen
        self.position = position
        self.original_position = position
        self.points = points # points of convex hull
        self.direction = direction
        self.rotation = random.uniform(0.1, 1) * math.pi / 180
        self.speed = speed # 0.01 # random.randint(1, 100) * 0.0001 
        self.level = level
        self.health = self.level * self.level

        self.t, self.b, self.l, self.r = False, False, False, False # is translation over edge
        self.transform_t = lambda p : (p[0], p[1] - SCREEN_Y + 100)
        self.transformed_points = []

        self.inc_x = (direction[0] - position[0]) * self.speed
        self.inc_y = (direction[1] - position[1]) * self.speed

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
        buffer = 50
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


    def hit(self):
        self.health -= 1
        if self.health <= 0:
            return True
        return False

    def split(self):
        new_direction_x = self.inc_x / self.speed + self.position[0]
        new_direction_y = self.inc_y / self.speed + self.position[1] 

        alpha = 20 * math.pi / 180
        beta = -20 * math.pi / 180
        directionA_x = new_direction_x * math.cos(alpha) - new_direction_y * math.sin(alpha)
        directionA_y = new_direction_x * math.sin(alpha) + new_direction_y * math.cos(alpha)
        
        directionB_x = new_direction_x * math.cos(beta) - new_direction_y * math.sin(beta)
        directionB_y = new_direction_x * math.sin(beta) + new_direction_y * math.cos(beta)

        return self.position, (directionA_x, directionA_y), (directionB_x, directionB_y), self.speed, self.level - 1

        

    def move_on_hit(self, hit_point, hit_direction):
        # compute Center C, hit point H and projectile origin O
        Hx, Hy = hit_point
        Dx, Dy = hit_direction
        dist_x, dist_y = (Hx-Dx) * 0.1, (Hy-Dy) * 0.1
        Ox, Oy = Hx+dist_x, Hy+dist_y
        Cx, Cy = self.get_center_of_mass()
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
        
        R = dist_from_center_of_mass * hit_angle_factor * hit_orientation_fac * 0.001 / (self.level * 10)
        self.rotation += R

        # push 
        level_push_fac = (self.level * self.level)
        push_x, push_y = d[0] * 0.1 / level_push_fac , d[1] * 0.1 / level_push_fac
        self.inc_x -= push_x 
        self.inc_y -= push_y


    def render(self):
        pygame.draw.polygon(self.screen, Colors.GREEN, self.points)
        for i,p in enumerate(self.points):
            for j, p in enumerate(self.points):
                pygame.draw.line(self.screen, Colors.RED, self.points[i], self.points[j])