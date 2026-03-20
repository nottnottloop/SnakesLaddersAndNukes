import pygame
from ..shared.constants import *
from . import load_assets as assets
from collections import namedtuple

MovableDrawData = namedtuple("MovableDrawData", ["regular_sprite", "deg_sprite", "offset"])

WIDTH = 750
HEIGHT = 750

CHANGE_STATE = pygame.USEREVENT + 1
FAILED_TO_CONNECT_TIMER = pygame.USEREVENT + 2
WINNER = pygame.USEREVENT + 2

SQUARE_SIZE = 51
BOARD_START_X = 117
BOARD_START_Y = 517

FONTS = {
    25: pygame.font.SysFont("consolas", 25),
    40: pygame.font.SysFont("consolas", 40),
    50: pygame.font.SysFont("consolas", 50),
    60: pygame.font.SysFont("consolas", 60),
    80: pygame.font.SysFont("consolas", 80),
    90: pygame.font.SysFont("consolas", 90),
    120: pygame.font.SysFont("consolas", 120),
}

DEG_NUKE_FONT = pygame.font.SysFont("impact", 120)

MOVABLE_DRAW_DATA = {
    "snake1": MovableDrawData(assets.SNAKE1, assets.SNAKE1DEG, Position(-19, 33)),
    "snake2": MovableDrawData(assets.SNAKE2, assets.SNAKE2DEG, Position(-65, 23)),
    "snake3": MovableDrawData(assets.SNAKE3, assets.SNAKE3DEG, Position(10, 20)),
    "snake4": MovableDrawData(assets.SNAKE4, assets.SNAKE4DEG, Position(0, 28)),
    "ladder1": MovableDrawData(assets.LADDER1, assets.LADDER1, Position(15, -148)),
    "ladder2": MovableDrawData(assets.LADDER2, assets.LADDER2DEG, Position(15, -79)),
    "ladder3": MovableDrawData(assets.LADDER3, assets.LADDER3, Position(-41, -67)),
    "ladder4": MovableDrawData(assets.LADDER4, assets.LADDER4DEG, Position(-17, -240)),
}
