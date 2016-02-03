import pygame as pg
import sys, os, random

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 1080
FONT_SIZE = 30

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.FULLSCREEN | pg.HWACCEL | pg.HWSURFACE)

# Shortcuts
SCREEN_CENTER = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

# Color key
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Load images
img_background = pg.image.load('background.bmp').convert()
img_bullet = pg.image.load('bullet.png').convert_alpha()
img_missile = pg.image.load('missile.png').convert_alpha()
img_explosion = pg.image.load('explosion.png').convert_alpha()
img_explosion_final = pg.image.load('explosion_last.png').convert_alpha()
img_explosion_final = pg.transform.scale2x(img_explosion_final)
img_player = pg.image.load('ship.png').convert_alpha()
img_enemy = pg.image.load('enemy.png').convert_alpha()
img_life = pg.image.load('life.png').convert_alpha()

# Load sounds
pg.mixer.pre_init(44100, -16, 2, 2048)
pg.mixer.init()
pg.mixer.music.load(os.path.join('star_razer.ogg'))
snd_shoot = pg.mixer.Sound('pewpew.wav')
snd_explode = pg.mixer.Sound('explode.wav')
snd_blow = pg.mixer.Sound('blow_up.wav')

# Load font system
pg.font.init()
font = pg.font.Font("SPACEBIT.ttf", FONT_SIZE)

# Controller logic
pg.joystick.init()
js = pg.joystick.Joystick(0)
js.init()


curr_time = pg.time.get_ticks()


def randomize(scale):
    return random.choice([-scale, 0, scale])


class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, image):
        pg.sprite.Sprite.__init__(self)

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.size = (self.rect.x, self.rect.y)
        self.dx = 0
        self.velocity = 0

    def update(self):
        x, y = self.rect.center
        x += self.dx
        y += self.velocity
        self.rect.center = x, y

        if y <= 0:
            self.kill()


class Player(pg.sprite.Sprite):
    bullets_max = 20
    bullets = []
    allBullets = pg.sprite.Group()

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = img_player
        self.dx = 0
        self.dy = 0
        self.speed = 10
        self.rect = self.image.get_rect()
        self.size = (self.rect[2], self.rect[3])
        self.rect.centerx = SCREEN_WIDTH / 2
        self.rect.bottom = SCREEN_HEIGHT - self.size[1]
        self.moving = False
        self.last_x = 0
        self.last_y = 0
        self.dead = False
        self.dead_timer = pg.time.get_ticks()
        self.cool_down = 0

    def update(self):
        if self.dead:
            self.rect.y = SCREEN_HEIGHT + 100
            if pg.time.get_ticks() - self.dead_timer > 3000:
                self.dead = False
                self.image = img_player
                self.rect.centerx = SCREEN_WIDTH / 2
                self.rect.bottom = SCREEN_HEIGHT - self.size[1]

        if self.rect.right > SCREEN_WIDTH:
            self.rect.x = SCREEN_WIDTH - self.size[0]
            self.dx = 0
        if self.rect.left < 0:
            self.rect.x = 0
            self.dx = 0
        if self.rect.bottom > SCREEN_HEIGHT and not self.dead:
            self.rect.bottom = SCREEN_HEIGHT
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
            if len(self.allBullets) < self.bullets_max:
                self.cool_down = pg.time.get_ticks()
                snd_shoot.play()
                new_bullet1 = Bullet(self.rect.centerx - 5, self.rect.bottom - self.size[1], img_bullet)
                new_bullet2 = Bullet(self.rect.centerx + 5, self.rect.bottom - self.size[1], img_bullet)
                new_bullet1.velocity = -5
                new_bullet2.velocity = -5
                self.allBullets.add(new_bullet1, new_bullet2)


