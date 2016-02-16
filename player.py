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
        self.last_x = 0
        self.last_y = 0
        self.dead = False
        self.dead_timer = pg.time.get_ticks()
        self.cool_down = 0
        self.power_level = 1

    def update(self):
        if self.arrive:
            self.dy = -10
            self.rect.y += self.dy
            self.draw_trail(constants.SCREEN_HEIGHT, 3)
            if self.rect.bottom < constants.SCREEN_HEIGHT - 100:
                self.arrive = False
        else:

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

            if self.dead:
                self.rect.y = self.start_position
                self.dead_timer += 1
                if self.dead_timer >= 100:
                    self.dead = False
                    self.arrive = True
                    self.image = gfx.img_player
                    self.rect.centerx = constants.SCREEN_WIDTH / 2
                    self.dead_timer = 0

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
        pg.draw.line(gfx.screen, (65, 255, 255), (last_x-offset, last_y-5), (last_x-offset, last_y+length), 5)
        pg.draw.line(gfx.screen, (65, 255, 255), (last_x+offset, last_y-5), (last_x+offset, last_y+length), 5)
        pg.draw.aaline(gfx.screen, (255, 255, 255), (last_x-offset, last_y-5), (last_x-offset, last_y+length+5), True)
        pg.draw.aaline(gfx.screen, (255, 255, 255), (last_x+offset, last_y-5), (last_x+offset, last_y+length+5), True)
        helper_functions.refresh()

    def shoot(self):
        if not self.dead and not self.arrive:
            if pg.time.get_ticks() > self.cool_down + 50:
                if self.power_level == 1:
                    self.cool_down = pg.time.get_ticks()
                    snd.load_sound("pewpew.wav")
                    new_bullet1 = main.Bullet(self.rect.centerx - 5, self.rect.bottom - self.size[1],
                                              gfx.img_bullet)
                    new_bullet2 = main.Bullet(self.rect.centerx + 5, self.rect.bottom - self.size[1],
                                              gfx.img_bullet)
                    new_bullet1.dy = -10
                    new_bullet2.dy = -10
                    self.allBullets.add(new_bullet1, new_bullet2)
                if self.power_level >= 2:
                    self.cool_down = pg.time.get_ticks()
                    snd.load_sound("pewpew2.wav")
                    new_bullet1 = main.Bullet(self.rect.centerx - 10, self.rect.bottom - self.size[1],
                                              gfx.img_bullet_upgraded)
                    new_bullet2 = main.Bullet(self.rect.centerx + 10, self.rect.bottom - self.size[1],
                                              gfx.img_bullet_upgraded)
                    new_bullet3 = main.Bullet(self.rect.centerx - 25, self.rect.bottom - self.size[1],
                                              gfx.img_bullet_upgraded)
                    new_bullet4 = main.Bullet(self.rect.centerx + 25, self.rect.bottom - self.size[1],
                                              gfx.img_bullet_upgraded)
                    new_bullet1.dy = -15
                    new_bullet2.dy = -15
                    new_bullet3.dy = -15
                    new_bullet4.dy = -15
                    self.allBullets.add(new_bullet1, new_bullet2, new_bullet3, new_bullet4)

    def die(self):
        self.last_x = self.rect.x
        self.last_y = self.rect.y
        self.image = gfx.img_explosion
        snd.load_sound("blow_up.wav")
        gfx.screen.blit(gfx.load_image("explosion_last.png"), (self.last_x - 100, self.last_y - 200))
        snd.load_sound("explode.wav")
        for i in range(100):
            new_x = helper_functions.randomize(i) - 50
            new_y = helper_functions.randomize(i) - 50
            gfx.screen.blit(pg.transform.scale(gfx.img_explosion, (101 - i, 101 - i)),
                            ((self.last_x + new_x) - i, (self.last_y + new_y) + i))
            gfx.screen.blit(pg.transform.scale(gfx.img_explosion, (101 - i, 101 - i)),
                            ((self.last_x + new_x) + i, (self.last_y + new_y) - i))
            gfx.screen.blit(pg.transform.scale(gfx.img_explosion, (101 - i, 101 - i)),
                            ((self.last_x + new_x) - i, (self.last_y + new_y) - i))
            gfx.screen.blit(pg.transform.scale(gfx.img_explosion, (101 - i, 101 - i)),
                            ((self.last_x + new_x) + i, (self.last_y + new_y) + i))
            helper_functions.refresh()

        self.dead = True

