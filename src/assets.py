import pygame
from pathlib import Path

pygame.init()

base_dir = Path("assets")
img_dir = base_dir / "img"
audio_dir = base_dir / "audio"

def load(path):
    return pygame.image.load(path)

ui_dir = img_dir / "ui"
board_dir = img_dir / "board"
pieces_dir = img_dir / "pieces"
dice_dir = img_dir / "dice"
ladders_dir = img_dir / "ladders"
snakes_dir = img_dir / "snakes"
explosion_dir = img_dir / "explosion"

# ui
ICON = load(ui_dir / "icon.png")
TITLE1 = load(ui_dir / "title1.png")
TITLE2 = load(ui_dir / "title2.png")
TITLE3 = load(ui_dir / "title3.png")

UNMUTED = load(ui_dir / "unmuted.png")
UNMUTED = pygame.transform.scale(UNMUTED, (70, 70))
MUTED = load(ui_dir / "muted.png")
MUTED = pygame.transform.scale(MUTED, (70, 70))

NUCLEARICON = load(ui_dir / "nukeinactive.png")
NUCLEARICON = pygame.transform.scale(NUCLEARICON, (70, 70))
NUCLEARICONTRANSPARENT = load(ui_dir / "nukeactive.png")
NUCLEARICONTRANSPARENT = pygame.transform.scale(NUCLEARICONTRANSPARENT, (70, 70))

# board
BOARD1 = load(board_dir / "board1.png")
BOARD1 = pygame.transform.scale(BOARD1, (575, 575))
BOARD2 = load(board_dir / "board2.png")
BOARD2 = pygame.transform.scale(BOARD2, (575, 575))
BOARD3 = load(board_dir / "board3.png")
BOARD3 = pygame.transform.scale(BOARD3, (575, 575))
BOARD4 = load(board_dir / "board4.png")
BOARD4 = pygame.transform.scale(BOARD4, (575, 575))
BOARD5 = load(board_dir / "board5.png")
BOARD5 = pygame.transform.scale(BOARD5, (575, 575))

BOARD = (BOARD1, BOARD2, BOARD3, BOARD4, BOARD5)

# pieces
NUCLEARBOMB = load(pieces_dir / "nuclearbomb.png")
NUCLEARBOMB = pygame.transform.scale(NUCLEARBOMB, (37, 38))

PIECERED = load(pieces_dir / "piecered.png")
PIECERED = pygame.transform.scale(PIECERED, (40, 40))
BIGGERPIECERED = pygame.transform.scale(PIECERED, (80, 80))
PIECEGREEN = load(pieces_dir / "piecegreen.png")
PIECEGREEN = pygame.transform.scale(PIECEGREEN, (40, 40))
BIGGERPIECEGREEN = pygame.transform.scale(PIECEGREEN, (80, 80))
PIECEBLUE = load(pieces_dir / "pieceblue.png")
PIECEBLUE  = pygame.transform.scale(PIECEBLUE, (40, 40))
BIGGERPIECEBLUE = pygame.transform.scale(PIECEBLUE, (80, 80))
PIECEYELLOW = load(pieces_dir / "pieceyellow.png")
PIECEYELLOW  = pygame.transform.scale(PIECEYELLOW, (40, 40))
BIGGERPIECEYELLOW = pygame.transform.scale(PIECEYELLOW, (80, 80))

PIECES = {"Red": PIECERED, "Green": PIECEGREEN, "Blue": PIECEBLUE, "Yellow": PIECEYELLOW}
BIGGERPIECES = {"Red": BIGGERPIECERED, "Green": BIGGERPIECEGREEN, "Blue": BIGGERPIECEBLUE, "Yellow": BIGGERPIECEYELLOW}

PIECEBLUEDEG = load(pieces_dir / "piecebluedeg.png")
PIECEBLUEDEG = pygame.transform.scale(PIECEBLUEDEG, (40, 40))
BIGGERPIECEBLUEDEG = pygame.transform.scale(PIECEBLUEDEG, (80, 80))
PIECEGREENDEG = load(pieces_dir / "piecegreendeg.png")
PIECEGREENDEG = pygame.transform.scale(PIECEGREENDEG, (40, 40))
BIGGERPIECEGREENDEG = pygame.transform.scale(PIECEGREENDEG, (80, 80))
PIECEREDDEG = load(pieces_dir / "piecereddeg.png")
PIECEREDDEG = pygame.transform.scale(PIECEREDDEG, (40, 40))
BIGGERPIECEREDDEG = pygame.transform.scale(PIECEREDDEG, (80, 80))
PIECEYELLOWDEG = load(pieces_dir / "pieceyellowdeg.png")
PIECEYELLOWDEG = pygame.transform.scale(PIECEYELLOWDEG, (40, 40))
BIGGERPIECEYELLOWDEG = pygame.transform.scale(PIECEYELLOWDEG, (80, 80))

PIECESDEG = {"Red": PIECEREDDEG, "Green": PIECEGREENDEG, "Blue": PIECEBLUEDEG, "Yellow": PIECEYELLOWDEG}
BIGGERPIECESDEG = {"Red": BIGGERPIECEREDDEG, "Green": BIGGERPIECEGREENDEG, "Blue": BIGGERPIECEBLUEDEG, "Yellow": BIGGERPIECEYELLOWDEG}