class Stars(pg.sprite.Sprite):
    MAX_STARS = 100
    STAR_SPEED = 2

    def __init__(self):
        """ Create the starfield """
        self.stars = []
        for i in range(self.MAX_STARS):
            star = [random.randrange(0, screen.get_width() - 1),
                    random.randrange(0, screen.get_height() - 1),
                    random.choice([1, 2, 3])]
            self.stars.append(star)

    def render(self):
        """ Move and draw the stars in the given screen """
        for star in self.stars:
            star[1] += star[2]
            # If the star hit the bottom border then we reposition
            # it in the top of the screen with a random X coordinate.
            if star[1] >= screen.get_height():
                star[1] = 0
                star[0] = random.randrange(0, SCREEN_WIDTH)
                star[2] = random.choice([1, 2, 3])

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


class Enemy(pg.sprite.Sprite):
    image = None
    BULLETS_MAX = 1

    spawn_points = []
    for i in range(SCREEN_WIDTH - 20):
        i += 20
        spawn_points.append(i)

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = img_enemy
        self.rect = self.image.get_rect()
        self.rect.x = random.choice(self.spawn_points)
        self.rect.y = 0
        self.dx = 0
        self.dy = 1
        self.alive_time = 0
        self.spawn_time = pg.time.get_ticks()
        self.bullets = pg.sprite.Group()
        self.has_shot = False
        self.change = 0

    def respawn(self):
        self.image = img_enemy
        self.rect.x = random.choice(self.spawn_points)
        self.rect.y = 1
        self.dx = 0
        self.dy = 1

    def movement(self):
        if self.alive_time > self.spawn_time + 2000:
            self.dy += .1
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.kill()
        if self.has_shot:
            if self.rect.centerx > SCREEN_WIDTH / 2:
                self.change += 1
            else:
                self.change -= 1

    def update(self):
        self.alive_time += pg.time.get_ticks()
        if self.rect.y >= SCREEN_HEIGHT:
            self.kill()
            self.respawn()
        else:
            self.movement()

        self.rect.x += self.change
        self.rect.y += self.dy

    def die(self):
        snd_explode.play()
        self.image = img_explosion
        screen.blit(self.image, (self.rect.x - 40, self.rect.y - 40))
        pg.display.update()
        pg.time.delay(20)
        self.kill()


