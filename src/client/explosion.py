import pygame
from . import load_assets as assets
from .constants import *

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = assets.EXPLOSION_IMAGES
        self.index = 0
        self.image = self.images[self.index]
        self.rect = pygame.Rect(0, 0, 950, 950)
        self.rect.center = [WIDTH/2, HEIGHT/2]
        self.counter = 0

    def update(self):
        explosion_speed = 15
        #update explosion animation
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        #if the animation is complete, reset animation index
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()