# dice
DICE1 = load(dice_dir / "dice1.png")
DICE1 = pygame.transform.scale(DICE1, (100, 100))
DICE2 = load(dice_dir / "dice2.png")
DICE2 = pygame.transform.scale(DICE2, (100, 100))
DICE3 = load(dice_dir / "dice3.png")
DICE3 = pygame.transform.scale(DICE3, (100, 100))
DICE4 = load(dice_dir / "dice4.png")
DICE4 = pygame.transform.scale(DICE4, (100, 100))
DICE5 = load(dice_dir / "dice5.png")
DICE5 = pygame.transform.scale(DICE5, (100, 100))
DICE6 = load(dice_dir / "dice6.png")
DICE6 = pygame.transform.scale(DICE6, (100, 100))

DICE = (None, DICE1, DICE2, DICE3, DICE4, DICE5, DICE6)

DICE1DEG = load(dice_dir / "dice1deg.png")
DICE1DEG = pygame.transform.scale(DICE1DEG, (100, 100))
DICE2DEG = load(dice_dir / "dice2deg.png")
DICE2DEG = pygame.transform.scale(DICE2DEG, (100, 100))
DICE3DEG = load(dice_dir / "dice3deg.png")
DICE3DEG = pygame.transform.scale(DICE3DEG, (100, 100))
DICE4DEG = load(dice_dir / "dice4deg.png")
DICE4DEG = pygame.transform.scale(DICE4DEG, (100, 100))
DICE5DEG = load(dice_dir / "dice5deg.png")
DICE5DEG = pygame.transform.scale(DICE5DEG, (100, 100))
DICE6DEG = load(dice_dir / "dice6deg.png")
DICE6DEG = pygame.transform.scale(DICE6DEG, (100, 100))

DICEDEG = (None, DICE1DEG, DICE2DEG, DICE3DEG, DICE4DEG, DICE5DEG, DICE6DEG)

# ladders
LADDER1 = load(ladders_dir / "ladder1.png")
LADDER2 = load(ladders_dir / "ladder2.png")
LADDER3 = load(ladders_dir / "ladder3.png")
LADDER4 = load(ladders_dir / "ladder4.png")

LADDER1 = pygame.transform.scale(LADDER1, (48, 230))
LADDER1 = pygame.transform.rotate(LADDER1, 225)
LADDER1 = pygame.transform.flip(LADDER1, True, False)
LADDER2 = pygame.transform.scale(LADDER2, (30, 108))
LADDER3 = pygame.transform.scale(LADDER3, (90, 96))
LADDER4 = pygame.transform.scale(LADDER4, (92, 274))

LADDERS = (LADDER1, LADDER2, LADDER3, LADDER4)

LADDER2DEG = load(ladders_dir / "ladder2deg.png")
LADDER4DEG = load(ladders_dir / "ladder4deg.png")

LADDER2DEG = pygame.transform.scale(LADDER2DEG, (30, 108))
LADDER4DEG = pygame.transform.scale(LADDER4DEG, (92, 274))

LADDERSDEG = (LADDER1, LADDER2DEG, LADDER3, LADDER4DEG)

# snakes
SNAKE1 = load(snakes_dir / "snake1.png")
SNAKE2 = load(snakes_dir / "snake2.png")
SNAKE3 = load(snakes_dir / "snake3.png")
SNAKE4 = load(snakes_dir / "snake4.png")

SNAKE1 = pygame.transform.scale(SNAKE1, (60, 50))
SNAKE2 = pygame.transform.scale(SNAKE2, (115, 120))
SNAKE3 = pygame.transform.scale(SNAKE3, (52, 320))
SNAKE4 = pygame.transform.scale(SNAKE4, (192, 257))

SNAKES = (SNAKE1, SNAKE2, SNAKE3, SNAKE4)

SNAKE1DEG = load(snakes_dir / "snake1deg.png")
SNAKE2DEG = load(snakes_dir / "snake2deg.png")
SNAKE3DEG = load(snakes_dir / "snake3deg.png")
SNAKE4DEG = load(snakes_dir / "snake4deg.png")

SNAKE1DEG = pygame.transform.scale(SNAKE1DEG, (60, 50))
SNAKE2DEG = pygame.transform.scale(SNAKE2DEG, (115, 120))
SNAKE3DEG = pygame.transform.scale(SNAKE3DEG, (52, 320))
SNAKE4DEG = pygame.transform.scale(SNAKE4DEG, (192, 257))

SNAKESDEG = (SNAKE1DEG, SNAKE2DEG, SNAKE3DEG, SNAKE4DEG)

EXPLOSION_IMAGES = []
for i in range(12):
    img = pygame.image.load(explosion_dir / f'explosion{i}.png')
    img = pygame.transform.scale(img, (950, 950))
    EXPLOSION_IMAGES.append(img)

# audio
papers_please = audio_dir / "papers_please.mp3"
but_nobody_came = audio_dir / "but_nobody_came.mp3"
genocide = audio_dir / "genocide.mp3"

nuke_get_sounds = []
for i in range(1, 6):
    sound = pygame.mixer.Sound(audio_dir / "nuke_get" / f"nuke_get_{i}.mp3")
    sound.set_volume(0.15)
    nuke_get_sounds.append(sound)

click = pygame.mixer.Sound(audio_dir / "click.mp3")
dice = pygame.mixer.Sound(audio_dir / "dice.mp3")
explosion = pygame.mixer.Sound(audio_dir / "explosion.mp3")
explosion.set_volume(0.1)
nukewin = pygame.mixer.Sound(audio_dir / "nukewin.mp3")
nukewin.set_volume(1)
pacifistwin = pygame.mixer.Sound(audio_dir / "pacifistwin.mp3")
pacifistwin.set_volume(0.1)
ladder = pygame.mixer.Sound(audio_dir / "ladder.mp3")
ladder.set_volume(0.2)
snake = pygame.mixer.Sound(audio_dir / "snake.mp3")
snake.set_volume(0.2)
