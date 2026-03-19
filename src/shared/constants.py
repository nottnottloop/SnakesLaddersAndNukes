from enum import Enum
from collections import namedtuple

Color = namedtuple("Color", ["text", "color"])
Position = namedtuple("Position", ["x", "y"])

BLACK = Color("Black", (0, 0, 0))
WHITE = Color("White", (255, 255, 255))
RED = Color("Red", (255, 0, 0))
BLUE = Color("Blue", (0, 0, 255))
GREEN = Color("Green", (0, 255, 0))
YELLOW = Color("Yellow", (252, 226, 5))

COLOR_MAP = {
    "Red": RED,
    "Blue": BLUE,
    "Green": GREEN,
    "Yellow": YELLOW,
}

class DEG_MAX(Enum):
    DEG_BOARD = 4
    DEG_COLOR = 5
    DEG_PIECES = 1
    DEG_DICE = 1
    DEG_NUKE_TEXT = 1
    DEG_SNAKES_AND_LADDERS = 1
    DEG_PIECE_SHAKE = 1
