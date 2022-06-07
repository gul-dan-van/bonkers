import math
import pygame
from pygame.locals import *
import random
import copy

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 700

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
LIGHT_GREY = (220, 220, 220)
DARK_GREY = (30, 30, 30)

BAT_IMG = pygame.image.load("img/bonk.png")
DOGE_IMG = pygame.image.load("img/doge.png")
BUBBLE_IMG = [pygame.image.load(f"img/b{i}.png") for i in range(1, 6)]
SHIELD_IMG = pygame.image.load("img/shield.png")
MONSTER_IMG = [pygame.image.load(f"img/t{i}.png") for i in range(1, 6)]

SCORE_FONT = pygame.font.Font('font/impact.ttf', 30)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Bonkers")


def restart():
    global thrower
    global bats
    global monsters
    global bubbles
    global score

    thrower = Thrower()
    bats = pygame.sprite.Group()
    monsters = pygame.sprite.Group()
    bubbles = pygame.sprite.Group()
    score = Score()
    Monster.presence = 0


def draw_bg():
    screen.fill(BLACK)


def get_angle(ship):
    toMouse = pygame.mouse.get_pos() - ship.position
    angle = math.atan2(toMouse.y, toMouse.x)
    return -math.degrees(angle)


def get_magnitude(x, y):
    return (x * x + y * y) ** 0.5


def get_unit_vector(v):
    m = get_magnitude(v.x, v.y)
    if m == 0:
        return pygame.Vector2(0, 0)
    return v / get_magnitude(v.x, v.y)


def get_direction(ox, oy, x, y):
    a = x - ox
    b = y - oy

    mag = get_magnitude(a, b)

    return (a / mag, b / mag)


def wrap(pos, dim):
    a, b = dim[0], dim[1]
    if pos.x < -int(b * 1 / 4):
        return pygame.Vector2(screen_width - int(b * 1 / 4), pos.y)
    elif pos.x > screen_width + int(b * 1 / 4):
        return pygame.Vector2(-int(b * 1 / 4), pos.y)
    elif pos.y < -int(a * 1 / 4):
        return pygame.Vector2(pos.x, screen_height - int(a * 1 / 4))
    elif pos.y > screen_height + int(a * 1 / 4):
        return pygame.Vector2(pos.x, -int(a * 1 / 4))
    else:
        return pos


def spawn_monster(pos=None, threat=10):
    Monster.presence += threat
    monsters.add(Monster(pos, threat))


