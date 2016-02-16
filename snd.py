import pygame as pg
import os

pg.mixer.pre_init(44100, -16, 2, 2048)
pg.mixer.init()

# Sounds Library
# snd_shoot = pg.mixer.Sound('pewpew.wav')
# snd_hit = pg.mixer.Sound('hit.wav')
# snd_explode = pg.mixer.Sound('explode.wav')
# snd_blow = pg.mixer.Sound('blow_up.wav')


def load_sound(FILENAME):
    sound = pg.mixer.Sound(os.path.join("sounds/", FILENAME))
    sound.play()