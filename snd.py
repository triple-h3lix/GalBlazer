import pygame as pg
from os import path

# Sounds Library
# shoot = pg.mixer.Sound('pewpew.wav')
# hit = pg.mixer.Sound(path.join("sounds", "hit.wav"))
# little_explode = pg.mixer.Sound('explode.wav')
# big_explode = pg.mixer.Sound('blow_up.wav')


def load_sound(FILENAME):

    sound = pg.mixer.Sound(path.join("sounds/", FILENAME))
    sound.play()

def play_song(FILENAME):

    pg.mixer.music.stop()
    pg.mixer.music.load(path.join("sounds/", "music/", str(FILENAME)))
    pg.mixer.music.play(-1)