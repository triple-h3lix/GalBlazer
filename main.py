import pygame as pg
import sys, os, random
import numpy, math

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 1080
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.FULLSCREEN)
FPS = 60

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
img_explosion_final = pg.image.load('explosion_last.png')
img_explosion_final = pg.transform.scale2x(img_explosion_final)
img_player = pg.image.load('ship.png').convert_alpha()
img_enemy = pg.image.load('enemy.png').convert_alpha()

# Load sounds
pg.mixer.init(44100, -16, 2, 2048)
pg.mixer.music.load(os.path.join('star_razer.ogg'))
snd_shoot = pg.mixer.Sound('pewpew.wav')
snd_explode = pg.mixer.Sound('explode.wav')
snd_blow = pg.mixer.Sound('blow_up.wav')

# Load font system
pg.font.init()
font = pg.font.Font("SPACEBIT.ttf", 30)


def randomize(scale):
    n = random.choice([-scale, 0, scale])

    return n


def left_or_right():
    direction = [-90, 90]
    turn = random.choice(direction)
    return turn

class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, image):
        pg.sprite.Sprite.__init__(self)

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.size = (self.rect.x, self.rect.y)
        self.dx = 0
        self.velocity = 0
        self.delta = (self.dx, self.velocity)
        self.alive = pg.time.get_ticks()

    def update(self):
        x, y = self.rect.center
        x += self.dx * randomize(1)
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
        self.speed = 5
        self.rect = self.image.get_rect()
        self.size = (self.rect[2], self.rect[3])
        self.rect.centerx = SCREEN_WIDTH / 2
        self.rect.bottom = SCREEN_HEIGHT - self.size[1]
        self.moving = False
        self.last_x = 0
        self.last_y = 0
        self.dead = False
        self.dead_timer = pg.time.get_ticks()

    def update(self):
        if self.dead:
            self.rect.y = SCREEN_HEIGHT + 100
            if pg.time.get_ticks() - self.dead_timer > 3000:
                self.dead = False
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
        if len(self.allBullets) < self.bullets_max:
            snd_shoot.play()
            new_bullet = Bullet(self.rect.centerx, self.rect.bottom - self.size[1], img_bullet)
            new_bullet.velocity = -20
            new_bullet.dx = 5
            self.allBullets.add(new_bullet)

    def die(self):
        self.last_x = self.rect.x
        self.last_y = self.rect.y
        for i in range(10):
            snd_explode.play()
            new_x = randomize(40) - 40
            new_y = randomize(40) - 40
            screen.blit(img_explosion_final, (self.last_x - 80, self.last_y - 80))
            screen.blit(img_explosion, (self.last_x + new_x, self.last_y + new_y))
            pg.time.delay(50)
            pg.display.update()
        self.dead = True
        self.dead_timer = pg.time.get_ticks()

    def render(self, surface):
        if not self.dead:
            surface.blit(self.image, (self.rect.x, self.rect.y))
            self.allBullets.draw(screen)

        pg.display.update()


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
        self.dy = 4
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
        if self.alive_time > self.spawn_time + 1000:
            self.dy += .1
        if self.rect.left <= 0:
            self.kill()
        if self.rect.right >= SCREEN_WIDTH:
            self.kill()
        if self.has_shot:
            if self.rect.centerx > SCREEN_WIDTH/2:
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
        self.image = None
        self.FPS = 60
        self.player = Player()
        self.stars = Stars()
        self.player_bullets = self.player.allBullets
        self.enemies = pg.sprite.Group()
        self.enemy_bullets = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()

    def on_init(self):
        pg.init()
        self._is_running = True
        for i in range(self.MAX_ENEMIES):
            e = Enemy()
            self.enemies.add(e)
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.enemies)
        pg.mixer.music.play(-1)

    def on_event(self):
        event = pg.event.get()
        if event == pg.QUIT:
            quit()
        pressed = pg.key.get_pressed()
        if not self.player.dead:
            if pressed[pg.K_w]:
                self.player.move_up()
            if pressed[pg.K_s]:
                self.player.move_down()
            if pressed[pg.K_a]:
                self.player.move_left()
            if pressed[pg.K_d]:
                self.player.move_right()
            if pressed[pg.K_SPACE]:
                self.player.shoot()
        if pressed[pg.K_ESCAPE]:
            self._is_running = False

    def update_loop(self):
        self.all_sprites.add(self.player_bullets)
        self.all_sprites.add(self.enemy_bullets)
        self.all_sprites.update()

        if self.ENEMIES_KILLED > 30:
            self.MAX_ENEMIES += 1
            self.ENEMIES_KILLED = 0

        for target in pg.sprite.groupcollide(self.enemies, self.player_bullets, False, True):
            if target.rect.y > 20:
                target.die()
                self.KILL_COUNT += 1
                self.ENEMIES_KILLED += 1

        for e in self.enemies:
            if not e.has_shot and e.rect.bottom >= 400:
                new_bullet = Bullet(e.rect.x, e.rect.y, img_missile)
                new_bullet.velocity = 5
                new_bullet.dx = 0
                self.enemy_bullets.add(new_bullet)
                self.all_sprites.add(self.enemy_bullets)
                e.has_shot = True
            if not self.player.dead and pg.sprite.spritecollide(self.player, self.enemies, True):
                self.player.die()
                screen.blit(img_explosion_final, (self.player.last_x, self.player.last_y))
                snd_blow.play()
            if not self.player.dead and pg.sprite.spritecollide(self.player, self.enemy_bullets, True):
                self.player.die()
                screen.blit(img_explosion_final, (self.player.last_x, self.player.last_y))
                snd_blow.play()

        if len(self.enemies) < self.MAX_ENEMIES:
            e = Enemy()
            self.enemies.add(e)
            self.all_sprites.add(self.enemies)

        self.clock.tick(self.FPS)

    def on_render(self):
        screen.blit(img_background, (0, 0))
        self.stars.render()
        self.all_sprites.draw(screen)
        score = font.render("ENEMIES KILLED: " + str(self.KILL_COUNT), True, WHITE)
        screen.blit(score, (20, SCREEN_HEIGHT - 40))
        pg.display.flip()

    def on_cleanup(self):
        pg.quit()

    def loop(self):
        while self._is_running:
            self.on_event()
            self.update_loop()
            self.on_render()


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    game = App()
    game.on_init()
    game.loop()
    game.on_cleanup()
    sys.exit()
