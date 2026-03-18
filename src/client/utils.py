import pygame
from abc import ABC, abstractmethod

from ..shared.game import Game
from .constants import *
from .networking import Network

class ScreenStateInterface(ABC):
    @abstractmethod
    def handle_event(self, event: pygame.event.Event):
        """Process input events (keyboard, mouse, etc.)"""
        pass

    @abstractmethod
    def update(self, dt: float):
        """Update game logic. dt is delta time in milliseconds."""
        pass

    @abstractmethod
    def draw(self):
        """Draw state elements to the screen."""
        pass

class ClientState():
    def __init__(self):
        self.game: Game = None
        self.screen_state: ScreenStateInterface
        self.clock = pygame.time.Clock()
        self.network = Network()
        self.connected = False
        self.player_id = None

        self.music_degraded = 0
        self.sound_enabled = True

        self.players_moving = []
        self.player_movement_started = []
        self.player_position_cache = []

        self.nuke_cache = []
        self.nukes_cached = False
        self.nukes_acquired = 0

        self.ticks_passed = 0
        self.distance_x, self.distance_y = 0, 0

        self.shake_amount = 0
        self.shake_direction = True
        self.explosion_group = pygame.sprite.Group()

        for _ in range(5):
            self.players_moving.append(False)
            self.player_movement_started.append(False)
            self.player_position_cache.append([0, 0])

def blit_centered_text(window, text, y_offset=0):
    window.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 - text.get_height() / 2 + y_offset))

def parse_color(color):
    if color == "Red":
        return RED
    if color == "Green":
        return GREEN
    if color == "Blue":
        return BLUE
    if color == "Yellow":
        return YELLOW

def draw_bg(window, state):
    if state.game == None or state.game.discoloration == 0:
        window.fill(WHITE)
    if state.game != None:
        if state.game.discoloration == 1:
            window.fill((192, 192, 192))
        elif state.game.discoloration == 2:
            window.fill((128, 128, 128))
        elif state.game.discoloration == 3:
            window.fill((64, 64, 64))
        elif state.game.discoloration == 4:
            window.fill((102, 0, 0))
        elif state.game.discoloration >= 5:
            window.fill((0, 0, 0))
