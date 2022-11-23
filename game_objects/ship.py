from typing import List
import pygame
import math

from colors import Colors
from window import Window
from game_objects.projectile import Projectile
from utils import map_value_to_interval, radians


SCREEN_X = 1000
SCREEN_Y = 1000
MIN_BOOST_ACCELERATION_TIME = 15

class SpaceShip:
    def __init__(self, screen, name, spawn_position):
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
        self.speed = (0,0)
        self.speed_factor = 0.06
        self.boost_speec_factor = 0.36
        self.rotation_factor = 5
        self.projectiles: List[Projectile] = []
        self.shooting_freq = 125
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
        if keys[pygame.K_SPACE] and self.acceleration_time > MIN_BOOST_ACCELERATION_TIME:
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
            sx_inc = map_value_to_interval(rel_rot, r_from, r_to, x_from, x_to)
            sy_inc = map_value_to_interval(rel_rot, r_from, r_to, y_from, y_to)
        
        if self.boost:
            speed_factor = self.boost_speec_factor
        else:
            speed_factor = self.speed_factor
    
        self.speed = (sx + sx_inc * self.speed_factor, sy + sy_inc * speed_factor)
    
    def set_position(self):
        x, y = Window.translate_point(self.position, SCREEN_X, SCREEN_Y)
        x = x + self.speed[0]
        y = y + self.speed[1]
        self.position = (x, y)

    def set_acceleration_time(self):
        keys = pygame.key.get_pressed()
        new_acc = 0
        if keys[pygame.K_w]:
            new_acc = min(self.acceleration_time + 1, self.max_acceleration_time)
        else:
            new_acc = max(self.acceleration_time - 1, self.min_acceleration_time)
        self.acceleration_time = new_acc
        

    def get_projectile_points(self, tx, ty):
        # origin (o) center (c) target point (p) distance (d)
        ox = self.position[0] + self.w - tx
        oy = self.position[1] + self.h - ty
        cx = self.position[0] + self.w / 2
        cy = self.position[1] + self.h / 2
        d_oc_x, d_oc_y = cx-ox, cy-oy
        d_oc = math.sqrt(d_oc_x*d_oc_x + d_oc_y*d_oc_y) 
        d_cp = d_oc
        alpha_rad = radians(360) - radians(self.rotation)
        left_px = cx - (d_cp * math.cos(alpha_rad))
        left_py = cy - (d_cp * math.sin(alpha_rad))
        right_px = cx + (d_cp * math.cos(alpha_rad))
        right_py = cy + (d_cp * math.sin(alpha_rad))
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

        for i,projectile in enumerate(self.projectiles):
            if (Window.is_point_off_window(projectile.position, SCREEN_X, SCREEN_Y)):
                self.projectiles.pop(i)
            else:
                projectile.step()
        
    def render(self):
        file_path = f'./images/{self.image_path}.png'
        img = pygame.image.load(file_path)
        img = pygame.transform.scale(img, (self.w, self.h))

        img_rect_center = img.get_rect(topleft = (self.position[0],self.position[1])).center       
        img_rotated = pygame.transform.rotate(img, self.rotation)
        img_rotated_rect = img_rotated.get_rect(center=img_rect_center)
        self.screen.blit(img_rotated, img_rotated_rect)        
        
        for projectile in self.projectiles:
            projectile.render()