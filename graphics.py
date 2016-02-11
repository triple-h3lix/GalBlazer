import pygame as pg
import os

# Image Library
# img_background = pg.image.load('background.bmp').convert()
# img_bullet = pg.image.load('bullet.png').convert_alpha()
# img_missile = pg.image.load('missile.png').convert_alpha()
# img_explosion = pg.image.load('explosion.png').convert_alpha()
# img_explosion_final = pg.image.load('explosion_last.png').convert_alpha()
# img_explosion_final = pg.transform.scale2x(img_explosion_final)
# img_player = pg.image.load('ship.png').convert_alpha()
# img_enemy = pg.image.load('fighter.png').convert_alpha()
# img_enemyhit = pg.image.load('fighter_hit.png').convert_alpha()
# img_cruiser = pg.image.load('cruiser.png').convert_alpha()
# img_cruiserhit = pg.image.load('cruiser_hit.png').convert_alpha()
# img_life = pg.image.load('life.png').convert_alpha()
# img_hit = pg.image.load('hit.png').convert_alpha()

def load_image(FILENAME):
    image = pg.image.load(os.path.join("graphics", FILENAME)).convert_alpha()
    return image