import math
import pygame
from pygame.locals import *
import random

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

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Bonkers")

def draw_bg():
    screen.fill(BLACK)

class Bat:
    def __init__(self, x, rot, dir):
        self.position = pygame.Vector2( x, screen_height//2 )
        self.texture = pygame.transform.rotozoom( BAT_IMG, rot, 1/6 )
        self.dir=dir
        self.mask = pygame.mask.from_surface(self.texture)

    def render(self):
        screen.blit(
            self.texture,
            self.position - pygame.Vector2(self.texture.get_rect().size ) * 0.5
        )

        self.position += (2*self.dir, 0)

bat1 = Bat(0, 90, 1)
bat2 = Bat(screen_width, 0, -1)

def game():

    run = True
    while run:
        clock.tick(fps)

        draw_bg()
        bat1.render()
        bat2.render()

        overlap = bat1.mask.overlap( bat2.mask, [*map(int, bat1.position - bat2.position)] )
        print(overlap)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    game()
