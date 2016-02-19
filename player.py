import pygame as pg

import constants
import gfx
import main
import snd
import helper_functions


class Player(pg.sprite.Sprite):
    allBullets = pg.sprite.Group()
    start_position = constants.SCREEN_HEIGHT * 2

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = gfx.img_player
        self.arrive = True
        self.dx = 0
        self.dy = 0
        self.speed = 8
        self.rect = self.image.get_rect()
        self.size = (self.rect[2], self.rect[3])
        self.rect.centerx = constants.SCREEN_WIDTH / 2
        self.rect.bottom = self.start_position
        self.moving = False
        self.shooting = False
        self.last_x = 0
        self.last_y = 0
        self.dead = False
        self.invulnerable = False
        self.dead_timer = pg.time.get_ticks()
        self.cool_down = 0
        self.power_level = 1
        self.t = 0
        self.anim_timer = 0

    def update(self):

        if self.arrive:
            self.dy = -5
            self.dx = 0
            self.rect.y += self.dy
            self.draw_trail(constants.SCREEN_HEIGHT, 3)
            if self.rect.bottom < constants.SCREEN_HEIGHT - 200:
                self.invulnerable = True
                self.arrive = False
                if self.invulnerable:
                    self.image = gfx.img_player_flash
                    helper_functions.refresh()
                    self.anim_timer += 1
                    if self.anim_timer > 20:
                        self.image = gfx.img_player
                        helper_functions.refresh()
                        self.anim_timer = 0
                        self.t += 1
                        if self.t > 100:
                            self.invulnerable = False

        elif self.rect.right > constants.SCREEN_WIDTH:
            self.rect.x = constants.SCREEN_WIDTH - self.size[0]
            self.dx = 0
        elif self.rect.left < 0:
            self.rect.x = 0
            self.dx = 0
        elif self.rect.bottom > constants.SCREEN_HEIGHT and not self.dead:
            self.rect.bottom = constants.SCREEN_HEIGHT
            self.dy = 0

        if self.moving and not self.arrive:
            self.rect.x += self.dx
            self.rect.y += self.dy
        else:
            self.dx = 0
            self.dy = 0

        if not self.shooting and not self.invulnerable:
            self.t = 0

        if self.dead:
            self.rect.y = self.start_position
            self.dead_timer += 1
            if self.dead_timer >= 100:
                self.image = gfx.img_player
                self.rect.centerx = constants.SCREEN_WIDTH / 2
                self.dead_timer = 0
                self.dead = False
                self.arrive = True

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

    def draw_trail(self, length, offset):
        last_x = self.rect.centerx
        last_y = self.rect.bottom
        pg.draw.line(gfx.screen, (65, 255, 255), (last_x - offset, last_y - 5), (last_x - offset, last_y + length), 5)
        pg.draw.line(gfx.screen, (65, 255, 255), (last_x + offset, last_y - 5), (last_x + offset, last_y + length), 5)
        pg.draw.aaline(gfx.screen, (255, 255, 255), (last_x - offset, last_y - 5),
                       (last_x - offset, last_y + length + 5), True)
        pg.draw.aaline(gfx.screen, (255, 255, 255), (last_x + offset, last_y - 5),
                       (last_x + offset, last_y + length + 5), True)
        helper_functions.refresh()

    def shoot(self):
        if not self.dead and not self.arrive:
            self.shooting = True
            if self.power_level == 1 and (pg.time.get_ticks() > self.cool_down + 100):
                self.cool_down = pg.time.get_ticks()
                snd.load_sound("pewpew.wav")
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
                    snd.load_sound("pewpew2.wav")
                if self.t == 4:
                    self.allBullets.add(new_bullet3)
                    self.allBullets.add(new_bullet4)
                    snd.load_sound("pewpew2.wav")
                if self.t > 5:
                    self.t = 0
            elif self.power_level >= 3 and (pg.time.get_ticks() > self.cool_down + 20):
                self.t += 1
                self.cool_down = pg.time.get_ticks()

                new_bullet = main.Bullet(self.rect.centerx - 80, self.rect.y, gfx.img_bullet_3)
                new_bullet.dy = -20
                new_bullet.image = pg.transform.scale(new_bullet.image, (200, 100))

                if self.t >= 4:
                    self.allBullets.add(new_bullet)
                    snd.load_sound("pewpew3.wav")
                    self.t = 0

    def die(self):
        self.last_x = self.rect.x
        self.last_y = self.rect.y
        snd.load_sound("explode.wav")
        gfx.explosion(self.last_x, self.last_y)
        pg.time.delay(20)
        self.power_level = 1
        self.dead = True
