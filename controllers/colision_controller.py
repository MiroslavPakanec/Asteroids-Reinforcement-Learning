from shapely.geometry import Polygon, Point
from game_objects.ship import SpaceShip
from controllers.asteroid_controller import AsteroidController

class ColisionController:

    @staticmethod
    def check_asteroid_ship(ac: AsteroidController, ship: SpaceShip):
        for ai,asteroid in enumerate(ac.asteroids):
            polygon_asteroid = Polygon(asteroid.points)
            polygon_ship = Polygon(ship.skeleton_points)
            if (polygon_asteroid.intersects(polygon_ship)):
                raise Exception('GAME OVER')

            
    @staticmethod
    def check_asteroid_projectile(ac: AsteroidController, ship: SpaceShip):
        for ai,asteroid in enumerate(ac.asteroids):
            polygon = Polygon(asteroid.points)
            for pi, projectile in enumerate(ship.projectiles):
                projectile_point = Point(projectile.position[0],projectile.position[1])
                if polygon.contains(projectile_point):
                    ship.projectiles.pop(pi)
                    
                    destroyed = asteroid.hit()
                    if not destroyed:
                        asteroid.move_on_hit(projectile.position, projectile.direction)
                    else:
                        position, dir_A, dir_B, speed, level = asteroid.split()
                        ac.asteroids.pop(ai)
                        if (level <= 0):
                            continue
                        ac.generate_asteroid(level, position, dir_A, speed)
                        ac.generate_asteroid(level, position, dir_B, speed)