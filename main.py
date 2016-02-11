import pygame as pg
import player, constants, graphics, audio
from os import path, environ
from sys import exit
from random import choice, randrange, randint

# Configure display surface
screen = pg.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))

# Shortcuts
SCREEN_CENTER = (constants.SCREEN_WIDTH / 2, constants.SCREEN_HEIGHT / 2)


def refresh():
    return pg.display.flip()


# Font controller
pg.font.init()
font = pg.font.Font(path.join("fonts", "SPACEBIT.ttf"), constants.FONT_SIZE)

# Controller logic
pg.joystick.init()
try:
    js = pg.joystick.Joystick(0)
    js.init()
except:
    print("No joystick detected!")

# Record time that program began
start_time = pg.time.get_ticks()


def randomize(scale):
    return choice([-scale, 0, scale])


def calc_angle(origin, target):
    import math

    x = origin.rect.x
    y = origin.rect.y

    x2 = target.rect.x
    y2 = target.rect.y

    angle = math.atan2(y2 - y, x2 - x)

    return angle


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
        screen.blit(graphics.load_image("hit.png"), self.rect.center)
        refresh()


class PowerUp(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.images = []
        self.images.append(graphics.load_image("POWERUP/powerup_a.png"))
        self.images.append(graphics.load_image("POWERUP/powerup_b.png"))
        self.images.append(graphics.load_image("POWERUP/powerup_c.png"))
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
        audio.load_sound("powerup.wav")
        self.kill()


class Stars(pg.sprite.Sprite):
    MAX_STARS = 100

    # STAR_SPEED = 2

    def __init__(self):
        """ Create the starfield """
        self.stars = []
        for i in range(self.MAX_STARS):
            star = [randrange(0, screen.get_width() - 1),
                    randrange(0, screen.get_height() - 1),
                    choice([1, 2, 3])]
            self.stars.append(star)

    def render(self):
        """ Move and draw the stars in the given screen """
        for star in self.stars:
            star[1] += star[2]
            # If the star hit the bottom border then we reposition
            # it in the top of the screen with a random X coordinate.
            if star[1] >= screen.get_height():
                star[1] = 0
                star[0] = randrange(0, constants.SCREEN_WIDTH)
                star[2] = choice([1, 2, 3])

            # Adjust the star color according to the speed.
            # The slower the star, the darker should be its color.
            if star[2] == 1:
                color = (100, 100, 100)
            elif star[2] == 2:
                color = (190, 190, 190)
            elif star[2] == 3:
                color = (255, 255, 255)

            # Draw the star as a rectangle.
            # The star size is proportional to its speed.
            screen.fill(color, (star[0], star[1], star[2], star[2]))


class EnemyFighter(pg.sprite.Sprite):
    image = None
    HEALTH = 2
    BULLETS_MAX = 1
    allBullets = pg.sprite.Group()

    spawn_points = []
    for i in range(constants.SCREEN_WIDTH - 20):
        i += 20
        spawn_points.append(i)

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = graphics.load_image("fighter.png")
        self.rect = self.image.get_rect()
        self.rect.x = choice(self.spawn_points)
        self.rect.y = 0
        self.dx = 0
        self.dy = 4
        self.spawn_time = pg.time.get_ticks()
        self.bullets = pg.sprite.Group()
        self.has_shot = False
        self.is_hit = False
        self.change = 0

    def respawn(self):
        self.image = graphics.load_image("fighter.png")
        self.rect.x = choice(self.spawn_points)
        self.rect.y = 1
        self.dx = 0
        self.dy = 4

    def movement(self):
        if self.rect.left <= 0 or self.rect.right >= constants.SCREEN_WIDTH:
            self.kill()

        if self.has_shot:
            if self.rect.centerx > constants.SCREEN_WIDTH / 2:
                self.change += .2
            else:
                self.change -= .2

        self.rect.x += self.dx + self.change
        self.rect.y += self.dy

    def update(self):
        if self.is_hit:
            self.image = graphics.load_image("fighter_hit.png")
            self.is_hit = False
        else:
            self.image = graphics.load_image("fighter.png")

        if self.rect.y >= constants.SCREEN_HEIGHT:
            self.kill()
            self.respawn()
        else:
            self.movement()

        if self.HEALTH <= 0:
            self.die()

        for bullet in self.allBullets:
            bullet.image = choice([graphics.load_image("enemy_shot_a.png"),graphics.load_image("enemy_shot_b.png")])

    def shoot(self, target):
        import math
        new_bullet = Bullet(self.rect.x, self.rect.y, graphics.load_image("enemy_shot.png"))
        new_bullet.dx = 2 * math.cos(calc_angle(self, target)) * 5
        new_bullet.dy = 2 * math.sin(calc_angle(self, target)) * 5
        self.allBullets.add(new_bullet)
        self.has_shot = True

    def die(self):
        audio.load_sound("explode.wav")
        self.image = graphics.load_image("explosion.png")
        screen.blit(self.image, (self.rect.x - 40, self.rect.y - 40))
        refresh()
        pg.time.delay(10)
        App.ENEMIES_KILLED += 1
        self.kill()


class EnemyCruiser(pg.sprite.Sprite):
    image = None
    HEALTH = 400

    allBullets = pg.sprite.Group()

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = graphics.load_image("cruiser.png")
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
        self.t = 0
        self.beamtime = 0
        self.next_shot = 0

    def update(self):
        if self.is_hit:
            self.image = graphics.load_image("cruiser_hit.png")
            self.is_hit = False
        else:
            self.image = graphics.load_image("cruiser.png")

        self.rect.bottom += self.dy

        if not self.charging and self.rect.bottom == constants.SCREEN_HEIGHT / 2:
            self.dy = 0
            self.next_shot += 1

            if self.next_shot == 200:
                self.charging = True

        if self.HEALTH <= 0:
            self.die()

        if self.charging:
            self.t += 1
            if self.t >= 2:
                self.fire_beam()
                self.t = 0
                self.beamtime += 1
            elif self.beamtime >= 50:
                self.next_shot = 0
                self.beamtime = 0
                self.charging = False
        else:
            self.t = 0

        self.allBullets.update()

    def fire_beam(self):
        beam = Bullet(self.rect.centerx, self.rect.bottom - 60, graphics.load_image("beam.png"))
        beam.dy = 4
        self.allBullets.add(beam)
        audio.load_sound("firing_beam.wav")

    def die(self):
        for i in range(30):
            self.image = graphics.load_image("cruiser_hit.png")
            refresh()
            screen.blit(graphics.load_image("explosion.png"),
                        (self.center[0] + randrange(-150, 150), self.center[1] + randrange(-150, 150)))
            audio.load_sound("explode.wav")
            refresh()
            pg.time.delay(100)
            self.image = graphics.load_image("cruiser_hit.png")
            refresh()
        self.image = graphics.load_image("explosion_last.png")
        audio.load_sound("blow_up.wav")
        pg.time.wait(500)
        refresh()
        self.kill()

    def respawn(self):
        self.image = graphics.load_image("cruiser.png")
        self.rect.x = (constants.SCREEN_WIDTH / 2) - (self.size[0] / 2)
        self.rect.bottom = 0
        self.dx = 0
        self.dy = 1


class App:
    clock = pg.time.Clock()
    MAX_ENEMIES = 4
    ENEMIES_KILLED = 0
    KILL_COUNT = 0

    def __init__(self):
        self._is_running = False
        self.FPS = 120
        self.player = player.Player()
        self.powerups = pg.sprite.Group()
        self.player_lives = 3
        self.stars = Stars()
        self.player_bullets = self.player.allBullets
        self.fighters = pg.sprite.Group()
        self.cruiser = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.enemy_bullets = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()
        self.spawn_timer = 0

    def on_init(self):
        pg.init()
        pg.mixer.music.load(path.join("sounds", "deadly_opposition.ogg"))
        pg.mixer.music.set_volume(.5)

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

        if randint(0, 1000) == 1:
            self.powerups.add(PowerUp())
            self.all_sprites.add(self.powerups)

        if len(self.cruiser) == 0:
            big_enemy = EnemyCruiser()
            self.cruiser.add(big_enemy)
            self.enemies.add(self.cruiser)
            self.all_sprites.add(self.enemies)

        if not self.player.dead and len(self.fighters) < self.MAX_ENEMIES:
            self.spawn_timer += 1
            if self.spawn_timer == 5:
                little_enemy = EnemyFighter()
                self.fighters.add(little_enemy)
                self.enemies.add(self.fighters)
                self.spawn_timer = 0

        if self.player.dead:
            self.fighters.empty()

        if self.ENEMIES_KILLED > 10:
            self.MAX_ENEMIES += 1
            self.ENEMIES_KILLED = 0

        for enemy in self.fighters:
            if not self.player.dead:
                if enemy.rect.bottom >= 300 and not enemy.has_shot:
                    enemy.shoot(self.player)
                    self.enemy_bullets.add(enemy.allBullets)
            if self.player.rect.colliderect(enemy.rect):
                enemy.HEALTH -= 5
                self.die()

        for cruiser in self.cruiser:
            if pg.sprite.collide_mask(self.player, cruiser):
                cruiser.HEALTH -= 5
                self.die()
            self.enemy_bullets.add(cruiser.allBullets)

        for bullet in self.enemy_bullets:
            if not self.player.dead and self.player.rect.colliderect(bullet.rect):
                self.die()

        for bullet in self.player_bullets:
            for enemy in self.enemies:
                if pg.sprite.collide_mask(bullet, enemy):
                    bullet.on_hit()
                    enemy.is_hit = True
                    refresh()
                    audio.load_sound("hit.wav")
                    enemy.HEALTH -= 1
                    bullet.kill()

        for powerup in self.powerups:
            if pg.sprite.collide_mask(powerup, self.player):
                powerup.on_pickup()
                self.player.power_level += 1

        for sprite in self.all_sprites:
            if 0 > sprite.rect.x > constants.SCREEN_WIDTH:
                sprite.kill()
            if 0 > sprite.rect.y > constants.SCREEN_HEIGHT:
                sprite.kill()

        self.all_sprites.update()
        self.clock.tick(self.FPS)

    def on_render(self):
        screen.blit(graphics.load_image("background.bmp"), (0, 0))
        self.stars.render()
        score = font.render("ENEMIES KILLED: " + str(self.KILL_COUNT), True, constants.WHITE)
        lives = [(constants.SCREEN_WIDTH - graphics.load_image("life.png").get_size()[0], constants.SCREEN_HEIGHT - 40),
                 (constants.SCREEN_WIDTH - graphics.load_image("life.png").get_size()[0] * 2,
                  constants.SCREEN_HEIGHT - 40), (
                     constants.SCREEN_WIDTH - graphics.load_image("life.png").get_size()[0] * 3,
                     constants.SCREEN_HEIGHT - 40)]
        screen.blit(score, (20, constants.SCREEN_HEIGHT - 40))
        for i in range(self.player_lives):
            screen.blit(graphics.load_image("life.png"), lives[i])
        self.all_sprites.draw(screen)
        refresh()

    def on_cleanup(self):
        pg.quit()
        quit()
        exit()

    def title_screen(self):
        title_a = graphics.load_image("title_a.png")
        title_b = graphics.load_image("title_b.png")
        title_size = title_a.get_size()
        steps = int(title_size[0])
        for i in range(steps + 36):
            screen.fill(constants.BLUE)
            screen.blit(title_a, (-title_size[0] + i, 100))
            screen.blit(title_b, (constants.SCREEN_WIDTH - i, 100))
            refresh()
        audio.load_sound("blow_up.wav")
        menu = font.render("PRESS ENTER", True, constants.WHITE)
        screen.blit(menu, (SCREEN_CENTER[0] - menu.get_width() / 2, SCREEN_CENTER[1]))
        refresh()

        while True:
            e = pg.event.poll()
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_RETURN:
                    break

        for i in range(255):
            screen.fill((255 - i, 255 - i, 255 - i))
            refresh()

        text = font.render("GET READY", True, constants.WHITE)
        count_list = ['5', '4', '3', '2', '1', 'GO!']
        for i in range(6):
            countdown = font.render(count_list[i], True, constants.WHITE)
            screen.fill(constants.BLACK)
            screen.blit(text, (SCREEN_CENTER[0] - text.get_width() / 2, SCREEN_CENTER[1]))
            screen.blit(countdown, (SCREEN_CENTER[0] - countdown.get_width() / 2, SCREEN_CENTER[1] + 30))
            refresh()
            pg.time.wait(1000)
        self._is_running = True

    def game_over(self):
        pg.mixer.music.stop()
        screen.fill((255, 255, 255))
        for i in range(255):
            screen.fill((255 - i, 255 - i, 255 - i))
            refresh()
            pg.time.delay(10)
        import glob
        for image in sorted(glob.glob(path.join('graphics/GAMEOVER', '*.png'))):
            screen.fill(constants.BLACK)
            part = pg.image.load(image).convert()
            screen.blit(part, (SCREEN_CENTER[0] - 250, SCREEN_CENTER[1]))
            refresh()
            pg.time.delay(100)
        refresh()
        pg.time.wait(2000)

    def loop(self):
        self.title_screen()
        pg.mixer.music.play(-1)
        while self._is_running and self.player_lives > 0:
            self.on_event()
            self.update_loop()
            self.on_render()

        self.game_over()

    def die(self):
        self.player.last_x = self.player.rect.x
        self.player.last_y = self.player.rect.y
        self.player.image = graphics.load_image("explosion.png")
        audio.load_sound("blow_up.wav")
        screen.blit(graphics.load_image("explosion_last.png"), (self.player.last_x - 100, self.player.last_y - 200))
        audio.load_sound("explode.wav")
        for i in range(100):
            new_x = randomize(i) - 50
            new_y = randomize(i) - 50
            screen.blit(pg.transform.scale(graphics.load_image("explosion.png"), (101 - i, 101 - i)),
                        ((self.player.last_x + new_x) - i, (self.player.last_y + new_y) + i))
            screen.blit(pg.transform.scale(graphics.load_image("explosion.png"), (101 - i, 101 - i)),
                        ((self.player.last_x + new_x) + i, (self.player.last_y + new_y) - i))
            screen.blit(pg.transform.scale(graphics.load_image("explosion.png"), (101 - i, 101 - i)),
                        ((self.player.last_x + new_x) - i, (self.player.last_y + new_y) - i))
            screen.blit(pg.transform.scale(graphics.load_image("explosion.png"), (101 - i, 101 - i)),
                        ((self.player.last_x + new_x) + i, (self.player.last_y + new_y) + i))
            refresh()

        self.player.dead = True
        self.player.dead_timer = pg.time.get_ticks()
        self.player_lives -= 1


if __name__ == "__main__":
    environ['SDL_VIDEO_CENTERED'] = '1'
    game = App()
    game.on_init()
    game.loop()
    game.on_cleanup()
