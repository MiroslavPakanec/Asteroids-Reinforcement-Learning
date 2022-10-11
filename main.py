from tkinter import Toplevel
from gym import Space
import pygame
from pygame import Surface
from typing import Tuple, List
import traceback
import math

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
        
    def set_shooting(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LCTRL]:
            pygame.draw.circle(self.screen, Colors.BLUE, self.position, 1)
            projectile = Projectile(self.screen, self.position, self.rotation)
            self.projectiles.append(projectile)

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

def main(screen):
    try:
        clock = pygame.time.Clock()
        ship = build_space_ship(screen)

        while True:
            handle_exit_events()
            screen.fill(Colors.BACKGROUND)
            
            ship.step()
            ship.render()

            pygame.display.flip()
            clock.tick(FPS)

    except Exception as e:
        print(traceback.format_exc())
        print(e)
        pygame.quit()
        
    

if __name__ == '__main__':
    screen = initialize()   
    main(screen)