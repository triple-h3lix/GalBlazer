from glob import *
from os import path

from pygame import *

import constants

screen = display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))


def set_gamma(value):
    return display.set_gamma(value)


def load_image(file):
    img = image.load(path.join("graphics", file)).convert_alpha()
    return img


# Image Library
img_background = image.load(path.join("graphics", "background.bmp")).convert()
img_bullet = image.load(path.join("graphics", "bullet.png")).convert_alpha()
img_bullet_2 = image.load(path.join("graphics", "bullet_2.png")).convert_alpha()
img_bullet_3 = image.load(path.join("graphics", "bullet_3.png")).convert_alpha()
img_missile = image.load(path.join("graphics", "missile.png")).convert_alpha()
img_explosion = image.load(path.join("graphics", "explosion.png")).convert_alpha()
img_explosion_final = image.load(path.join("graphics", "explosion_last.png")).convert_alpha()
img_player = image.load(path.join("graphics", "ship.png")).convert_alpha()
img_player_forward = image.load(path.join("graphics", "ship_moveforward.png")).convert_alpha()
img_player_back = image.load(path.join("graphics", "ship_moveback.png")).convert_alpha()
img_player_left = image.load(path.join("graphics", "ship_moveleft.png")).convert_alpha()
img_player_right = image.load(path.join("graphics", "ship_moveright.png")).convert_alpha()
img_player_invulnerable = image.load(path.join("graphics", "ship_invulnerable.png")).convert_alpha()
img_fighter = image.load(path.join("graphics", "fighter.png")).convert_alpha()
img_fighter_hit = image.load(path.join("graphics", "fighter_hit.png")).convert_alpha()
img_frigate = image.load(path.join("graphics", "frigate.png")).convert_alpha()
img_frigate_hit = image.load(path.join("graphics", "frigate_hit.png")).convert_alpha()
img_cruiser = image.load(path.join("graphics", "cruiser.png")).convert_alpha()
img_cruiser_firing = image.load(path.join("graphics", "cruiser_firing.png")).convert_alpha()
img_cruiser_hit = image.load(path.join("graphics", "cruiser_hit.png")).convert_alpha()
img_beam = image.load(path.join("graphics", "beam.png")).convert()
img_beam_arc = image.load(path.join("graphics", "beam_arc.png")).convert()
img_life = image.load(path.join("graphics", "life.png")).convert_alpha()
img_hit = image.load(path.join("graphics", "hit.png")).convert_alpha()
img_title_stars = image.load(path.join("graphics", "title_stars.png")).convert()
img_title_background = image.load(path.join("graphics", "title_background.png")).convert()
img_title_background = transform.scale(img_title_background, (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
img_title_a = image.load(path.join("graphics", "title_a.png")).convert_alpha()
img_title_b = image.load(path.join("graphics", "title_b.png")).convert_alpha()
img_title_whole = image.load(path.join("graphics", "title_whole.png")).convert_alpha()
img_enemy_shot_a = image.load(path.join("graphics", "enemy_shot_a.png")).convert_alpha()
img_enemy_shot_b = image.load(path.join("graphics", "enemy_shot_b.png")).convert_alpha()

scanlines = image.load(path.join("scanlines.png")).convert_alpha()
scanlines = transform.scale(scanlines, (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))

title_ship_a = image.load(path.join("graphics", "TITLE_SHIP", "zx_delta_1.png")).convert_alpha()
title_ship_b = image.load(path.join("graphics", "TITLE_SHIP", "zx_delta_2.png")).convert_alpha()


def explosion(x, y):
    for file in glob("graphics/explosion_1/*.png"):
        img = image.load(file).convert_alpha()
        img = transform.scale(img, (200, 200))
        for _ in range(10):
            screen.blit(img, (x - 80, y - 80))
            display.update()
