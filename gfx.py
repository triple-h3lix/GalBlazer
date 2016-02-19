from glob import *
from os import path

import pygame as pg

import constants

pg.display.init()
screen = pg.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT),
                             pg.DOUBLEBUF | pg.HWSURFACE | pg.HWACCEL | pg.HWPALETTE)


def load_image(file):
    image = pg.image.load(path.join("graphics", file)).convert_alpha()
    return image


# Image Library
img_background = pg.image.load(path.join("graphics", "background.bmp")).convert()
img_bullet = pg.image.load(path.join("graphics", "bullet.png")).convert_alpha()
img_bullet_2 = pg.image.load(path.join("graphics", "bullet_2.png")).convert_alpha()
img_bullet_3 = pg.image.load(path.join("graphics", "bullet_3.png")).convert_alpha()
img_missile = pg.image.load(path.join("graphics", "missile.png")).convert_alpha()
img_explosion = pg.image.load(path.join("graphics", "explosion.png")).convert_alpha()
img_explosion_final = pg.image.load(path.join("graphics", "explosion_last.png")).convert_alpha()
img_player = pg.image.load(path.join("graphics", "ship.png")).convert_alpha()
img_player_flash = pg.image.load(path.join("graphics", "ship.png")).convert_alpha()
img_fighter = pg.image.load(path.join("graphics", "fighter.png")).convert_alpha()
img_fighter_hit = pg.image.load(path.join("graphics", "fighter_hit.png")).convert_alpha()
img_frigate = pg.image.load(path.join("graphics", "frigate.png")).convert_alpha()
img_frigate_hit = pg.image.load(path.join("graphics", "frigate_hit.png")).convert_alpha()
img_cruiser = pg.image.load(path.join("graphics", "cruiser.png")).convert_alpha()
img_cruiser_firing = pg.image.load(path.join("graphics", "cruiser_firing.png")).convert_alpha()
img_cruiser_hit = pg.image.load(path.join("graphics", "cruiser_hit.png")).convert_alpha()
img_beam = pg.image.load(path.join("graphics", "beam.png")).convert()
img_beam_arc = pg.image.load(path.join("graphics", "beam_arc.png")).convert()
img_life = pg.image.load(path.join("graphics", "life.png")).convert_alpha()
img_hit = pg.image.load(path.join("graphics", "hit.png")).convert_alpha()
img_title_stars = pg.image.load(path.join("graphics", "title_stars.png")).convert()
img_title_background = pg.image.load(path.join("graphics", "title_background.png")).convert()
img_title_background = pg.transform.scale(img_title_background, (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
img_title_a = pg.image.load(path.join("graphics", "title_a.png")).convert_alpha()
img_title_b = pg.image.load(path.join("graphics", "title_b.png")).convert_alpha()
img_title_whole = pg.image.load(path.join("graphics", "title_whole.png")).convert_alpha()
img_enemy_shot_a = pg.image.load(path.join("graphics", "enemy_shot_a.png")).convert_alpha()
img_enemy_shot_b = pg.image.load(path.join("graphics", "enemy_shot_b.png")).convert_alpha()

scanlines = pg.image.load(path.join("scanlines.png")).convert_alpha()
scanlines = pg.transform.scale(scanlines, (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))


def explosion(x, y):

    for file in glob("graphics/explosion_1/*.png"):
        image = pg.image.load(file).convert()
        image = pg.transform.scale(image, (200, 200))
        for time in range(200):
            pg.display.update(screen.blit(image, (x-80, y-80)))
