import pygame
from ..shared.game import Game
from .constants import *

class ClientState():
    def __init__(self):
        self.game: Game = None
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
