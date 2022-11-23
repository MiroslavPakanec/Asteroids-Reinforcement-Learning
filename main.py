import pygame
import traceback

from colors import Colors
from game_objects.ship import SpaceShip
from builders.ship_builder import ShipBuilder
from controllers.asteroid_controller import AsteroidController
from controllers.colision_controller import ColisionController

SCREEN_X = 1000
SCREEN_Y = 1000
FPS = 60


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
  

def main(screen):
    clock = pygame.time.Clock()
    try:
        ship: SpaceShip = ShipBuilder.build_space_ship(screen)
        asteroid_controller = AsteroidController(screen)

        while True:
            handle_exit_events()
            screen.fill(Colors.BACKGROUND)

            ship.step()
            asteroid_controller.step()

            ColisionController.check_asteroid_projectile(asteroid_controller, ship)

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