class App:
    clock = pg.time.Clock()
    MAX_ENEMIES = 4
    ENEMIES_KILLED = 0
    KILL_COUNT = 0

    def __init__(self):
        self._is_running = False
        self._show_title = True
        self.image = None
        self.FPS = 59
        self.player = Player()
        self.player_lives = 3
        self.stars = Stars()
        self.player_bullets = self.player.allBullets
        self.enemies = pg.sprite.Group()
        self.enemy_bullets = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()

    def on_init(self):
        pg.init()
        self.title_screen()
        for i in range(self.MAX_ENEMIES):
            e = Enemy()
            self.enemies.add(e)
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.enemies)
        pg.mixer.music.set_volume(.5)
        pg.mixer.music.play(-1)

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

        if self.player.dead:
            self.enemies.empty()
        elif len(self.enemies) < self.MAX_ENEMIES:
            e = Enemy()
            self.enemies.add(e)
            self.all_sprites.add(self.enemies)

        if self.ENEMIES_KILLED > 50:
            self.MAX_ENEMIES += 1
            self.ENEMIES_KILLED = 0

        for target in pg.sprite.groupcollide(self.enemies, self.player_bullets, False, True):
            if target.rect.y > 20:
                target.die()
                self.KILL_COUNT += 1
                self.ENEMIES_KILLED += 1

        for e in self.enemies:
            if not e.has_shot and e.rect.bottom >= 300:
                new_bullet = Bullet(e.rect.x, e.rect.y, img_missile)
                new_bullet.velocity = 6
                self.enemy_bullets.add(new_bullet)
                self.all_sprites.add(self.enemy_bullets)
                e.has_shot = True
            if not self.player.dead and pg.sprite.spritecollide(self.player, self.enemies, True):
                self.die()
            if not self.player.dead and pg.sprite.spritecollide(self.player, self.enemy_bullets, True):
                self.die()

        self.all_sprites.update()
        self.clock.tick(self.FPS)

    def on_render(self):
        screen.blit(img_background, (0, 0))
        self.stars.render()
        self.all_sprites.draw(screen)
        score = font.render("ENEMIES KILLED: " + str(self.KILL_COUNT), True, WHITE)
        lives = [(SCREEN_WIDTH - img_life.get_size()[0], SCREEN_HEIGHT - 40), (SCREEN_WIDTH - img_life.get_size()[0]*2, SCREEN_HEIGHT - 40), (SCREEN_WIDTH - img_life.get_size()[0]*3, SCREEN_HEIGHT - 40)]
        screen.blit(score, (20, SCREEN_HEIGHT - 40))
        for i in range(self.player_lives):
            screen.blit(img_life, lives[i])
        pg.display.flip()

    def on_cleanup(self):
        pg.quit()
        quit()
        sys.exit()

    def title_screen(self):
        title_a = pg.image.load('title_a.png').convert_alpha()
        title_b = pg.image.load('title_b.png').convert_alpha()
        title_size = title_a.get_size()
        steps = int(title_size[0])
        for i in range(steps + 36):
            screen.fill(BLUE)
            screen.blit(title_a, (-title_size[0] + i, 100))
            screen.blit(title_b, (SCREEN_WIDTH - i, 100))
            pg.display.update()
        snd_blow.play()
        menu = font.render("PRESS ENTER", True, WHITE)
        screen.blit(menu, (SCREEN_CENTER[0] - menu.get_width() / 2, SCREEN_CENTER[1]))
        pg.display.flip()

        while True:
            e = pg.event.poll()
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_RETURN:
                    break

        for i in range(255):
            screen.fill((255 - i, 255 - i, 255 - i))
            pg.display.flip()

        begin = font.render("GET READY", True, WHITE)
        count_list = ['5', '4', '3', '2', '1', 'GO!']
        for i in range(6):
            countdown = font.render(count_list[i], True, WHITE)
            screen.fill(BLACK)
            screen.blit(begin, (SCREEN_CENTER[0] - begin.get_width() / 2, SCREEN_CENTER[1]))
            screen.blit(countdown, (SCREEN_CENTER[0] - countdown.get_width() / 2, SCREEN_CENTER[1] + 30))
            pg.display.flip()
            pg.time.wait(1000)
        self._is_running = True

    def loop(self):
        while self._is_running and self.player_lives > 0:
            self.on_event()
            self.update_loop()
            self.on_render()

    def die(self):
        self.player.last_x = self.player.rect.x
        self.player.last_y = self.player.rect.y
        self.player.image = img_explosion
        snd_blow.play()
        screen.blit(img_explosion_final, (self.player.last_x - 200, self.player.last_y - 200))
        snd_explode.play()
        for i in range(100):
            new_x = randomize(i) - 50
            new_y = randomize(i) - 50
            screen.blit(pg.transform.scale(img_explosion, (101 - i, 101 - i)),
                        ((self.player.last_x + new_x) - i, (self.player.last_y + new_y) + i))
            screen.blit(pg.transform.scale(img_explosion, (101 - i, 101 - i)),
                        ((self.player.last_x + new_x) + i, (self.player.last_y + new_y) - i))
            screen.blit(pg.transform.scale(img_explosion, (101 - i, 101 - i)),
                        ((self.player.last_x + new_x) - i, (self.player.last_y + new_y) - i))
            screen.blit(pg.transform.scale(img_explosion, (101 - i, 101 - i)),
                        ((self.player.last_x + new_x) + i, (self.player.last_y + new_y) + i))
            pg.display.update()

        self.player.dead = True
        self.player.dead_timer = pg.time.get_ticks()
        self.player_lives -= 1


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    game = App()
    game.on_init()
    game.loop()
    game.on_cleanup()
