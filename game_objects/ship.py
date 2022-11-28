import math
import random
import pygame
from colors import Colors
from game_objects.projectile import Projectile
from utils import map_value_to_interval, radians
from window import Window
from typing import List

SCREEN_X = 1000
SCREEN_Y = 1000
MIN_BOOST_ACCELERATION_TIME = 15


class SpaceShip:
    def __init__(self, screen, config):
        print(config)
        self.init_config(config)
        self.screen = screen
        self.direction = 0, 0
        self.rotation = 0
        self.total_rotation = self.rotation
        self.skeleton_points = self.get_ship_points()
        self.misile_points = self.get_missile_points()
        self.particles = []
        self.particle_vecs = []
        self.particle_renders = []
        self.particle_colors = []
        self.boost = False
        self.last_shooting_time = 0
        self.projectiles: List[Projectile] = []

    def init_config(self, config):
        self.w = config['ship']['x']
        self.h = config['ship']['y']
        self.rotation_factor = config['ship']['rotation_factor']
        self.speed_factor = config['ship']['speed_factor']
        self.speed_factor_boost = config['ship']['speed_factor_boost']
        self.position = config['ship']['spawn_x'], config['ship']['spawn_y']
        self.speed_particle_renders = config['ship']['speed_particle_renders']
        self.speed_particle_renders_boost = config['ship']['speed_particle_renders_boost']
        self.speed_particle_spread_degrees = config['ship']['speed_particle_spread_degrees']
        self.speed_particle_spread_degrees_boost = config['ship']['speed_particle_spread_degrees_boost']
        self.shooting_freq = config['ship']['shooting_frequiency']
        self.config = config

    def get_ship_points(self):
        t = self.position[0], self.position[1] - (self.h / 2 )
        l = self.position[0] - self.w / 2, self.position[1] + (self.h / 2 )
        bl = self.position[0] - self.w / 4, self.position[1] + 3 * self.h / 4
        b = self.position[0], self.position[1] + (self.h / 2)
        br = self.position[0] + self.w / 4, self.position[1] + 3 * self.h / 4
        r = self.position[0] + self.w / 2, self.position[1] + (self.h / 2 )
        return [t, l, bl, b, br, r]

    def get_missile_points(self):
        lb = self.position[0] - self.w / 4, self.position[1] 
        rb = self.position[0] + self.w / 4 + 2, self.position[1]
        lt = self.position[0] - self.w / 4, self.position[1] - self.h / 2
        rt = self.position[0] + self.w / 4, self.position[1] - self.h / 2
        return [lb, rb, lt, rt]

    def set_shooting(self):
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()
        if keys[pygame.K_LCTRL] and current_time > self.last_shooting_time + self.shooting_freq:
            self.last_shooting_time = current_time
            lb, rb, lt, rt = self.get_missile_points()
            a = radians(self.total_rotation)
            cx, cy = self.position
            
            lb_rot = self.rotate_point(lb[0], lb[1], cx, cy, math.sin(a), math.cos(a))
            rb_rot = self.rotate_point(rb[0], rb[1], cx, cy, math.sin(a), math.cos(a))
            rt_rot = self.rotate_point(lt[0], rt[1], cx, cy, math.sin(a), math.cos(a))
            direction = rt_rot[0]-lb_rot[0], rt_rot[1]-lb_rot[1] # could be any point (left / right)
            projectile_left = Projectile(self.screen, self.config, lb_rot, direction)
            projectile_right = Projectile(self.screen, self.config, rb_rot, direction)
            self.projectiles.append(projectile_left)
            self.projectiles.append(projectile_right)

    def set_rotation(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rotation -= 1 * self.rotation_factor
            self.total_rotation -= 1 * self.rotation_factor
        if keys[pygame.K_d]:
            self.rotation += 1 * self.rotation_factor
            self.total_rotation += 1 * self.rotation_factor

    def set_boost(self):
        keys = pygame.key.get_pressed()
        self.boost = True if keys[pygame.K_SPACE] else False

    def set_particles(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self. add_particles()
        self.clear_particles()

    def get_max_particle_renders(self):
        return self.speed_particle_renders_boost if self.boost else self.speed_particle_renders

    def get_particle_speard(self):
        return self.speed_particle_spread_degrees_boost if self.boost else self.speed_particle_spread_degrees

    def get_particle_color(self):
        return Colors.PINK if self.boost else Colors.GREEN

    def add_particles(self):
        color = self.get_particle_color()
        spread = self.get_particle_speard()
        for _ in range(50):
            c = self.position
            alpha = radians(self.rotation) + radians(random.randint(-spread, spread))
            p = self.rotate_point(self.skeleton_points[3][0], self.skeleton_points[3][1], self.position[0], self.position[1], math.sin(alpha), math.cos(alpha))
            dx = p[0]-c[0]
            dy = p[1]-c[1]-random.randint(0,3)
            particle_vec = dx * 0.2 + self.direction[0], dy * 0.2 + self.direction[1]
            self.particles.append((p[0] + dx / 2,  p[1] + dy / 2))
            self.particle_vecs.append(particle_vec)
            self.particle_renders.append(0)
            self.particle_colors.append(color)

    def clear_particles(self):
        renders = self.get_max_particle_renders()
        for i, p in enumerate(self.particles):
            p = p[0] + self.particle_vecs[i][0], p[1] + self.particle_vecs[i][1]
            self.particles[i] = p
            if self.particle_renders[i] >= renders:
                self.particles.pop(i)
                self.particle_vecs.pop(i)
                self.particle_renders.pop(i)
                self.particle_colors.pop(i)
            else: 
                self.particle_renders[i] = self.particle_renders[i] + 1

    def rotate_point(self, px, py, cx, cy, sin, cos):
        x = cos * (px-cx) - sin * (py-cy) + cx
        y = sin * (px-cx) + cos * (py-cy) + cy
        return x, y

    def move_point(self, px, py, dx, dy):
        return px + dx, py + dy

    def rotate_ship(self):
        alpha = radians(self.rotation)
        sin, cos = math.sin(alpha), math.cos(alpha)
        cx, cy = self.position
        for i,p in enumerate(self.skeleton_points):
            self.skeleton_points[i] = self.rotate_point(p[0], p[1], cx, cy, sin, cos)
        for i,p in enumerate(self.misile_points):
            self.misile_points[i] = self.rotate_point(p[0], p[1], cx, cy, sin, cos)
        self.rotation = 0

    def set_direction(self):
        keys = pygame.key.get_pressed()
        dx, dy = self.direction
        dx_inc, dy_inc = 0, 0
        
        rel_rot = self.total_rotation % 360
        x_from, x_to, y_from, y_to, r_from, r_to = -1, -1, -1, -1, -1, -1
        if rel_rot <= 90: # <0 - 90>  
            x_from, x_to = 0, 1
            y_from, y_to = -1, 0
            r_from, r_to = 0, 90
        elif rel_rot <= 180: # (90, 180>
            x_from, x_to = 1, 0
            y_from, y_to = 0, 1
            r_from, r_to = 91, 180
        elif rel_rot <= 270: # (180, 270>
            x_from, x_to = 0, -1
            y_from, y_to = 1, 0
            r_from, r_to = 181, 270
        else: # (270, 360)
            r_from, r_to = 271, 359
            x_from, x_to = -1, 0
            y_from, y_to = 0, -1

        if keys[pygame.K_w]:
            dx_inc = map_value_to_interval(rel_rot, r_from, r_to, x_from, x_to)
            dy_inc = map_value_to_interval(rel_rot, r_from, r_to, y_from, y_to)


        f = self.speed_factor_boost if self.boost else self.speed_factor
        self.direction = (dx + dx_inc * f, dy + dy_inc * f)

    def set_position(self):
        x, y = self.position
        x, y = x + self.direction[0], y + self.direction[1]
        cx, cy = x, y

        sps, mps = [], []
        for p in self.skeleton_points:
            x, y = self.move_point(p[0], p[1], self.direction[0], self.direction[1])
            sps.append((x, y))
        for p in self.misile_points:
            x, y = self.move_point(p[0], p[1], self.direction[0], self.direction[1])
            mps.append((x, y))

        new_c, new_point_lists = Window.translate_over_edge((cx, cy), [sps, mps], buffer=20)
        self.position = new_c
        self.skeleton_points = new_point_lists[0]
        self.misile_points = new_point_lists[1]


    def step(self):
        self.set_boost()
        self.set_rotation()
        self.set_direction()
        self.set_position()
        self.set_shooting()
        self.rotate_ship()
        self.set_particles()
        for i,projectile in enumerate(self.projectiles):
            if (Window.is_point_off_window(projectile.position, SCREEN_X, SCREEN_Y)):
                self.projectiles.pop(i)
            else:
                projectile.step()

    def render(self):
        pygame.draw.line(self.screen, Colors.YELLOW, self.skeleton_points[0], self.skeleton_points[-1], width=2)
        for i, _ in enumerate(self.skeleton_points):
            if i == 0:
                continue
            pygame.draw.line(self.screen, Colors.YELLOW, self.skeleton_points[i], self.skeleton_points[i-1], width=2)

        for i, p in enumerate(self.particles):
            pygame.draw.circle(self.screen, self.particle_colors[i], p, 1)

        for projectile in self.projectiles:
            projectile.render()
