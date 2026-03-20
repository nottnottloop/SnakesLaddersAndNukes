import pygame
from .. import load_assets as assets
from ..button import Button
from ..explosion import Explosion
from ..utils import *
from src.shared.constants import *

class MenuScreen(ScreenStateInterface):
    def __init__(self, window: pygame.surface.Surface, state: ClientState):
        self.window = window
        self.state = state
        self.explosion_easter_egg_counter = 0
        self.explosion_group = pygame.sprite.Group()
        self.buttons: dict[str, Button] = {
            "mute_button": Button(window, state, 'Mute', 600, 590, 100, 100, WHITE.color, WHITE.color, image=assets.UNMUTED, enabled=True),
            "start_game_button": Button(window, state, 'Start Game', 420, 450, 275, 110, BLACK.color, WHITE.color, enabled=True),
        }

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if self.buttons["start_game_button"].click(pos):
                pygame.event.post(pygame.event.Event(CHANGE_STATE, {"state": "player_select"}))
            if self.buttons["mute_button"].click(pos):
                self.state.sound_enabled = not self.state.sound_enabled
                if self.state.sound_enabled:
                    assets.click.play()
                    self.buttons["mute_button"].image = assets.UNMUTED
                else:
                    self.buttons["mute_button"].image = assets.MUTED
            self.explosion_easter_egg_counter += 1
            if self.explosion_easter_egg_counter > 10:
                self.explosion_group.add(Explosion())

    def update(self, dt):
        self.explosion_group.update()

    def draw(self):
        draw_bg(self.window, self.state)
        self.window.blit(assets.TITLE3, (0, 0))
        self.buttons["start_game_button"].draw()
        self.buttons["mute_button"].draw()
        self.explosion_group.draw(self.window)

