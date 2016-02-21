from os import path, environ
from random import choice, randrange, randint
from sys import exit
from time import time
import math

import pygame as pg

import constants
import gfx
import player
import snd
import helper_functions

# Shortcuts
SCREEN_CENTER = (constants.SCREEN_WIDTH / 2, constants.SCREEN_HEIGHT / 2)


class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, image):
        pg.sprite.Sprite.__init__(self)

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.size = (self.rect.x, self.rect.y)
        self.dx = 0
        self.dy = 0

    def update(self):
        x, y = self.rect.center
        x += self.dx
        y += self.dy
        self.rect.center = x, y

        if y <= 0:
            self.kill()

    def on_hit(self):
        s = gfx.screen.blit(gfx.img_hit, (self.rect.centerx - gfx.img_hit.get_width() / 2, self.rect.y))
        pg.display.update(s)


class PowerUp(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.images = []
        self.images.append(gfx.load_image("POWERUP/powerup_a.png"))
        self.images.append(gfx.load_image("POWERUP/powerup_b.png"))
        self.images.append(gfx.load_image("POWERUP/powerup_c.png"))
        self.next_anim_frame = 0
        self.index = 0
        self.image = self.images[self.index]
        self.rect = pg.Rect(0, 0, 40, 40)
        self.rect.x = randrange(40, constants.SCREEN_WIDTH - 40)
        self.rect.y = 1

    def update(self):
        self.next_anim_frame += 1
        if self.next_anim_frame >= 10:
            self.index += 1
            self.next_anim_frame = 0
            if self.index >= len(self.images):
                self.index = 0

            self.image = self.images[self.index]

        self.rect.y += 2

    def on_pickup(self):
        snd.load_sound("powerup.wav")
        self.kill()


class Stars(pg.sprite.Sprite):
    MAX_STARS = 100
    color = (0, 0, 0)

    def __init__(self):
        self.stars = []
        for i in range(self.MAX_STARS):
            star = [randrange(0, gfx.screen.get_width() - 1),
                    randrange(0, gfx.screen.get_height() - 1),
                    choice([1, 2, 3])]
            self.stars.append(star)

    def render(self):
        for star in self.stars:
            star[1] += star[2]
            if star[1] >= gfx.screen.get_height():
                star[1] = 0
                star[0] = randrange(0, constants.SCREEN_WIDTH)
                star[2] = choice([1, 2, 3])

            if star[2] == 1:
                self.color = (100, 100, 100)
            elif star[2] == 2:
                self.color = (190, 190, 190)
            elif star[2] == 3:
                self.color = (255, 255, 255)

            gfx.screen.fill(self.color, (star[0], star[1], star[2], star[2]))


class EnemyFighter(pg.sprite.Sprite):
    image = None
    HEALTH = 2
    BULLETS_MAX = 1
    allBullets = pg.sprite.Group()
    spawn_areas = [50, 100, 200, 300, 400, 500, 600, 700, 750]

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = gfx.img_fighter
        self.rect = self.image.get_rect()
        self.rect.x = choice(self.spawn_areas)
        self.rect.y = 0
        self.dx = 0
        self.dy = 3
        self.spawn_time = pg.time.get_ticks()
        self.bullets = pg.sprite.Group()
        self.has_shot = False
        self.is_hit = False
        self.change = 0
        self.angle = 0

    def movement(self):
        if self.rect.bottom > 300:
            self.dy = 2

        if self.rect.left <= 0 or self.rect.right >= constants.SCREEN_WIDTH:
            self.kill()

        if self.has_shot:
            self.dy = 4
            if self.rect.centerx > constants.SCREEN_WIDTH / 2:
                self.change += .1
            else:
                self.change -= .1

        self.rect.x += self.dx + self.change
        self.rect.y += self.dy

        self.angle += math.degrees(self.change) / 180

    def update(self):
        if self.is_hit:
            self.image = gfx.img_fighter_hit
            pg.display.update(self.rect)
            self.is_hit = False
        else:
            self.image = gfx.img_fighter

        if self.rect.y >= constants.SCREEN_HEIGHT:
            self.kill()
        else:
            self.movement()

        if self.HEALTH <= 0:
            self.die()

        for bullet in self.allBullets:
            bullet.image = choice([gfx.img_enemy_shot_a, gfx.img_enemy_shot_b])

        self.image = pg.transform.rotate(self.image, self.angle)

    def shoot(self, target):
        import math
        for bullet in range(self.BULLETS_MAX):
            new_bullet = Bullet(self.rect.centerx, self.rect.bottom, gfx.img_enemy_shot_a)
            new_bullet.dx = 5 * math.cos(helper_functions.calc_angle(self, target))
            new_bullet.dy = 5 * math.sin(helper_functions.calc_angle(self, target))
            self.allBullets.add(new_bullet)
            snd.load_sound("enemy_shoot.wav")
        self.has_shot = True

    def die(self):
        snd.load_sound("explode.wav")
        self.image = gfx.img_explosion
        s = gfx.screen.blit(self.image, (self.rect.x - 40, self.rect.y - 40))
        pg.display.update(s)
        pg.time.delay(10)
        self.kill()


class EnemyFrigate(pg.sprite.Sprite):
    image = None
    HEALTH = 50
    MAX_SHOTS = 3

    allBullets = pg.sprite.Group()

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.spawn_delay = 0
        self.image = gfx.img_frigate
        self.rect = self.image.get_rect()
        self.size = self.image.get_size()
        self.rect.x = 0
        self.rect.right = 0
        self.rect.bottom = 0
        self.dx = 1
        self.dy = 0
        self.is_hit = False

    def update(self):
        if self.is_hit:
            self.image = gfx.img_frigate_hit
            self.is_hit = False
            if self.HEALTH <= 0:
                self.die()
        else:
            self.image = gfx.img_frigate

        if self.rect.x == randint(100, 500):
            if len(self.allBullets) < self.MAX_SHOTS:
                self.shoot()

        self.rect.x += self.dx

    def shoot(self):
        missile = Bullet(self.rect.centerx, self.rect.bottom, gfx.img_missile)
        missile.image = pg.transform.rotate(missile.image, 180)
        missile.dy = 4
        self.allBullets.add(missile)

    def die(self):
        snd.load_sound("explode.wav")
        self.image = gfx.img_explosion_final
        self.image = pg.transform.scale(self.image, (300, 300))
        s = gfx.screen.blit(self.image, (self.rect.x - 50, self.rect.y - 120))
        pg.display.update(s)
        pg.time.delay(10)
        self.kill()


class EnemyCruiser(pg.sprite.Sprite):
    image = None
    HEALTH = 500

    allBullets = pg.sprite.Group()

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = gfx.img_cruiser
        self.rect = self.image.get_rect()
        self.size = self.image.get_size()
        self.rect.x = (constants.SCREEN_WIDTH / 2) - (self.size[0] / 2)
        self.center = (self.rect.x + 100, self.rect.y + 270)
        self.rect.bottom = 0
        self.dx = 0
        self.dy = 1
        self.is_hit = False
        self.charging = False
        self.firing = False
        self.has_shot = False
        self.next_shot = 0
        self.charge = 0
        self.duration = 0
        self.beamtime = 0

    def update(self):
        if self.is_hit:
            self.image = gfx.img_cruiser_hit
            self.is_hit = False
            if self.HEALTH <= 0:
                self.die()
        else:
            self.image = gfx.img_cruiser

        if not (self.charging or self.firing) and self.rect.bottom == constants.SCREEN_HEIGHT / 2:
            self.dy = 0
            self.charge = 0
            self.duration = 0
            self.next_shot += 1
            if self.next_shot >= 500:
                self.charging = True
                self.next_shot = 0

        if self.charging:
            self.firing = False
            self.charge += 1
            snd.load_sound("charging.wav")
            if self.charge >= 180:
                self.firing = True
        if self.firing:
            self.charging = False

            self.image = gfx.img_cruiser_firing
            self.beamtime += 1
            if self.beamtime >= 5:
                self.duration += 1
                self.fire_beam()
                self.beamtime = 0
                if self.duration >= 100:
                    self.image = gfx.img_cruiser
                    self.firing = False

        if self.rect.left > 0 and self.rect.right < constants.SCREEN_WIDTH:
            self.rect.centerx += self.dx
        self.rect.bottom += self.dy

    def fire_beam(self):

        beam = Bullet(self.rect.centerx, self.rect.bottom - 60, gfx.img_beam)
        beam.dy = 8
        self.allBullets.add(beam)
        snd.load_sound("firing_beam.wav")
        s = gfx.screen.blit(gfx.img_beam_arc,
                            (self.rect.centerx - (gfx.img_beam_arc.get_width() / 2), self.rect.bottom - 100))
        pg.display.update(s)
        self.has_shot = True

    def die(self):
        for i in range(9):
            pg.display.update(
                    gfx.explosion(self.center[0] + randrange(-100, 100, 20), self.center[1] + randrange(-100, 100, 20)))
            snd.load_sound("explode.wav")
            pg.time.delay(20)
        self.image = pg.transform.scale2x(gfx.load_image("explosion_last.png"))
        snd.load_sound("blow_up.wav")
        helper_functions.refresh()
        pg.time.wait(100)
        snd.play_song("gravitational_constant.ogg")
        self.kill()


class GameControl:
    clock = 0
    MAX_ENEMIES = 5
    ENEMIES_KILLED = 0
    KILL_COUNT = 0
    SCORE = 0

    def __init__(self):
        self.screen = gfx.screen
        self.font = None
        self.js = None
        self._is_running = False
        self.started = True
        self.t0 = time()
        self.t1 = 0
        self.time = 0
        self.FPS = 60
        self.player = player.Player()
        self.powerups = pg.sprite.Group()
        self.drop_chance = 5
        self.player_lives = 3
        self.dead_timer = 0
        self.stars = Stars()
        self.player_bullets = self.player.allBullets
        self.fighters = pg.sprite.Group()
        self.frigates = pg.sprite.Group()
        self.cruiser = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.enemy_bullets = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()
        self.spawn_timer = 0

    def on_init(self):
        environ["SDL_VIDEO_CENTERED"] = "1"

        pg.init()
        pg.display.init()
        pg.mixer.pre_init(44100, -16, 2, 2048)
        pg.mixer.init()
        pg.font.init()
        self.font = pg.font.Font(path.join("fonts", "spacebit.ttf"), constants.FONT_SIZE)
        self.clock = pg.time.Clock()

        # Check if controller is present
        pg.joystick.init()
        try:
            js = pg.joystick.Joystick(0)
            js.init()
        except:
            print("No joystick detected!")

        self.t1 = time()

    def on_event(self):
        pressed = pg.key.get_pressed()
        if not self.player.dead:
            if pressed[pg.K_UP]:
                self.player.move_up()
            if pressed[pg.K_DOWN]:
                self.player.move_down()
            if pressed[pg.K_LEFT]:
                self.player.move_left()
            if pressed[pg.K_RIGHT]:
                self.player.move_right()
            if pressed[pg.K_SPACE]:
                self.player.shoot()
        if pressed[pg.K_ESCAPE]:
            self._is_running = False

        # These handle input from a controller
        for event in pg.event.get():
            if not self.player.dead:
                if event.type == pg.JOYHATMOTION:
                    if self.js.get_hat(0) == (-1, 0):
                        self.player.move_left()
                    if self.js.get_hat(0) == (1, 0):
                        self.player.move_right()
                    if self.js.get_hat(0) == (0, 1):
                        self.player.move_up()
                    if self.js.get_hat(0) == (0, -1):
                        self.player.move_down()
                if event.type == pg.JOYBUTTONDOWN:
                    if self.js.get_button(0):
                        self.player.shoot()

    def update_loop(self):
        self.time = round(self.t1 - self.t0, 1)

        self.all_sprites.add(self.player_bullets)
        self.all_sprites.add(self.enemy_bullets)
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.enemies)
        self.all_sprites.add(self.powerups)

        if self.player_lives < 0:
            self._is_running = False

        if self.started and not self.player.arrive:
            if len(self.cruiser) < 1 and self.KILL_COUNT >= 120:
                snd.play_song("deadly_opposition.ogg")
                big_enemy = EnemyCruiser()
                self.cruiser.add(big_enemy)
                self.enemies.add(self.cruiser)

            if not self.player.dead and len(self.fighters) < self.MAX_ENEMIES:
                if len(self.cruiser) == 0:
                    self.spawn_timer += 1
                    if self.spawn_timer >= 20:
                        little_enemy = EnemyFighter()
                        self.fighters.add(little_enemy)
                        self.enemies.add(self.fighters)
                        self.spawn_timer = 0

                    if len(self.frigates) < 1:
                        frigate = EnemyFrigate()
                        frigate.rect.y = choice([50, 100, 150, 200, 250, 300])
                        frigate.rect.right = 0
                        self.frigates.add(frigate)
                        self.enemies.add(self.frigates)

            if self.ENEMIES_KILLED > 25:
                self.MAX_ENEMIES += 1
                self.ENEMIES_KILLED = 0

            for fighter in self.fighters:
                if not self.player.dead and not fighter.has_shot:
                    if abs(self.player.rect.y - fighter.rect.bottom <= 300) and abs(
                                            self.player.rect.centerx - fighter.rect.centerx <= 500) and fighter.rect.y <= 900:
                        fighter.shoot(self.player)
                        self.enemy_bullets.add(fighter.allBullets)

            for frigate in self.frigates:
                if frigate.rect.left >= constants.SCREEN_WIDTH:
                    frigate.kill()
                self.enemy_bullets.add(frigate.allBullets)

            for cruiser in self.cruiser:
                if self.player.dead:
                    cruiser.allBullets.empty()
                self.enemy_bullets.add(cruiser.allBullets)

            for enemy in self.enemies:
                if pg.sprite.collide_mask(self.player, enemy) and not self.player.invulnerable:
                    enemy.HEALTH -= 10
                    self.player.die()
                    self.player_lives -= 1
                elif pg.sprite.collide_rect(self.player, enemy) and self.player.invulnerable:
                    enemy.HEALTH = 0

            for bullet in self.enemy_bullets:
                if not self.player.dead and self.player.rect.colliderect(bullet.rect):
                    self.player.die()
                    bullet.kill()
                    self.player_lives -= 1

            for bullet in self.player_bullets:
                for enemy in self.enemies:
                    if enemy.HEALTH > 0 and enemy.rect.y >= 10 and pg.sprite.collide_mask(bullet, enemy):
                        bullet.on_hit()
                        snd.load_sound("hit.wav")
                        enemy.is_hit = True
                        enemy.HEALTH -= 1
                        bullet.kill()
                        if enemy.HEALTH <= 0:
                            self.ENEMIES_KILLED += 1
                            self.KILL_COUNT += 1
                            pwr_up = PowerUp()
                            pwr_up.rect = enemy.rect
                            if randint(1, 20) == self.drop_chance:
                                self.powerups.add(pwr_up)

            for beam in EnemyCruiser.allBullets:
                for fighter in self.fighters:
                    if pg.sprite.collide_mask(beam, fighter):
                        fighter.die()
                for frigate in self.frigates:
                    if pg.sprite.collide_mask(beam, frigate):
                        frigate.die()

            for powerup in self.powerups:
                if pg.sprite.collide_mask(powerup, self.player):
                    powerup.on_pickup()
                    self.player.power_level += 1

            for sprite in self.all_sprites:
                if 0 > sprite.rect.x > constants.SCREEN_WIDTH:
                    sprite.kill()
                    self.all_sprites.remove(sprite)
                if 0 > sprite.rect.y > constants.SCREEN_HEIGHT:
                    sprite.kill()
                    self.all_sprites.remove(sprite)

        self.all_sprites.update()
        self.clock.tick(self.FPS)

    def on_render(self):
        gfx.screen.blit(gfx.img_background, (0, 0))
        self.stars.render()
        score = self.font.render("ENEMIES KILLED: " + str(self.KILL_COUNT), True, constants.WHITE)
        lives = [(constants.SCREEN_WIDTH - (gfx.img_life.get_width() + 10),
                  constants.SCREEN_HEIGHT - gfx.img_life.get_height() - 20),
                 (constants.SCREEN_WIDTH - (gfx.img_life.get_width() + 10) * 2,
                  constants.SCREEN_HEIGHT - gfx.img_life.get_height() - 20), (
                     constants.SCREEN_WIDTH - (gfx.img_life.get_width() + 10) * 3,
                     constants.SCREEN_HEIGHT - gfx.img_life.get_height() - 20)]
        gfx.screen.blit(score, (20, constants.SCREEN_HEIGHT - 50))
        for i in range(self.player_lives):
            gfx.screen.blit(gfx.img_life, lives[i])
        pg.display.update(self.all_sprites.draw(gfx.screen))
        pg.display.flip()

    def on_cleanup(self):
        pg.quit()
        quit()
        exit()

    def title_screen(self):
        scroll = 0
        anim = 0
        ship_image = None

        while True:
            title_a = gfx.img_title_a
            title_b = gfx.img_title_b
            title_size = title_a.get_size()
            steps = int(title_size[0] / 2)
            for i in range(steps + 75):
                gfx.screen.blit(gfx.img_title_background, (0, 0))
                gfx.screen.blit(gfx.img_title_stars, (0, 100))
                gfx.screen.blit(title_a, (10 - title_size[0] + i * 2, 300))
                gfx.screen.blit(title_b, (10 + constants.SCREEN_WIDTH - i * 2, 300))
                pg.display.flip()
            snd.load_sound("blow_up.wav")
            for i in range(100):
                self.screen.fill((i,i,i))
                pg.display.update()
            gfx.screen.blit(gfx.img_title_background, (0, 0))
            snd.play_song("title_song.ogg")
            break

        while True:

            if scroll <= constants.SCREEN_WIDTH:
                scroll += .5
            else:
                scroll = 0

            gfx.screen.blit(gfx.img_title_stars, (scroll, 100))
            gfx.screen.blit(gfx.img_title_stars, (-constants.SCREEN_WIDTH + scroll, 100))
            gfx.screen.blit(gfx.img_title_whole, (SCREEN_CENTER[0] - gfx.img_title_whole.get_width() / 2 + 20, 300))

            for _ in range(1):
                if anim < 30:
                    ship_image = gfx.title_ship_a
                elif anim > 30:
                    ship_image = gfx.title_ship_b
                pg.display.update(self.screen.blit(ship_image,
                                 (SCREEN_CENTER[0] - (gfx.title_ship_a.get_width() / 2) + 20, 600)))

                if anim < 50:
                    menu = self.font.render("PRESS ENTER", True, constants.WHITE)
                    gfx.screen.blit(menu, (SCREEN_CENTER[0] - menu.get_width() / 2, SCREEN_CENTER[1]))
                elif anim > 50:
                    menu = self.font.render("PRESS ENTER", True, constants.BLACK)
                    gfx.screen.blit(menu, (SCREEN_CENTER[0] - menu.get_width() / 2, SCREEN_CENTER[1]))

            anim += 1
            if anim >= 100:
                anim = 0
            print(anim)

            pg.display.update()

            e = pg.event.poll()
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_RETURN:
                    snd.load_sound("takeoff.wav")
                    while True:
                        for i in range(255):
                            gfx.screen.fill((255 - i, 255 - i, 255 - i))
                            helper_functions.refresh()
                        break
                    break

        while True:
            text = self.font.render("GET READY", True, constants.WHITE)
            count_list = ["5", "4", "3", "2", "1", "GO!"]
            for i in range(6):
                countdown = self.font.render(count_list[i], True, constants.WHITE)
                gfx.screen.fill(constants.BLACK)
                gfx.screen.blit(text, (SCREEN_CENTER[0] - text.get_width() / 2, SCREEN_CENTER[1]))
                gfx.screen.blit(countdown, (SCREEN_CENTER[0] - countdown.get_width() / 2, SCREEN_CENTER[1] + 30))
                helper_functions.refresh()
                pg.time.wait(1000)
            break

        snd.play_song("gravitational_constant.ogg")
        self._is_running = True

    def game_over(self):
        pg.mixer.music.stop()
        snd.load_sound("music/death.ogg")
        gfx.screen.fill((255, 255, 255))
        for i in range(255):
            gfx.screen.fill((255 - i, 255 - i, 255 - i))
            helper_functions.refresh()
            pg.time.delay(10)
        import glob
        for image in sorted(glob.glob(path.join("graphics/GAMEOVER", "*.png"))):
            gfx.screen.fill(constants.BLACK)
            part = pg.image.load(image).convert()
            gfx.screen.blit(part, (SCREEN_CENTER[0] - 250, SCREEN_CENTER[1]))
            helper_functions.refresh()
            pg.time.delay(100)
        pg.time.wait(2000)

    def loop(self):
        self.title_screen()
        while self._is_running:
            self.started = True
            self.on_event()
            self.update_loop()
            self.on_render()

        self.game_over()


if __name__ == "__main__":
    game = GameControl()
    game.on_init()
    game.loop()
    game.on_cleanup()
