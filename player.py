import pygame as pg
import main, constants, graphics, audio
from random import randrange


class Player(pg.sprite.Sprite):
    bullets_max = 20
    bullets = []
    allBullets = pg.sprite.Group()

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = graphics.load_image("ship.png")
        self.dx = 0
        self.dy = 0
        self.speed = 10
        self.rect = self.image.get_rect()
        self.size = (self.rect[2], self.rect[3])
        self.rect.centerx = constants.SCREEN_WIDTH / 2
        self.rect.bottom = constants.SCREEN_HEIGHT - self.size[1]
        self.moving = False
        self.last_x = 0
        self.last_y = 0
        self.dead = False
        self.dead_timer = pg.time.get_ticks()
        self.cool_down = 0
        self.power_level = 1

    def update(self):
        if self.dead:
            self.rect.y = constants.SCREEN_HEIGHT + 100
            if pg.time.get_ticks() - self.dead_timer > 3000:
                self.dead = False
                self.image = graphics.load_image("ship.png")
                self.rect.centerx = constants.SCREEN_WIDTH / 2
                self.rect.bottom = constants.SCREEN_HEIGHT - self.size[1]

        if self.rect.right > constants.SCREEN_WIDTH:
            self.rect.x = constants.SCREEN_WIDTH - self.size[0]
            self.dx = 0
        if self.rect.left < 0:
            self.rect.x = 0
            self.dx = 0
        if self.rect.bottom > constants.SCREEN_HEIGHT and not self.dead:
            self.rect.bottom = constants.SCREEN_HEIGHT
            self.dy = 0

        if self.moving:
            self.rect.x += self.dx
            self.rect.y += self.dy
        else:
            self.dx = 0
            self.dy = 0

        self.moving = False
        self.allBullets.update()

    def move_left(self):
        self.dx = -self.speed
        self.moving = True

    def move_right(self):
        self.dx = self.speed
        self.moving = True

    def move_up(self):
        self.dy = -self.speed
        self.moving = True

    def move_down(self):
        self.dy = self.speed
        self.moving = True

    def shoot(self):
        if pg.time.get_ticks() > self.cool_down + 100:
            if self.power_level == 1 and len(self.allBullets) < self.bullets_max:
                self.cool_down = pg.time.get_ticks()
                audio.load_sound("pewpew.wav")
                new_bullet1 = main.Bullet(self.rect.centerx - 5, self.rect.bottom - self.size[1], graphics.load_image("bullet.png"))
                new_bullet2 = main.Bullet(self.rect.centerx + 5, self.rect.bottom - self.size[1], graphics.load_image("bullet.png"))
                new_bullet1.dy = -10
                new_bullet2.dy = -10
                self.allBullets.add(new_bullet1, new_bullet2)
            if self.power_level == 2 and len(self.allBullets) < self.bullets_max:
                self.cool_down = pg.time.get_ticks()
                audio.load_sound("pewpew.wav")
                new_bullet1 = main.Bullet(self.rect.centerx - 5, self.rect.bottom - self.size[1], graphics.load_image("bullet.png"))
                new_bullet2 = main.Bullet(self.rect.centerx + 5, self.rect.bottom - self.size[1], graphics.load_image("bullet.png"))
                missile = main.Bullet(self.rect.centerx, self.rect.y, graphics.load_image("missile.png"))
                new_bullet1.dy = -10
                new_bullet2.dy = -10
                missile.dy = -20
                self.allBullets.add(new_bullet1, new_bullet2, missile)
            if self.power_level == 3:
                self.power_level = 2