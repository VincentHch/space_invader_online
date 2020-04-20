import numpy as np
import pygame
import os
import random

from misc import rot_center, normalize, out_of_bounds
from object import Object
from laser import Laser

SPACE1_IMG = pygame.transform.scale(pygame.image.load(os.path.join("asset", "player_ship.png")), (100, 100))
SPACE1_IMG_FIRE = pygame.transform.scale(pygame.image.load(os.path.join("asset", "player_fire.png")), (100, 100))

aliens = {0: pygame.transform.scale(pygame.image.load(os.path.join("asset", "alien1.png")), (100, 100)),
          1: pygame.transform.scale(pygame.image.load(os.path.join("asset", "alien2.png")), (100, 100)),
          2: pygame.transform.scale(pygame.image.load(os.path.join("asset", "alien3.png")), (100, 100))
          }

pygame.mixer.init()

LASER_BEAM = pygame.mixer.Sound(os.path.join("asset", "laser.wav"))
NO_AMMO = pygame.mixer.Sound(os.path.join("asset", "no_ammo.wav"))



class Ship(Object):

    fire_speed = 10

    def __init__(self, x, y, speed_x, speed_y, angle=0, speed_angle=0, health=100):
        super().__init__(x, y)
        self.speed = np.array([float(speed_x), float(speed_y)])
        self.angle = angle
        self.speed_angle = speed_angle
        self.max_health = health
        self.health = health
        self.laser = []
        self.cooldown_counter = 30
        self.cooldown = 30
        self.nb_ammo = 5

    def set_v_x(self, x):
        self.speed[0] = float(x)

    def set_v_y(self, y):
        self.speed[1] = float(y)

    def get_v_x(self):
        return self.speed[0]

    def get_v_y(self):
        return self.speed[1]

    def get_img(self):
        return self.image

    def draw(self, window):
        if self.get_img() is None:
            return None

        window.blit(rot_center(self.get_img(), self.angle), self.pos)

    def get_mask(self):
        return pygame.mask.from_surface(rot_center(self.get_img(), self.angle))

    def apply_speed(self):
        self.pos += self.speed
        self.angle += self.speed_angle

    def apply_steer(self, steer):
        self.speed += steer

    def next_state(self, steers=[]):
        self.cooldown_counter = max(0, self.cooldown_counter-1)
        [self.apply_steer(steer) for steer in steers]
        self.apply_speed()

    def shoot(self):
        if self.cooldown_counter == 0 and self.nb_ammo > 0:
            LASER_BEAM.play()
            self.cooldown_counter = self.cooldown
            self.nb_ammo -= 1
            angle = np.radians(self.angle + 90)
            speed_x = self.get_v_x() + np.cos(angle) * Ship.fire_speed
            speed_y = self.get_v_y() - np.sin(angle) * Ship.fire_speed
            new_laser = Laser(self.get_x() + 35, self.get_y() + 35, speed_x, speed_y, self.angle)

            self.laser.append(new_laser)

            return True
        else:
            NO_AMMO.play()
            return False


class Player(Ship):

    def __init__(self, x, y, speed_x, speed_y, angle=0, speed_angle=0, health=100, oil_level=200):
        super().__init__(x, y, speed_x, speed_y, angle, speed_angle, health)
        self.engine_on = False
        self.max_oil_level = oil_level
        self.oil_level = oil_level
        self.live = 3
        self.point = 0

    def get_img(self):
        if self.engine_on:
            return SPACE1_IMG_FIRE
        else:
            return SPACE1_IMG

    def turn_on(self):
        self.engine_on = True
        self.oil_level -= 1
        self.oil_level = max(0, self.oil_level)

    def turn_off(self):
        self.engine_on = False

    def get_oil_percentage(self):
        return self.oil_level / self.max_oil_level

    def fill_oil(self):
        self.oil_level = self.max_oil_level

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.get_x(), self.get_y() + self.get_img().get_height() + 10,
                                             self.get_img().get_width(), 5))
        pygame.draw.rect(window, (0,255,0), (self.get_x(), self.get_y() + self.get_img().get_height() + 10,
                                             self.get_img().get_width() * (1 - ((self.max_health - self.health)/self.max_health)), 5))

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

class Enemy(Ship):

    def __init__(self, x, y, type, speed_x=0, speed_y=0, angle=0, speed_angle=0, health=100):
        super().__init__(x, y, speed_x, speed_y, angle, speed_angle, health)
        self.appeared = False
        self.level = 1
        self.type = type

    def get_img(self):
        return aliens[self.type]

    def went_out(self, width, height):
        if not out_of_bounds(width, height, self):
            self.appeared = True
        if out_of_bounds(width, height, self) and self.appeared:
            self.level += 1
            return True
        return False

    def randomize(self, width, height, player, max_speed=3, min_speed=2, auto_speed = True):
        max_speed += self.level
        min_speed += self.level
        self.appeared = False
        x = random.randint(-2*width, 3*width)
        y = random.randint(-2*height, 3*height)
        while -width < x < 2*width and -height < y < 2*height:
            x = random.randint(-width, 2 * width)
            y = random.randint(-height, 2 * height)
        self.set_x(x)
        self.set_y(y)
        self.angle = random.randint(0, 360)
        self.image = aliens[random.randint(0, 2)]
        self.set_v_x(player.get_x()-self.get_x()+random.random()*200-100)
        self.set_v_y(player.get_y()-self.get_y()+random.random()*200-100)
        self.speed = normalize(self.speed, random.random()*(max_speed-min_speed)+min_speed)
        self.speed_angle = random.random() * 2 - 1
        return self
