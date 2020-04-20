import pygame
import numpy as np

def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

def collide(obj1, obj2):
    offset_x = int(obj2.get_x() - obj1.get_x())
    offset_y = int(obj2.get_y() - obj1.get_y())
    return obj1.get_mask().overlap(obj2.get_mask(), (offset_x, offset_y)) is not None

def out_of_bg(bg, obj):
    offset_x = int(-obj.get_x())
    offset_y = int(-obj.get_y())
    return pygame.mask.from_surface(bg).overlap(obj.get_mask(), (offset_x, offset_y)) is not None

def out_of_bounds(width, height, obj):
    if obj.get_x() + obj.get_img().get_width() > width or obj.get_x() < 0:
        return True
    if obj.get_y() + obj.get_img().get_height() \
            > height or obj.get_y() < 0:
        return True
    return False

def normalize(v, value=1):
    norm = np.linalg.norm(v)
    if norm == 0:
       return v
    v = v / norm * value
    return v