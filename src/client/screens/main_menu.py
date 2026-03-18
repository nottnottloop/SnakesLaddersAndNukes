import pygame
from .. import load_assets as assets
from ..button import Button
from ..explosion import Explosion
from ..utils import *
from ..constants import *
from ...shared.game import Game

class MenuScreen(ScreenStateInterface):
    def __init__(self, window: pygame.surface.Surface, state: ClientState):
        self.window = window
        self.state = state
        self.explosion_easter_egg_counter = 0
        self.buttons = {
            "mute_button": Button(window, state, 'Mute', 600, 590, 100, 100, WHITE, WHITE, image=assets.UNMUTED),
            "start_game_button": Button(window, state, 'Start Game', 420, 450, 275, 110, BLACK, WHITE, sound=assets.click),
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
                explosion = Explosion(WIDTH/2, HEIGHT/2)
                self.state.explosion_group.add(explosion)

    def update(self, dt):
        pass

    def draw(self):
        draw_bg(self.window, self.state)
        self.window.blit(assets.TITLE3, (0, 0))
        self.buttons["start_game_button"].draw()
        self.buttons["mute_button"].draw()
        self.state.explosion_group.draw(self.window)
        self.state.explosion_group.update()

