import pygame

WIDTH = 750
HEIGHT = 750

CHANGE_STATE = pygame.USEREVENT + 1
FAILED_TO_CONNECT_TIMER = pygame.USEREVENT + 2

SQUARE_SIZE = 51
BOARD_START_X = 117
BOARD_START_Y = 517

FONTS = {
    25: pygame.font.SysFont("consolas", 25),
    40: pygame.font.SysFont("consolas", 40),
    50: pygame.font.SysFont("consolas", 50),
    60: pygame.font.SysFont("consolas", 60),
    80: pygame.font.SysFont("consolas", 80),
    120: pygame.font.SysFont("consolas", 120),
}

DEG_NUKE_FONT = pygame.font.SysFont("impact", 120)
