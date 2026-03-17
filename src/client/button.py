import pygame
from .constants import * 
from .utils import ClientState

class Button:
    def __init__(self, window, client_state: ClientState, text, x, y, width, height, color, text_color=BLACK, enabled=False, border_radius=-1, click_sound=True, sound=None, callback=lambda *args, **kwargs: None):
        self.window = window
        self.client_state = client_state
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text_color = text_color
        self.enabled = enabled
        self.border_radius = border_radius
        self.click_sound = click_sound
        self.sound = sound
        self.callback = callback

    def draw(self):
        pygame.draw.rect(self.window, self.color, (self.x, self.y, self.width, self.height), border_radius=self.border_radius)
        font = pygame.font.SysFont("consolas", 40)
        text = font.render(self.text, True, self.text_color)
        self.window.blit(text, (self.x + round(self.width / 2) - round(text.get_width() / 2),
                        (self.y + round(self.height / 2) - round(text.get_height() / 2))))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height and self.enabled:
            if self.client_state.sound_enabled:
                self.sound.play()
            return True
        else:
            return False

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False
