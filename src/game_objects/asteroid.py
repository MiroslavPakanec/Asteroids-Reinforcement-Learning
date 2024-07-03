import random
import math
from shapely.geometry import Polygon
import pygame
from colors import Colors
from window import Window

class Asteroid:
    def __init__(self, screen, config, position, points, direction, speed, level):
        self.init_config(config)
        self.screen = screen
        self.position = position
        self.original_position = position
        self.points = points
        self.direction = direction
        
        self.speed = speed
        self.level = level
        self.health = self.level * self.level

        self.inc_x = (direction[0] - position[0]) * self.speed
        self.inc_y = (direction[1] - position[1]) * self.speed

    def init_config(self, config):
        min_rot = config['asteroid']['min_rotation_radians']
        max_rot = config['asteroid']['max_rotation_radians']
        self.rotation = random.uniform(min_rot, max_rot) * math.pi / 180
        self.missile_push_factor = config['asteroid']['missile_push_factor']
        self.missile_rotation_factor = config['asteroid']['missile_rotation_factor']
        self.config = config

    def rotate_point(self, center, point, angle):
        new_x = math.cos(angle) * (point[0]-center[0]) - math.sin(angle) * (point[1]-center[1]) + center[0]
        new_y = math.sin(angle) * (point[0]-center[0]) + math.cos(angle) * (point[1]-center[1]) + center[1]
        return (new_x, new_y)

    def get_center_of_mass(self):
        P = Polygon(self.points)
        return P.centroid.coords[0]

    def step(self):
        new_center_point = (self.position[0] + self.inc_x, self.position[1] + self.inc_y)
        new_points = []
        for p in self.points:
            np = (p[0] + self.inc_x, p[1] + self.inc_y)
            np = self.rotate_point(center=self.position, point=np, angle=self.rotation)
            new_points.append(np)

        new_center_point, new_points_lst = Window.translate_over_edge(self.config, new_center_point, [new_points], buffer=50)
        self.position = new_center_point
        self.points = new_points_lst[0]


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
        
        R = dist_from_center_of_mass * hit_angle_factor * hit_orientation_fac * self.missile_rotation_factor / (self.level * self.level)
        self.rotation += R

        # push 
        level_push_fac = (self.level * self.level)
        push_x, push_y = d[0] * self.missile_push_factor / level_push_fac , d[1] * self.missile_push_factor / level_push_fac
        self.inc_x -= push_x 
        self.inc_y -= push_y


    def render(self):
        pygame.draw.polygon(self.screen, Colors.GREEN, self.points)
        for i,p in enumerate(self.points):
            for j, p in enumerate(self.points):
                pygame.draw.line(self.screen, Colors.RED, self.points[i], self.points[j])