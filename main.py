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

# Font controller
pg.font.init()
font = pg.font.Font(path.join("fonts", "spacebit.ttf"), constants.FONT_SIZE)

# Controller logic
pg.joystick.init()
try:
    js = pg.joystick.Joystick(0)
    js.init()
except:
    print("No joystick detected!")

# Record time that program began
start_time = pg.time.get_ticks()


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
        gfx.screen.blit(gfx.img_hit, (self.rect.centerx - gfx.img_hit.get_width() / 2, self.rect.y))
        helper_functions.refresh()


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
    HEALTH = 4
    BULLETS_MAX = 3
    allBullets = pg.sprite.Group()

    spawn_points = []
    spawn_points.append(100)
    spawn_points.append(200)
    spawn_points.append(300)
    spawn_points.append(400)
    spawn_points.append(500)

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = gfx.img_fighter
        self.rect = self.image.get_rect()
        self.rect.x = choice(self.spawn_points)
        self.rect.y = 0
        self.dx = 0
        self.dy = 4
        self.spawn_time = pg.time.get_ticks()
        self.bullets = pg.sprite.Group()
        self.has_shot = False
        self.next_shot = 0
        self.is_hit = False
        self.change = 0
        self.angle = 0

    def movement(self):
        if self.rect.bottom > 300:
            self.dy = 1

        if self.rect.left <= 0 or self.rect.right >= constants.SCREEN_WIDTH:
            self.kill()

        if self.has_shot:
            self.dy = 5
            if self.rect.centerx > constants.SCREEN_WIDTH / 2:
                self.change += .2
            else:
                self.change -= .2

        self.rect.x += self.dx + self.change
        self.rect.y += self.dy

        self.angle += math.degrees(self.change) / 180
        self.image = pg.transform.rotate(gfx.img_fighter, self.angle)

    def update(self):
        if self.is_hit:
            self.image = gfx.img_fighter_hit
            self.is_hit = False
        else:
            self.image = gfx.img_fighter

        if self.rect.y >= constants.SCREEN_HEIGHT:
            self.kill()
            self.respawn()
        else:
            self.movement()

        if self.HEALTH <= 0:
            self.die()

        for bullet in self.allBullets:
            bullet.image = choice([gfx.img_enemy_shot_a, gfx.img_enemy_shot_b])

    def shoot(self, target):
        import math
        for bullet in range(self.BULLETS_MAX):
            new_bullet = Bullet(self.rect.centerx, self.rect.bottom, gfx.img_enemy_shot_a)
            new_bullet.dx = round(2 * math.cos(helper_functions.calc_angle(self, target)) * 5,
                                  1) + helper_functions.randomize(.2)
            new_bullet.dy = round(2 * math.sin(helper_functions.calc_angle(self, target)) * 5,
                                  1) + helper_functions.randomize(.2)
            self.allBullets.add(new_bullet)
        self.has_shot = True

    def die(self):
        snd.load_sound("explode.wav")
        self.image = gfx.img_explosion
        gfx.screen.blit(self.image, (self.rect.x - 40, self.rect.y - 40))
        helper_functions.refresh()
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
        self.last_x = 0
        self.last_y = 0
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
        self.image = gfx.img_explosion
        gfx.screen.blit(self.image, (self.rect.x - 40, self.rect.y - 40))
        helper_functions.refresh()
        pg.time.delay(10)
        self.kill()


class EnemyCruiser(pg.sprite.Sprite):
    image = None
    HEALTH = 400

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
        self.last_x = 0
        self.last_y = 0
        self.is_hit = False
        self.charging = False
        self.has_shot = False
        self.t = 0
        self.beamtime = 0
        self.next_shot = 0

    def update(self):
        if self.is_hit:
            self.image = gfx.img_cruiser_hit
            self.is_hit = False
            if self.HEALTH <= 0:
                self.die()
        else:
            self.image = gfx.img_cruiser

        if not self.charging and self.rect.bottom == constants.SCREEN_HEIGHT / 2:
            self.dy = 0
            self.next_shot += 1
            if self.next_shot >= 200:
                self.charging = True

        if self.charging:
            self.image = gfx.img_cruiser_firing
            self.t += 1
            if self.t >= 5:
                self.fire_beam()
                self.t = 0
                self.beamtime += 1
                if self.beamtime >= 50:
                    self.next_shot = 0
                    self.beamtime = 0
                    self.charging = False

        if self.rect.left > 0 and self.rect.right < constants.SCREEN_WIDTH:
            self.rect.centerx += self.dx
        self.rect.bottom += self.dy

    def fire_beam(self):
        beam = Bullet(self.rect.centerx, self.rect.bottom - 60, gfx.img_beam)
        beam.dy = 8
        self.allBullets.add(beam)
        snd.load_sound("firing_beam.wav")
        gfx.screen.blit(gfx.img_beam_arc,
                        (self.rect.centerx - (gfx.img_beam_arc.get_width() / 2), self.rect.bottom - 100))
        helper_functions.refresh()
        self.has_shot = True

    def die(self):
        for i in range(30):
            self.image = gfx.img_cruiser_hit
            helper_functions.refresh()
            gfx.screen.blit(gfx.img_explosion,
                            (self.center[0] + randrange(-150, 150), self.center[1] + randrange(-150, 150)))
            snd.load_sound("explode.wav")
            helper_functions.refresh()
        self.image = gfx.load_image("explosion_last.png")
        snd.load_sound("blow_up.wav")
        pg.time.wait(500)
        helper_functions.refresh()
        self.kill()

    def respawn(self):
        self.image = gfx.img_cruiser
        self.rect.x = (constants.SCREEN_WIDTH / 2) - (self.size[0] / 2)
        self.rect.bottom = 0
        self.dx = 0
        self.dy = 1


