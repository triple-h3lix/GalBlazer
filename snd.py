import pygame as pg
from os import path

pg.mixer.pre_init(44100, -16, 2, 2048)
pg.mixer.init()

# Sounds Library
# snd_shoot = pg.mixer.Sound('pewpew.wav')
# snd_hit = pg.mixer.Sound('hit.wav')
# snd_explode = pg.mixer.Sound('explode.wav')
# snd_blow = pg.mixer.Sound('blow_up.wav')


def load_sound(FILENAME):

    sound = pg.mixer.Sound(path.join("sounds/", FILENAME))
    sound.play()

def play_song(FILENAME):

    pg.mixer.music.stop()
    pg.mixer.music.load(path.join("sounds/", "music/", str(FILENAME)))
    pg.mixer.music.play(-1)