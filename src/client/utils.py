import pygame
from abc import ABC, abstractmethod

from ..shared import game_pb2
from .constants import *
from src.shared.constants import *
from .networking import Network
from ..shared.game_pb2 import Player, Game

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
        self.player_id: int = None
        self.server_events: list[str] = []
        self.server_events_counter: int = 0

        self.sound_enabled = True

        self.shake_amount = 0
        self.shake_direction = True
    
    def get_new_events(self):
        new_events = [e.event for e in self.game.events if e.id > self.server_events_counter]
        self.server_events_counter = self.game.events[-1].id if self.game.events else 0
        self.server_events = new_events

    def play_sound(self, sound):
        if self.sound_enabled:
            sound.play()
    
    def play_music(self, music: pygame.mixer_music):
        if self.sound_enabled:
            pygame.mixer.music.load(music)
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(-1)
    
    def jukebox(self, music: str):
        if music == "papers_please":
            self.play_music(assets.music_papers_please)
        elif music == "but_nobody_came":
            self.play_music(assets.music_but_nobody_came)
        elif music == "genocide":
            self.play_music(assets.music_genocide)

def blit_centered_text(window, text, y_offset=0):
    window.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 - text.get_height() / 2 + y_offset))

def draw_bg(window, state: ClientState):
    if state.game == None or state.game.deg_color == 0:
        window.fill(WHITE.color)
    else:
        if state.game.deg_color == 1:
            window.fill((192, 192, 192))
        elif state.game.deg_color == 2:
            window.fill((128, 128, 128))
        elif state.game.deg_color == 3:
            window.fill((64, 64, 64))
        elif state.game.deg_color == 4:
            window.fill((102, 0, 0))
        elif state.game.deg_color >= 5:
            window.fill((0, 0, 0))
