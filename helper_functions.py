import pygame as pg

from math import atan2
from random import choice

def refresh():
    return pg.display.update()
	
def randomize(scale):
    return choice([-scale, 0, scale])


def calc_angle(origin, target):
    import math

    x = origin.rect.x
    y = origin.rect.y

    x2 = target.rect.x
    y2 = target.rect.y

    angle = math.atan2(y2 - y, x2 - x)

    return angle