def draw_text( text, x, y, font, text_col = WHITE ):
    img = font.render( str(text) ,True ,text_col )
    w = img.get_width()
    screen.blit(img,(x-w//2,y))


class Score:
    def __init__(self):
        self.score = 0
        self.x = screen_width//2
        self.y = 0
        self.font = SCORE_FONT
        self.color = WHITE

    def render(self):
        draw_text(f'Score: {self.score}', self.x, self.y, self.font, self.color)

    def update(self):
        pass


class Bubble(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        pygame.sprite.Sprite.__init__(self)

        self.position = pos

        self.counter = 0
        self.new_frame_countdown = 7
        self.frameCnt = 5

        self.scale = [0.75,0.9,1.4][size]
        self.images = [
            pygame.transform.rotozoom(img, 0.0, self.scale) for img in BUBBLE_IMG
        ]
        self.texture = [0]

    def render(self):

        n = self.counter // self.new_frame_countdown
        if n < self.frameCnt:
            self.texture = self.images[(self.counter // self.new_frame_countdown)]
            screen.blit(
                self.texture,
                self.position - pygame.Vector2(self.texture.get_rect().size) * 0.5,
            )
            self.counter += 1
        else:
            self.kill()


class Thrower:

    bat_cooldown = 30
    counter = 0

    def __init__(self):

        self.position = pygame.Vector2(screen_width // 2, screen_height // 2)

        self.rotation = 0.0
        self.doge_scale = 0.85
        self.doge_dim = (
            DOGE_IMG.get_width() * self.doge_scale,
            DOGE_IMG.get_height() * self.doge_scale,
        )
        self.doge_img = pygame.transform.rotozoom(
            DOGE_IMG, self.rotation, self.doge_scale
        )

        self.bat_scale = 0.3
        self.bat_dim = (
            BAT_IMG.get_width() * self.bat_scale,
            BAT_IMG.get_height() * self.bat_scale,
        )
        self.bat_pos_offset = pygame.Vector2(20, 12)
        self.bat_angle_offset = -90
        self.bat_img = pygame.transform.rotozoom(BAT_IMG, self.rotation, self.bat_scale)
        self.mask = pygame.mask.from_surface(self.doge_img)

        self.speed = 5
        self.direction = pygame.Vector2(0, 0)
        self.color = BLUE

        # self.health = 3
        # self.healthBar = pygame.rect()

    def render(self):

        self.rotation = get_angle(self)
        self.doge_texture = pygame.transform.rotozoom(
            pygame.transform.flip(self.doge_img, 1, 0), self.rotation, self.doge_scale
        )
        self.mask = pygame.mask.from_surface(self.doge_texture)
        self.bat_texture = pygame.transform.rotozoom(
            pygame.transform.flip(self.bat_img, 1, 0),
            self.rotation + self.bat_angle_offset,
            self.bat_scale,
        )
        self.mask = pygame.mask.from_surface(self.doge_texture)

        screen.blit(
            self.doge_texture,
            self.position - pygame.Vector2(self.doge_texture.get_rect().size) * 0.5,
        )

        if self.counter > self.bat_cooldown:
            screen.blit(
                self.bat_texture,
                self.bat_pos_offset.rotate(-self.rotation)
                + self.position
                - pygame.Vector2(self.bat_texture.get_rect().size) * 0.5,
            )

        # pygame.draw.rect(screen,RED,self.rect)

    def update(self):

        # if pygame.sprite.collide_mask(self, monsters, False, pygame.sprite.collide_mask):
        #     self.kill()

        self.counter += 1

        keys = pygame.key.get_pressed()
        if keys[K_UP] or keys[K_w]:
            self.direction.y -= 1
        if keys[K_DOWN] or keys[K_s]:
            self.direction.y += 1
        if keys[K_LEFT] or keys[K_a]:
            self.direction.x -= 1
        if keys[K_RIGHT] or keys[K_d]:
            self.direction.x += 1

        self.position += get_unit_vector(self.direction) * self.speed
        self.position = wrap(self.position, self.doge_dim)

        if pygame.mouse.get_pressed()[0] and self.bat_cooldown < self.counter:

            self.counter = 0

            bats.add(
                Bat(
                    self.position + self.bat_pos_offset.rotate(-self.rotation),
                    self.rotation + self.bat_angle_offset,
                )
            )

        self.direction = pygame.Vector2(0, 0)


class Bat(pygame.sprite.Sprite):
    def __init__(self, pos, rotation):

        pygame.sprite.Sprite.__init__(self)

        self.rotation = rotation
        self.direction = pygame.Vector2(1, 0).rotate(-self.rotation - 90)

        self.scale = 0.3
        self.dim = (
            BAT_IMG.get_width() * self.scale,
            BAT_IMG.get_height() * self.scale,
        )
        self.img = pygame.transform.rotozoom(BAT_IMG, 0.0, self.scale)
        self.texture = pygame.transform.rotozoom(
            pygame.transform.flip(self.img, 1, 0), self.rotation, self.scale
        )
        self.position = pos - pygame.Vector2(self.texture.get_rect().size) * 0.5

        self.speed = 13
        self.color = RED

        self.counter = 0
        self.lifespan = 70

    def render(self):

        screen.blit(self.texture, self.position)
        self.mask = pygame.mask.from_surface(self.texture)

        self.counter += 1
        if self.counter > self.lifespan:
            self.kill()

    def update(self):

        self.position += get_unit_vector(self.direction) * self.speed
        self.position = wrap(self.position, self.dim)


class Monster(pygame.sprite.Sprite):

    presence = 0
    population_threshold = 39
    counter = 0
    spawn_cooldown = 60

    large = 10
    medium = 8
    small = 6

    def __init__(self, pos, threat):
        pygame.sprite.Sprite.__init__(self)

        self.threat = threat

        x, y = random.choice(
            [
                (random.randint(0, screen_width), 0),
                (random.randint(0, screen_width), screen_height),
                (0, random.randint(0, screen_height)),
                (screen_width, random.randint(0, screen_height)),
            ]
        )

        if pos == None:
            self.position = pygame.Vector2(x, y)
            self.direction = -(self.position - thrower.position).normalize()

        else:
            self.position = pos
            self.direction = pygame.Vector2(x, y).normalize()

        self.scale = threat * 2 / 10
        self.images = [
            pygame.transform.rotozoom(img, 0.0, self.scale) for img in MONSTER_IMG
        ]
        self.texture = self.images[0]

        self.speed = 3
        self.dim = (
            self.texture.get_width() * self.scale,
            self.texture.get_height() * self.scale,
        )

        self.timer = 0
        self.new_frame_countdown = 8
        self.n_images = len(self.images)

    def render(self):

        self.timer += 1

        self.texture = self.images[
            (self.timer // self.new_frame_countdown) % self.n_images
        ]
        self.mask = pygame.mask.from_surface(self.texture)
        self.dim = (
            self.texture.get_width(),
            self.texture.get_height(),
        )

        screen.blit(
            self.texture,
            self.position - pygame.Vector2(self.texture.get_rect().size) * 0.5,
        )

        w, h = self.dim[0], self.dim[1]
        a, b = self.position.x - w // 2, self.position.y - h // 2
        r = pygame.Rect(a, b, w, h)
        # pygame.draw.rect(screen, RED, r, 1)

    def update(self):
        t = copy.deepcopy(self.position)
        self.position += get_unit_vector(self.direction) * self.speed
        self.position = wrap(self.position, self.dim)


def update_monsters():
    Monster.counter += 1
    if (
        Monster.counter > Monster.spawn_cooldown
        and Monster.presence < Monster.population_threshold
    ):
        Monster.counter = 0
        spawn_monster()

    for monster in monsters:
        monster.render()
        monster.update()


def update_screen():

    thrower.render()
    thrower.update()

    for bat in bats:
        bat.render()
        bat.update()
        if bat.counter > bat.lifespan:
            bat.kill()

    update_monsters()
    score.render()

    for bubble in bubbles:
        bubble.render()


def thrower_monster_collisions():
    for monster in monsters:
        if thrower.mask.overlap(
            monster.mask, [*map(int, thrower.position - monster.position)]
        ):
            restart()


def killMonster(monster):
    threat = monster.threat
    Monster.presence -= threat

    w, h = int(monster.dim[0]), int(monster.dim[1])
    a, b = int(monster.position.x - w // 2), int(monster.position.y - h // 2)
    x1 = random.randrange(a, a + w//2)
    y1 = random.randrange(b, b + h//2)
    x2 = random.randrange(a-w//2, a)
    y2 = random.randrange(b-h//2, b)

    if threat == Monster.large:
        spawn_monster(pygame.Vector2(x1, y1), Monster.medium)
        spawn_monster(pygame.Vector2(x2, y2), Monster.medium)
        bubbles.add(Bubble(monster.position, 2))

    elif threat == Monster.medium:
        spawn_monster(pygame.Vector2(x1, y1), Monster.small)
        spawn_monster(pygame.Vector2(x2, y2), Monster.small)
        bubbles.add(Bubble(monster.position, 1))
    
    else:
        bubbles.add(Bubble(monster.position, 0))

    monster.kill()


def bat_monster_collisions():
    for monster in monsters:
        for bat in bats:
            if bat.mask.overlap(
                monster.mask, [*map(int, bat.position - monster.position)]
            ):
                bat.kill()
                score.score+=monster.threat
                killMonster(monster)

                # monster

                break


def check_collisions():

    thrower_monster_collisions()
    bat_monster_collisions()


thrower = Thrower()
bats = pygame.sprite.Group()
monsters = pygame.sprite.Group()
bubbles = pygame.sprite.Group()
score = Score()


def game():

    run = True
    while run:
        clock.tick(fps)

        draw_bg()
        update_screen()
        check_collisions()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    game()
