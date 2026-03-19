from enum import Enum
from collections import namedtuple
from dataclasses import dataclass

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

def generate_board_number_to_position():
    number_to_position = {}
    size = 10
    for row in range(size):
        y = row
        row_start = row * size + 1
        row_end = (row + 1) * size + 1
        numbers = range(row_start, row_end)
        if row % 2 == 1:
            numbers = reversed(numbers)
        for x, number in enumerate(numbers):
            number_to_position[number] = Position(x, y)
    
    return number_to_position

BOARD_NUMBER_TO_POSITION = generate_board_number_to_position()
POSITION_TO_BOARD_NUMBER = {v: k for k, v in BOARD_NUMBER_TO_POSITION.items()}

class DEG_MAX(Enum):
    DEG_BOARD = 4
    DEG_COLOR = 5
    DEG_PIECES = 1
    DEG_DICE = 1
    DEG_NUKE_TEXT = 1
    DEG_SNAKES_AND_LADDERS = 1
    DEG_PIECE_SHAKE = 1
