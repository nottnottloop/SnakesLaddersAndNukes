import pygame
from .constants import * 
from .utils import ClientState

class Button:
    def __init__(self, window, state: ClientState, text, x, y, width, height, color, text_color=BLACK, enabled=True, border_radius=-1, sound=None, image=None, callback=lambda *args, **kwargs: None):
        self.window = window
        self.state = state
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text_color = text_color
        self.enabled = enabled
        self.border_radius = border_radius
        self.sound = sound
        self.image = image
        self.callback = callback

    def draw(self):
        if self.image:
            self.window.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(self.window, self.color, (self.x, self.y, self.width, self.height), border_radius=self.border_radius)
            font = pygame.font.SysFont("consolas", 40)
            text = font.render(self.text, True, self.text_color)
            self.window.blit(text, (self.x + round(self.width / 2) - round(text.get_width() / 2),
                            (self.y + round(self.height / 2) - round(text.get_height() / 2))))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height and self.enabled:
            self.callback()
            if self.sound and self.state.sound_enabled:
                self.sound.play()
            return True
        else:
            return False
