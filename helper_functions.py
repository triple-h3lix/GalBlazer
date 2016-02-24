from random import choice
from math import atan2
import gfx


def scanlines():
    return gfx.screen.blit(gfx.scanlines, (0, 0))


def randomize(scale):
    return choice([-scale, 0, scale])


def calc_angle(origin, target):

    x = origin.rect.x
    y = origin.rect.y

    x2 = target.rect.x
    y2 = target.rect.y

    angle = atan2(y2 - y, x2 - x)

    return angle