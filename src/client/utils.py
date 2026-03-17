import pygame
from .constants import *

class ClientState():
    def __init__(self):
        self.music_degraded = 0
        self.sound_enabled = True

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
