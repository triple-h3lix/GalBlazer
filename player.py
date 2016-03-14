from random import choice
from time import clock

import pygame as pg

import gfx
import main
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from snd import load_sound


class Player(pg.sprite.Sprite):
    allBullets = pg.sprite.Group()
    start_position = SCREEN_HEIGHT + 200

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = gfx.img_player
        self.arrive = True
        self.dx = 0
        self.dy = 0
        self.speed = 8
        self.dv = 0
        self.rect = self.image.get_rect()
        self.size = (self.rect[2], self.rect[3])
        self.rect.centerx = SCREEN_WIDTH / 2
        self.rect.bottom = self.start_position
        self.moving = False
        self.shooting = False
        self.last_x = 0
        self.last_y = 0
        self.dead = False
        self.respawn = False
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.dead_timer = pg.time.get_ticks()
        self.cool_down = 0
        self.power_level = 1
        self.t = 0
        self.anim_timer = 0

    def update(self):

        if self.arrive:
            self.appear()
            load_sound("leave_hyperspace.wav")
        elif self.respawn:
            self.invulnerable = True
            self.appear()

        if self.invulnerable:
            imgs = [gfx.img_player, gfx.img_player_invulnerable]
            self.image = choice(imgs)
            self.invulnerable_timer += 1
            if self.invulnerable_timer >= 180:
                self.image = gfx.img_player
                self.invulnerable_timer = 0
                self.invulnerable = False

        if self.rect.right > SCREEN_WIDTH:
            self.rect.x = SCREEN_WIDTH - self.size[0]
            self.dx = 0
        elif self.rect.left < 0:
            self.rect.x = 0
            self.dx = 0
        elif self.rect.bottom > SCREEN_HEIGHT and not self.dead:
            self.rect.bottom = SCREEN_HEIGHT
            self.dy = 0

        if self.moving:
            if not all([self.dead or self.respawn or self.arrive]):
                # for i in range(self.speed):
                #     self.rect.x += self.dx
                #     self.rect.y += self.dy
                self.rect.x += round(self.dx * self.dv)
                self.rect.y += round(self.dy * self.dv)
                if self.dv < self.speed:
                    self.dv += 1.005
        else:
            if not self.invulnerable:
                self.image = gfx.img_player
            self.rect.x += self.dx * self.dv
            self.rect.y += self.dy * self.dv

            if self.dv > 0:
                self.dv -= .5
            else:
                self.dv = 0
        if self.dead:
            self.rect.y = self.start_position
            self.dead_timer += 1
            if self.dead_timer >= 180:
                self.rect.centerx = SCREEN_WIDTH / 2
                self.dead = False
                self.respawn = True
        else:
            self.dead_timer = 0

        if not self.shooting:
            self.t = 0

        self.moving = False
        self.allBullets.update()

    def move_left(self):
        self.dx, self.dy = -1, 0
        if not self.invulnerable:
            self.image = gfx.img_player_left
        self.moving = True

    def move_right(self):
        self.dx, self.dy = 1, 0
        if not self.invulnerable:
            self.image = gfx.img_player_right
        self.moving = True

    def move_up(self):
        self.dx, self.dy = 0, -1
        if not self.invulnerable:
            self.image = gfx.img_player_forward
        self.moving = True

    def move_down(self):
        self.dx, self.dy = 0, 1
        if not self.invulnerable:
            self.image = gfx.img_player_back
        self.moving = True

    def move_upleft(self):
        self.dx, self.dy = -1, -1
        if not self.invulnerable:
            self.image = gfx.img_player_forward
        self.moving = True

    def move_upright(self):
        self.dx, self.dy = 1, -1
        if not self.invulnerable:
            self.image = gfx.img_player_forward
        self.moving = True

    def move_downleft(self):
        self.dx, self.dy = -1, 1
        if not self.invulnerable:
            self.image = gfx.img_player_back
        self.moving = True

    def move_downright(self):
        self.dx, self.dy = 1, 1
        if not self.invulnerable:
            self.image = gfx.img_player_back
        self.moving = True

    def appear(self):
        self.dy = -3
        self.dx = 0
        self.rect.bottom += self.dy
        self.draw_trail(SCREEN_HEIGHT, 3)

        if self.rect.bottom < 900:
            self.rect.bottom = 900
            self.dy = 0
            duration = 2.0
            current_time = clock()
            if current_time > duration:
                self.arrive = False
                self.respawn = False

    def draw_trail(self, length, offset):
        last_x = self.rect.centerx
        last_y = self.rect.bottom
        pg.draw.line(gfx.screen, (65, 255, 255), (last_x - offset, last_y - 5), (last_x - offset, last_y + length), 5)
        pg.draw.line(gfx.screen, (65, 255, 255), (last_x + offset, last_y - 5), (last_x + offset, last_y + length), 5)
        pg.draw.aaline(gfx.screen, (255, 255, 255), (last_x - offset, last_y - 5),
                       (last_x - offset, last_y + length + 5), True)
        pg.draw.aaline(gfx.screen, (255, 255, 255), (last_x + offset, last_y - 5),
                       (last_x + offset, last_y + length + 5), True)
        pg.display.update()

    def shoot(self):
        if not self.dead and not self.arrive:
            self.shooting = True
            if self.power_level == 1 and (pg.time.get_ticks() > self.cool_down + 100):
                self.cool_down = pg.time.get_ticks()
                load_sound("pewpew.wav")
                new_bullet1 = main.Bullet(self.rect.centerx - 5, self.rect.bottom - self.size[1],
                                          gfx.img_bullet)
                new_bullet2 = main.Bullet(self.rect.centerx + 5, self.rect.bottom - self.size[1],
                                          gfx.img_bullet)
                new_bullet1.dy = -15
                new_bullet2.dy = -15
                self.allBullets.add(new_bullet1, new_bullet2)
            elif self.power_level == 2 and (pg.time.get_ticks() > self.cool_down + 20):
                self.t += 1
                self.cool_down = pg.time.get_ticks()
                new_bullet1 = main.Bullet(self.rect.centerx - 10, self.rect.bottom - self.size[1],
                                          gfx.img_bullet_2)
                new_bullet2 = main.Bullet(self.rect.centerx + 10, self.rect.bottom - self.size[1],
                                          gfx.img_bullet_2)
                new_bullet3 = main.Bullet(self.rect.centerx - 25, self.rect.bottom - self.size[1],
                                          gfx.img_bullet_2)
                new_bullet4 = main.Bullet(self.rect.centerx + 25, self.rect.bottom - self.size[1],
                                          gfx.img_bullet_2)

                new_bullet1.dy = -10
                new_bullet2.dy = -10
                new_bullet3.dy = -10
                new_bullet4.dy = -10

                if self.t == 2:
                    self.allBullets.add(new_bullet1)
                    self.allBullets.add(new_bullet2)
                    load_sound("pewpew2.wav")
                if self.t == 4:
                    self.allBullets.add(new_bullet3)
                    self.allBullets.add(new_bullet4)
                    load_sound("pewpew2.wav")
                if self.t > 5:
                    self.t = 0
            elif self.power_level >= 3 and (pg.time.get_ticks() > self.cool_down + 50):
                self.t += 1
                self.cool_down = pg.time.get_ticks()

                new_bullet = main.Bullet(self.rect.centerx - 60, self.rect.y, gfx.img_bullet_3)
                new_bullet.dy = -20
                new_bullet.image = pg.transform.scale(new_bullet.image, (150, 100))

                if self.t >= 4:
                    self.allBullets.add(new_bullet)
                    load_sound("pewpew3.wav")
                    self.t = 0

    def die(self):
        self.last_x = self.rect.x
        self.last_y = self.rect.y
        load_sound("explode.wav")
        gfx.explosion(self.last_x, self.last_y)
        self.power_level = 1
        self.dead = True
