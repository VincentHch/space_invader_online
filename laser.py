import numpy as np
import pygame
import os
import random

from object import Object
from misc import rot_center

LASER = pygame.transform.scale(pygame.image.load(os.path.join("asset", "laser.png")), (29, 29))


class Laser(Object):

    def __init__(self, x, y, speed_x, speed_y, angle):
        super().__init__(x, y)
        self.speed = np.array([float(speed_x), float(speed_y)])
        self.angle = angle
        self.image = LASER
        self.mask = pygame.mask.from_surface(rot_center(self.image, self.angle))

    def draw(self, window):
        if self.get_img() is None:
            return None

        window.blit(rot_center(self.image, self.angle), self.pos)

    def next_state(self):
        self.pos += self.speed
