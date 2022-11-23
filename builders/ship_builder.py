from game_objects.ship import SpaceShip

SCREEN_X = 1000
SCREEN_Y = 1000

class ShipBuilder:
    @staticmethod
    def build_space_ship(screen):
        w, h = 44, 56
        x = SCREEN_X / 2 - w / 2
        y = SCREEN_Y / 2 - h / 2
        return SpaceShip(
            screen, 
            'ship',
            (x, y)
        )