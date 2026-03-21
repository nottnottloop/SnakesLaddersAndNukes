import pygame
from ..shared.constants import * 
from .utils import ClientState
from .load_assets import *

class Button:
    def __init__(self, window, state: ClientState, text, x, y, width, height, color=WHITE.color, text_color=BLACK.color, enabled=False, border_radius=-1, border_width=0, border_color=BLACK.color, sound=sound_click, image=None, data=None, callback=lambda *args, **kwargs: None):
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
        self.border_width = border_width
        self.border_color = border_color
        self.sound = sound
        self.image = image
        self.data = data
        self.callback = callback

        if not self.data:
            self.data = self.text

    def draw(self):
        if not self.enabled:
            return
        if self.image:
            self.window.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(self.window, self.color, (self.x, self.y, self.width, self.height), border_radius=self.border_radius)
            if self.border_width:
                pygame.draw.rect(self.window, self.border_color, (self.x, self.y, self.width, self.height), width=3, border_radius=self.border_radius)
            font = pygame.font.SysFont("consolas", 40)
            text = font.render(self.text, True, self.text_color)
            self.window.blit(text, (self.x + round(self.width / 2) - round(text.get_width() / 2),
                            (self.y + round(self.height / 2) - round(text.get_height() / 2))))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height and self.enabled:
            self.callback()
            self.play_button_sound()
            return True
        else:
            return False
        
    def play_button_sound(self):
        if self.sound and self.state.sound_enabled:
            self.sound.play()
    
    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def toggle(self):
        self.enabled = not self.enabled