class GameControl:
    clock = 0
    MAX_ENEMIES = 2
    ENEMIES_KILLED = 0
    KILL_COUNT = 0
    SCORE = 0

    def __init__(self):
        self._is_running = False
        self.started = True
        self.t0 = time()
        self.t1 = 0
        self.time = 0
        self.FPS = 40
        self.player = player.Player()
        self.powerups = pg.sprite.Group()
        self.drop_chance = 5
        self.player_lives = 3
        self.dead_timer = 0
        self.stars = Stars()
        self.player_bullets = self.player.allBullets
        self.fighters = pg.sprite.Group()
        self.frigates = pg.sprite.Group()
        self.spawn_areas = [100, 200, 300, 400]
        self.cruiser = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.enemy_bullets = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()
        self.spawn_timer = 0

    def on_init(self):
        pg.init()
        self.clock = pg.time.Clock()

    def on_event(self):
        for event in pg.event.get():
            if not self.player.dead:
                if event.type == pg.JOYHATMOTION:
                    if js.get_hat(0) == (-1, 0):
                        print("HAT_Left")
                        self.player.move_left()
                    if js.get_hat(0) == (1, 0):
                        print("HAT_Right")
                        self.player.move_right()
                    if js.get_hat(0) == (0, 1):
                        print("HAT_Up")
                        self.player.move_up()
                    if js.get_hat(0) == (0, -1):
                        print("HAT_Down")
                        self.player.move_down()
                if event.type == pg.JOYBUTTONDOWN:
                    if js.get_button(0):
                        self.player.shoot()

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

    def update_loop(self):
        self.all_sprites.add(self.player_bullets)
        self.all_sprites.add(self.enemy_bullets)
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.enemies)
        self.all_sprites.add(self.powerups)

        if self.started:
            self.t1 = 0 + time()
            self.time = round(self.t1 - self.t0, 1)

        if self.time > 10 and not self.player.arrive:
            if len(self.cruiser) == 0 and self.KILL_COUNT == 5:
                big_enemy = EnemyCruiser()
                self.cruiser.add(big_enemy)
                self.enemies.add(self.cruiser)

            if not self.player.dead and len(self.fighters) < self.MAX_ENEMIES:
                self.spawn_timer += 1
                if self.spawn_timer == 10:
                    little_enemy = EnemyFighter()
                    little_enemy.rect.x == choice(self.spawn_areas)
                    self.fighters.add(little_enemy)
                    self.enemies.add(self.fighters)
                    self.spawn_timer = 0

            if not self.player.dead and len(self.frigates) < 1:
                frigate = EnemyFrigate()
                frigate.rect.y = choice(self.spawn_areas)
                frigate.rect.right = 0
                self.frigates.add(frigate)
                self.enemies.add(self.frigates)

            if self.ENEMIES_KILLED > 25:
                self.MAX_ENEMIES += 1
                self.ENEMIES_KILLED = 0

            for fighter in self.fighters:
                if not self.player.dead and not fighter.has_shot:
                    if abs(self.player.rect.y - fighter.rect.bottom <= 300) and abs(
                                            self.player.rect.centerx - fighter.rect.centerx <= 300):
                        fighter.shoot(self.player)
                        self.enemy_bullets.add(fighter.allBullets)
                if self.player.rect.colliderect(fighter.rect):
                    fighter.HEALTH -= 5
                    self.player.die()
                if fighter.HEALTH <= 0:
                    fighter.die()
                    self.KILL_COUNT += 1

            for frigate in self.frigates:
                if frigate.rect.left >= constants.SCREEN_WIDTH:
                    frigate.kill()
                self.enemy_bullets.add(frigate.allBullets)

            for cruiser in self.cruiser:
                if self.player.dead:
                    cruiser.charge_timer = 0
                self.enemy_bullets.add(cruiser.allBullets)

            for enemy in self.enemies:
                if pg.sprite.collide_mask(self.player, enemy):
                    enemy.HEALTH -= 10
                    self.player.die()
                    self.player_lives -= 1

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
        score = font.render("ENEMIES KILLED: " + str(self.KILL_COUNT), True, constants.WHITE)
        lives = [(constants.SCREEN_WIDTH - (gfx.img_life.get_width() + 10),
                  constants.SCREEN_HEIGHT - gfx.img_life.get_height() - 20),
                 (constants.SCREEN_WIDTH - (gfx.img_life.get_width() + 10) * 2,
                  constants.SCREEN_HEIGHT - gfx.img_life.get_height() - 20), (
                     constants.SCREEN_WIDTH - (gfx.img_life.get_width() + 10) * 3,
                     constants.SCREEN_HEIGHT - gfx.img_life.get_height() - 20)]
        gfx.screen.blit(score, (20, constants.SCREEN_HEIGHT - 50))
        for i in range(self.player_lives):
            gfx.screen.blit(gfx.img_life, lives[i])
        self.all_sprites.draw(gfx.screen)
        helper_functions.refresh()

    def on_cleanup(self):
        pg.quit()
        quit()
        exit()

    def title_screen(self):
        pg.mixer.music.load(path.join("sounds", "music", "title_song.ogg"))
        pg.mixer.music.set_volume(.5)
        pg.mixer.music.play(-1)
        title_a = gfx.img_title_a
        title_b = gfx.img_title_b
        title_size = title_a.get_size()
        steps = int(title_size[0])
        for i in range(steps + 36):
            gfx.screen.blit(gfx.img_title_background, (0, 0))
            gfx.screen.blit(gfx.img_title_stars, (0, 100))
            gfx.screen.blit(title_a, (-title_size[0] + i, 100))
            gfx.screen.blit(title_b, (constants.SCREEN_WIDTH - i, 100))
            helper_functions.refresh()
        snd.load_sound("blow_up.wav")

        while True:
            while True:
                e = pg.event.poll()
                if e.type == pg.KEYDOWN:
                    if e.key == pg.K_RETURN:
                        snd.load_sound("explode.wav")
                        break

                menu = font.render("PRESS ENTER", True, constants.WHITE)
                gfx.screen.blit(menu, (SCREEN_CENTER[0] - menu.get_width() / 2, SCREEN_CENTER[1]))
                helper_functions.refresh()
                pg.time.wait(100)
                menu = font.render("PRESS ENTER", True, constants.BLACK)
                gfx.screen.blit(menu, (SCREEN_CENTER[0] - menu.get_width() / 2, SCREEN_CENTER[1]))
                helper_functions.refresh()
                pg.time.wait(100)

            break

        for i in range(255):
            gfx.screen.fill((255 - i, 255 - i, 255 - i))
            helper_functions.refresh()

        text = font.render("GET READY", True, constants.WHITE)
        count_list = ["5", "4", "3", "2", "1", "GO!"]
        for i in range(6):
            countdown = font.render(count_list[i], True, constants.WHITE)
            gfx.screen.fill(constants.BLACK)
            gfx.screen.blit(text, (SCREEN_CENTER[0] - text.get_width() / 2, SCREEN_CENTER[1]))
            gfx.screen.blit(countdown, (SCREEN_CENTER[0] - countdown.get_width() / 2, SCREEN_CENTER[1] + 30))
            helper_functions.refresh()
            pg.time.wait(1000)
        self._is_running = True

    def game_over(self):
        pg.mixer.music.stop()
        gfx.screen.fill((255, 255, 255))
        for i in range(255):
            gfx.screen.fill((255 - i, 255 - i, 255 - i))
            helper_functions.refresh()
            pg.time.delay(10)
        import glob
        for image in sorted(glob.glob(path.join("gfx/GAMEOVER", "*.png"))):
            gfx.screen.fill(constants.BLACK)
            part = pg.image.load(image).convert()
            gfx.screen.blit(part, (SCREEN_CENTER[0] - 250, SCREEN_CENTER[1]))
            helper_functions.refresh()
            pg.time.delay(100)
        pg.time.wait(2000)

    def loop(self):
        self.title_screen()
        pg.mixer.music.stop()
        pg.mixer.music.load(path.join("sounds", "music", "deadly_opposition.ogg"))
        pg.mixer.music.play(-1)
        while self._is_running and self.player_lives > 0:
            self.started = True
            self.on_event()
            self.update_loop()
            self.on_render()

        self.game_over()


if __name__ == "__main__":
    environ["SDL_VIDEO_CENTERED"] = "1"
    game = GameControl()
    game.on_init()
    game.loop()
    game.on_cleanup()
