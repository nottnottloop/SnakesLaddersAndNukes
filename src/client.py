import pygame
import random
import sys
import network
import load_assets as a
import debug
import gc
# this import statement is actually needed if you want to run turn the client into an exe ;)
import game
# game = game.Game()
# color constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
# pure yellow hurts everyone's eyes
YELLOW = (252, 226, 5)

pygame.font.init()
pygame.display.set_icon(a.ICON)

WIDTH = 750
HEIGHT = 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snakes, Ladders and Nukes")

music_degraded = 0

sound_enabled = True

def blit_centered_text(text, y_offset=0):
    WIN.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 - text.get_height() / 2 + y_offset))

WIN.fill(WHITE)
font = pygame.font.SysFont("consolas", 60)
text = font.render("LOADING", True, BLACK)
blit_centered_text(text)
pygame.display.update()


n = network.Network()

clock = pygame.time.Clock()


SQUARE_SIZE = 51
BOARD_START_X = 117
BOARD_START_Y = 517

def init_vars():
    global players_moving, player_movement_started, player_position_cache, nuke_cache, ticks_passed, nukes_cached, distance_x, distance_y, shake_amount, shake_direction
    players_moving = []
    for i in range(5):
        players_moving.append(False)

    player_movement_started = []
    for i in range(5):
        player_movement_started.append(False)

    player_position_cache = []
    for i in range(5):
        player_position_cache.append([0, 0])

    nuke_cache = []
    nukes_cached = False

    ticks_passed = 0
    distance_x, distance_y = 0, 0

    shake_amount = 0
    shake_direction = True

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = a.EXPLOSION_IMAGES
        self.index = 0
        self.image = self.images[self.index]
        self.rect = pygame.Rect(0, 0, 950, 950)
        self.rect.center = [WIDTH/2, HEIGHT/2]
        self.counter = 0

    def update(self):
        explosion_speed = 15
        #update explosion animation
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        #if the animation is complete, reset animation index
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()

explosion_group = pygame.sprite.Group()

class Button:
    def __init__(self, text, x, y, width, height, color, text_color=BLACK, enabled=False, border_radius=-1, click_sound=True, sound=None, mute_button=False, unmute_button=False):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text_color = text_color
        self.enabled = enabled
        self.border_radius = border_radius
        self.click_sound = click_sound
        self.sound = sound
        self.mute_button = mute_button
        self.unmute_button = unmute_button


    def draw(self):
        pygame.draw.rect(WIN, self.color, (self.x, self.y, self.width, self.height), border_radius=self.border_radius)
        font = pygame.font.SysFont("consolas", 40)
        text = font.render(self.text, True, self.text_color)
        WIN.blit(text, (self.x + round(self.width / 2) - round(text.get_width() / 2),
                        (self.y + round(self.height / 2) - round(text.get_height() / 2))))

    def click(self, pos):
        global sound_enabled
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height and self.enabled:
            if self.unmute_button or self.mute_button and not sound_enabled:
                self.sound.play()
            if self.click_sound and sound_enabled and not self.mute_button:
                self.sound.play()
            return True
        else:
            return False

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

def parse_color(color):
    if color == "Red":
        return RED
    if color == "Green":
        return GREEN
    if color == "Blue":
        return BLUE
    if color == "Yellow":
        return YELLOW

SELECT_COLOR_BUTTONS = (
    Button('Red', 375, 175, 200, 200, RED, RED, sound=a.click),
    Button('Green', 375, 375, 200, 200, GREEN, GREEN, sound=a.click),
    Button('Blue', 175, 175, 200, 200, BLUE, BLUE, sound=a.click),
    Button('Yellow', 175, 375, 200, 200, YELLOW, YELLOW, sound=a.click),
)

MUTE_BUTTON_LOCATION = (600, 590)
MUTE_BUTTON = (Button('Mute', MUTE_BUTTON_LOCATION[0], MUTE_BUTTON_LOCATION[1], 100, 100, WHITE, WHITE, sound=a.click, mute_button=True),)
UNMUTE_BUTTON = (Button('Unmute', MUTE_BUTTON_LOCATION[0], MUTE_BUTTON_LOCATION[1], 100, 100, WHITE, WHITE, sound=a.click, unmute_button=True),)

START_GAME_BUTTON = (Button('Start Game', 420, 450, 275, 110, BLACK, WHITE, sound=a.click),)
START_GAME_BUTTON = (Button('Start Game', 420, 450, 275, 110, BLACK, WHITE, sound=a.click),)

READY_UP_BUTTON = (Button('Ready Up', 225, 450, 300, 150, BLACK, WHITE, sound=a.click),)

DICE_BUTTON = (Button('roll', 550, 625, 100, 100, BLACK, WHITE, border_radius=100, sound=a.dice),)

NUKE_BUTTON = (Button('NUKE', 295, 615, 130, 130, RED, WHITE, border_radius=50, sound=a.click),)

BUTTONS = SELECT_COLOR_BUTTONS + READY_UP_BUTTON + DICE_BUTTON + NUKE_BUTTON

NUKE_ICON_LOCATION = (15, 635)
MOVE_TURN_ICON_LOCATION = (5, 5)


def check_and_display_waiting_for_players(game, p):
    # checks if color selection has been made. if it has been made, display waiting for players
    if not game.started and game.players[p][1] != None:
        font = pygame.font.SysFont("consolas", 25)
        text = font.render("Lobby: " + str(game.id), True, BLACK)
        WIN.blit(text, (10, 10))
        text = font.render("Player: " + str(p), True, BLACK)
        WIN.blit(text, (10, 40))
        text = font.render(game.players[p][1], True, parse_color(game.players[p][1]))
        WIN.blit(text, (10, 70))
        font = pygame.font.SysFont("consolas", 40)
        text = font.render("Players in Lobby: (" + str(game.num_of_players) + "/4)", True, BLACK)
        blit_centered_text(text, -220)
        if game.num_of_players < 4:
            font = pygame.font.SysFont("consolas", 50)
            text = font.render("Waiting for Players...", True, BLUE)
            blit_centered_text(text, -50)
        if game.num_of_players >= 2:
            if game.players[p][3] == True:
                READY_UP_BUTTON[0].disable()
            else:
                READY_UP_BUTTON[0].draw()
                READY_UP_BUTTON[0].enable()


def check_and_ask_for_color(game, p):
    if game.players[p][1] == None:
        font = pygame.font.SysFont("consolas", 50)
        text = font.render("Choose your colour!", True, BLACK)
        blit_centered_text(text, -300)
        for btn in SELECT_COLOR_BUTTONS:
            if btn.text in game.blocked_colors:
                btn.disable()
            else:
                btn.draw()
                btn.enable()
    else:
        for btn in SELECT_COLOR_BUTTONS:
            btn.disable()


    # nudge each of the player tokens to prevent overlapping
def calculate_offset_nudge(player):
    return (player - 1) * 5

def draw_stationary_pieces(player):
    # if shake_direction true, move right
    global shake_amount, shake_direction
    x_offset, y_offset = game.players[player][0][0], game.players[player][0][1]
    offset_nudge = calculate_offset_nudge(player)
    if game.piece_shake == 1:
        if shake_direction:
            shake_amount += 1
            if shake_amount == 5:
                shake_direction = not shake_direction
        if not shake_direction:
            shake_amount -= 1
            if shake_amount == -5:
                shake_direction = not shake_direction
    if game.pieces_degraded == 0:
        WIN.blit(a.PIECES[game.players[player][1]],
                 (BOARD_START_X + x_offset * SQUARE_SIZE + offset_nudge + shake_amount,
                  BOARD_START_Y - y_offset * SQUARE_SIZE + offset_nudge))
    else:
        WIN.blit(a.PIECESDEG[game.players[player][1]],
                 (BOARD_START_X + x_offset * SQUARE_SIZE + offset_nudge + shake_amount,
                  BOARD_START_Y - y_offset * SQUARE_SIZE + offset_nudge))

def draw_game_pieces(game, p):
    global player_movement_started
    for player in range(1, 5):
        if game.players[player][3] == True:
            draw_stationary_pieces(player)
            if players_moving[player] and not player_movement_started[player] and not game.nuke_used:
                play_movement_animation(player, calculate_offset_nudge(player), p, game)


def play_movement_animation(player, offset_nudge, p, game):
    global players_moving, player_position_cache, player_movement_started, ticks_passed, distance_x, distance_y
    # destination is game.players[player][0][0]
    # old position is player_position_cache
    ticks_passed = 0
    if game.player_travelled_on_movable[player]:
        # print("travelled on movable")
        # print(game.players_previous_space[player])
        loop_completed = False
        old_x, old_y = player_position_cache[player][0], player_position_cache[player][1]
        new_x, new_y = game.players_previous_space[player][0], game.players_previous_space[player][1]
        distance_x, distance_y = new_x - old_x, new_y - old_y
    else:
        # print("didn't")
        # print(game.players_previous_space[player])
        loop_completed = True
        old_x, old_y = player_position_cache[player][0], player_position_cache[player][1]
        new_x, new_y = game.players[player][0][0], game.players[player][0][1]
        distance_x, distance_y = new_x - old_x, new_y - old_y
    while players_moving[player]:
        player_movement_started[player] = True
        ticks_passed += 1
        draw_bg(game)
        draw_board(game)
        draw_dice(p)
        draw_nuke_buttons(p)
        if not debug.disable_move_turns:
            draw_move_icon()
        if not debug.disable_snakes_and_ladders:
            draw_snakes_and_ladders()
        for hypothetical_stationary_player in range(1, 5):
            if game.players[hypothetical_stationary_player][1] != None:
                if hypothetical_stationary_player != player:
                    draw_stationary_pieces(hypothetical_stationary_player)
        draw_nukes()
        if game.pieces_degraded == 0:
            WIN.blit(a.PIECES[game.players[player][1]],
                     (BOARD_START_X + old_x * SQUARE_SIZE + 0.85 * ticks_passed * distance_x + offset_nudge,
                      BOARD_START_Y - old_y * SQUARE_SIZE - 0.85 * ticks_passed * distance_y + offset_nudge))
        else:
            WIN.blit(a.PIECESDEG[game.players[player][1]],
                     (BOARD_START_X + old_x * SQUARE_SIZE + 0.85 * ticks_passed * distance_x + offset_nudge,
                      BOARD_START_Y - old_y * SQUARE_SIZE - 0.85 * ticks_passed * distance_y + offset_nudge))
        explosion_group.draw(WIN)
        explosion_group.update()
        pygame.display.update()
        if not loop_completed and ticks_passed == 60:
            # for nuke in (range(len(nuke_cache))):
            #     if nuke_cache[nuke] == game.players_previous_space[player]:
            #         nuke_cache[nuke] = [-100, -100]
            cache_nukes(p, game)
            # game = n.send("get")
            old_x, old_y = game.players_previous_space[player][0], game.players_previous_space[player][1]
            new_x, new_y = game.players[player][0][0], game.players[player][0][1]
            distance_x, distance_y = new_x - old_x, new_y - old_y
            ticks_passed = 0
            loop_completed = True
        if ticks_passed == 60 and loop_completed:
            players_moving[player] = False

def draw_snakes_and_ladders():
    if game.snakes_and_ladders_degraded == 0:
        for snake in range(3, -1, -1):
            # y_offset, x_offset = calculate_offset(game.snakes[snake][0])
            # if game.snakes[snake][3] == True:
            #     x_offset += x_offset
            if snake == 0:
                WIN.blit(a.SNAKE1,
                         (117 + (game.snakes[snake][0][0] * 51) - 19, 517 - (game.snakes[snake][0][1] * 51) + 33))
            if snake == 1:
                WIN.blit(a.SNAKE2,
                         (117 + (game.snakes[snake][0][0] * 51) - 65, 517 - (game.snakes[snake][0][1] * 51) + 23))
            if snake == 2:
                WIN.blit(a.SNAKE3,
                         (117 + (game.snakes[snake][0][0] * 51) + 10, 517 - (game.snakes[snake][0][1] * 51) + 20))
            if snake == 3:
                WIN.blit(a.SNAKE4,
                         (117 + (game.snakes[snake][0][0] * 51) , 517 - (game.snakes[snake][0][1] * 51) + 28))
        for ladder in range (3, -1, -1):
            if ladder == 0:
                WIN.blit(a.LADDER1,
                         (117 + (game.ladders[ladder][0][0] * 51) + 15, 517 - (game.ladders[ladder][0][1] * 51) - 148))
            if ladder == 1:
                WIN.blit(a.LADDER2,
                         (117 + (game.ladders[ladder][0][0] * 51) + 15, 517 - (game.ladders[ladder][0][1] * 51) - 79))
            if ladder == 2:
                WIN.blit(a.LADDER3,
                         (117 + (game.ladders[ladder][0][0] * 51) - 41, 517 - (game.ladders[ladder][0][1] * 51) - 67))
            if ladder == 3:
                WIN.blit(a.LADDER4,
                         (117 + (game.ladders[ladder][0][0] * 51) - 17, 517 - (game.ladders[ladder][0][1] * 51) - 240))
    else:
        for snake in range(3, -1, -1):
            if snake == 0:
                WIN.blit(a.SNAKE1DEG,
                         (117 + (game.snakes[snake][0][0] * 51) - 19, 517 - (game.snakes[snake][0][1] * 51) + 33))
            if snake == 1:
                WIN.blit(a.SNAKE2DEG,
                         (117 + (game.snakes[snake][0][0] * 51) - 65, 517 - (game.snakes[snake][0][1] * 51) + 23))
            if snake == 2:
                WIN.blit(a.SNAKE3DEG,
                         (117 + (game.snakes[snake][0][0] * 51) + 10, 517 - (game.snakes[snake][0][1] * 51) + 20))
            if snake == 3:
                WIN.blit(a.SNAKE4DEG,
                         (117 + (game.snakes[snake][0][0] * 51) , 517 - (game.snakes[snake][0][1] * 51) + 28))
        for ladder in range (3, -1, -1):
            if ladder == 0:
                WIN.blit(a.LADDER1,
                         (117 + (game.ladders[ladder][0][0] * 51) + 15, 517 - (game.ladders[ladder][0][1] * 51) - 148))
            if ladder == 1:
                WIN.blit(a.LADDER2DEG,
                         (117 + (game.ladders[ladder][0][0] * 51) + 15, 517 - (game.ladders[ladder][0][1] * 51) - 79))
            if ladder == 2:
                WIN.blit(a.LADDER3,
                         (117 + (game.ladders[ladder][0][0] * 51) - 41, 517 - (game.ladders[ladder][0][1] * 51) - 67))
            if ladder == 3:
                WIN.blit(a.LADDER4DEG,
                         (117 + (game.ladders[ladder][0][0] * 51) - 17, 517 - (game.ladders[ladder][0][1] * 51) - 240))

def draw_nukes():
    # WIN.blit(a.NUCLEARBOMB,
    #          (117 + (game.ladders[ladder][0][0] * 51) - 17, 517 - (game.ladders[ladder][0][1] * 51) - 240))
    for nuke in (range(len(nuke_cache))):
        WIN.blit(a.NUCLEARBOMB,
                 (125 + (nuke_cache[nuke][0] * 51), 522 - (nuke_cache[nuke][1] * 51)))

def draw_nuke_buttons(p):
    if game.players[p][2] == 0:
        WIN.blit(a.NUCLEARICONTRANSPARENT, NUKE_ICON_LOCATION)
    else:
        WIN.blit(a.NUCLEARICON, NUKE_ICON_LOCATION)
        if game.degraded_nuke_text == 0:
            font = pygame.font.SysFont("consolas", 120)
            text = font.render(str(game.players[p][2]), True, RED)
            WIN.blit(text, (90, 620))
        else:
            font = pygame.font.SysFont("impact", 120)
            text = font.render(str(game.players[p][2]), True, RED)
            WIN.blit(text, (90, 600))
        NUKE_BUTTON[0].draw()

def draw_dice(p):
    if game.player_to_move == p:
        DICE_BUTTON[0].enable()
    else:
        DICE_BUTTON[0].disable()
    DICE_BUTTON[0].draw()
    if game.dice_degraded == 0:
        WIN.blit(a.DICE[game.dice_pips], (550, 625))
    else:
        WIN.blit(a.DICEDEG[game.dice_pips], (550, 625))

def draw_move_icon():
    for player in range(1, len(game.players)):
        if player == game.player_to_move and game.pieces_degraded == 0:
            if game.players[player][1] == "Red":
                WIN.blit(a.BIGGERPIECERED, MOVE_TURN_ICON_LOCATION)
            if game.players[player][1] == "Green":
                WIN.blit(a.BIGGERPIECEGREEN, MOVE_TURN_ICON_LOCATION)
            if game.players[player][1] == "Blue":
                WIN.blit(a.BIGGERPIECEBLUE, MOVE_TURN_ICON_LOCATION)
            if game.players[player][1] == "Yellow":
                WIN.blit(a.BIGGERPIECEYELLOW, MOVE_TURN_ICON_LOCATION)
        elif player == game.player_to_move and game.pieces_degraded == 1:
            if game.players[player][1] == "Red":
                WIN.blit(a.BIGGERPIECEREDDEG, MOVE_TURN_ICON_LOCATION)
            if game.players[player][1] == "Green":
                WIN.blit(a.BIGGERPIECEGREENDEG, MOVE_TURN_ICON_LOCATION)
            if game.players[player][1] == "Blue":
                WIN.blit(a.BIGGERPIECEBLUEDEG, MOVE_TURN_ICON_LOCATION)
            if game.players[player][1] == "Yellow":
                WIN.blit(a.BIGGERPIECEYELLOWDEG, MOVE_TURN_ICON_LOCATION)

def draw_board(game):
    WIN.blit(a.BOARD[game.board], (WIDTH / 2 - a.BOARD1.get_width() / 2, 30))

def draw_winner_window(p, game):
    font = pygame.font.SysFont("consolas", 70, bold=True)
    text = font.render("ERROR", True, parse_color(game.players[game.winner][1]))
    if game.winner == p:
        #, parse_color(game.players[game.winner][1])
        if game.num_nukes_used == 0:
            text = font.render("YOU WON! :D", True, parse_color(game.players[game.winner][1]))
            if sound_enabled:
                a.pacifistwin.play()
            pygame.mixer.music.stop()
        if game.num_nukes_used >= 1:
            text = font.render("You won...", True, parse_color(game.players[game.winner][1]))
            if sound_enabled:
                a.nukewin.play()
            if music_degraded == 0:
                pygame.mixer.music.stop()
    else:
        if game.num_nukes_used == 0:
            text = font.render(game.players[game.winner][1].upper() + " WON! :)", True, parse_color(game.players[game.winner][1]))
            if sound_enabled:
                a.pacifistwin.play()
            pygame.mixer.music.stop()
        if game.num_nukes_used >= 1:
            text = font.render(game.players[game.winner][1] + " won...", True, parse_color(game.players[game.winner][1]))
            if sound_enabled:
                a.nukewin.play()
            if music_degraded == 0:
                pygame.mixer.music.stop()
    blit_centered_text(text, y_offset=-325)
    # else:
    #     font = pygame.font.SysFont("consolas", 25)
    #     if game.winner == p:
    #         # text = font.render("You" + m.winner_message, True, WHITE)
    #     else:
    #         # text = font.render(game.players[game.winner][1] + m.winner_message, True,
    #         #                    parse_color(game.players[game.winner][1]))
    #     blit_centered_text(text, y_offset=-30)
    #     text = font.render(m.winner_message_2, True, WHITE)
    #     blit_centered_text(text, y_offset=30)

def draw_game_objects(game=None, p=None, player_position_cache=None):
    # a box on the board is 46x47 pixels at 750x750 resolution
    # moving x or y means change by 51 pixels in that direction
    # def calculate_offset(position):
    #     y_offset = position // 10
    #     x_offset = position % 10
    #     if y_offset % 2 != 0:
    #         x_offset = 9 - x_offset
    #     return y_offset, x_offset
    if game.started:
        READY_UP_BUTTON[0].disable()
    draw_board(game)
    draw_dice(p)
    draw_nuke_buttons(p)
    if not debug.disable_move_turns:
        draw_move_icon()
    if not debug.disable_snakes_and_ladders:
        draw_snakes_and_ladders()
    draw_nukes()
    draw_game_pieces(game, p)
    explosion_group.draw(WIN)
    explosion_group.update()
    # if game.winner != 0:
    #     draw_winner_window(p)

    # pygame.draw.rect(WIN, BLACK, (122,522,46,47))
    # pygame.draw.rect(WIN, BLACK, (173,522,46,47))
    # pygame.draw.rect(WIN, BLACK, (122,471,46,47))
    # DEBUG CODE
    # redraw_window(white = False)

def draw_bg(game=None):
    if game == None or game.discoloration == 0:
        WIN.fill(WHITE)
    if game != None:
        if game.discoloration == 1:
            WIN.fill((192, 192, 192))
        elif game.discoloration == 2:
            WIN.fill((128, 128, 128))
        elif game.discoloration == 3:
            WIN.fill((64, 64, 64))
        elif game.discoloration == 4:
            WIN.fill((102, 0, 0))
        elif game.discoloration >= 5:
            WIN.fill((0, 0, 0))

def redraw_window(game=None, p=None, white=True, update=True):
    if white == True:
        draw_bg(game)
    if game and p != None:
        if game.started == True:
            draw_game_objects(game, p)
        # if player has not chosen color yet
        check_and_ask_for_color(game, p)
        check_and_display_waiting_for_players(game, p)
    if update:
        pygame.display.update()
    # DEBUG CODE
    # pygame.time.delay(5999)


def connect():
    redraw_window()
    server_crash = False
    # if debug:
    #     p = 1
    #     main(p)
    font = pygame.font.SysFont("consolas", 80)
    text = font.render("Connecting...", True, BLUE)
    blit_centered_text(text)
    pygame.display.update()
    try:
        p = int(n.get_p())
    except ValueError:
        print("Server crashed!")
        pygame.quit()
        server_crash = True
    except TypeError as e:
        print("Could not connect!")
        print(e)
        failed_to_connect()

    if not server_crash:
        print("You are player", p)
        main(p)


def main(p):
    global players_moving, player_position_cache, music_degraded, game, nukes_acquired
    run = True
    nuke_rendered = False
    nukes_used = 0
    music_set = False

    snakes_gone_down = 0
    ladders_gone_up = 0
    nukes_acquired = 0
    while run:
        clock.tick(60)
        try:
            game = n.send("get")
        except Exception as e:
            run = False
            print("Couldn't get game")
            print(e)
            break
        if game.started:
            if not music_set and sound_enabled:
                pygame.mixer.music.load(a.papers_please)
                pygame.mixer.music.set_volume(0.1)
                pygame.mixer.music.play(-1)
                music_set = True
            if nukes_used == 7 and music_degraded == 0:
                pygame.mixer.music.load(a.but_nobody_came)
                pygame.mixer.music.set_volume(0.1)
                pygame.mixer.music.play(-1)
                music_degraded = 1
            if music_degraded == 1:
                # pygame.mixer.music.load(a.genocide)
                pygame.mixer.music.load(a.but_nobody_came)
                pygame.mixer.music.set_volume(0.1)
                pygame.mixer.music.play(-1)
                music_degraded = 2
        if not nukes_cached:
            cache_initial_nuke_positions(game)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if game.started:
                    if game.players[p][2] > 0:
                        NUKE_BUTTON[0].enable()
                    else:
                        NUKE_BUTTON[0].disable()
                else:
                    DICE_BUTTON[0].disable()
                    NUKE_BUTTON[0].disable()
                for btn in BUTTONS:
                    if btn.click(pos):
                        game = n.send(btn.text)
                        print("Clicked:", btn.text)
                        print("Position", game.players[p][0])
                        print("Color:", game.players[p][1])
                        print("Blocked colors", game.blocked_colors)
            if event.type == pygame.KEYUP and debug.movement and game.started:
                if event.key == pygame.K_1:
                    game = n.send("1")
                    debug_print(p, game)
                if event.key == pygame.K_2:
                    game = n.send("2")
                    debug_print(p, game)
                if event.key == pygame.K_3:
                    game = n.send("3")
                    debug_print(p, game)
                if event.key == pygame.K_4:
                    game = n.send("4")
                    debug_print(p, game)
                if event.key == pygame.K_5:
                    game = n.send("5")
                    debug_print(p, game)
                if event.key == pygame.K_6:
                    game = n.send("6")
                    debug_print(p, game)
                if event.key == pygame.K_8:
                    game = n.send("-1")
                    debug_print(p, game)
                if event.key == pygame.K_UP:
                    game = n.send("Up")
                    debug_print(p, game)
                if event.key == pygame.K_DOWN:
                    game = n.send("Down")
                    debug_print(p, game)
                if event.key == pygame.K_LEFT:
                    game = n.send("Left")
                    debug_print(p, game)
                if event.key == pygame.K_RIGHT:
                    game = n.send("Right")
                    debug_print(p, game)
                if event.key == pygame.K_h:
                    game = n.send("killme")
                    debug_print(p, game)
        if not debug.printed and not debug.disable_snakes_and_ladders:
            print("Snake 0 (green loveable snake):", game.snakes[0])
            print("Snake 1 (cutesy orange snake):", game.snakes[1])
            print("Snake 2 (long squiggly red snake):", game.snakes[2])
            print("Snake 3 (the PYTHON snake):", game.snakes[3])
            print ("Ladder 1", game.ladders[0])
            print("Ladder 2", game.ladders[1])
            print("Ladder 3", game.ladders[2])
            print("Ladder 4", game.ladders[3])
            for nuke in (range(len(game.nukes))):
                print("Nuke", nuke,"at", game.nukes[nuke])
            print("Game id", game.id)
            print("Player ids connected", game.player_ids_connected)
        #     # print(game.board)
        #     print()
            debug.printed = True

        if debug.debug and game.players[p][4] != True:
            game = n.send("debug")

        if snakes_gone_down != game.snakes_gone_down:
            if sound_enabled:
                a.snake.play()
            snakes_gone_down += 1
        if ladders_gone_up != game.ladders_gone_up:
            if sound_enabled:
                a.ladder.play()
            ladders_gone_up += 1

        if nukes_used == game.num_nukes_used:
            nuke_rendered = False
        else:
            cache_player_positions(game)
            nukes_used += 1
            if not nuke_rendered:
                explosion = Explosion(WIDTH / 2, HEIGHT / 2)
                explosion_group.add(explosion)
                if sound_enabled:
                    a.explosion.play()
                nuke_rendered = True
        check_if_player_moving(game)
        # main game redraw function
        redraw_window(game=game, p=p)
        cache_nukes(p, game)
        cache_player_positions(game)
        if game.winner != 0:
            # game = n.send("ending")
            redraw_window(game=game, p=p, update=False)
            draw_winner_window(p, game)
            pygame.display.update()
            pygame.time.delay(3000)
            run = False
    del game
    nuke_cache.clear()

def cache_nukes(p, game):
    global nukes_acquired
    for player in range(1, game.num_of_players + 1):
        if nukes_acquired != game.nukes_acquired[p] and not players_moving[p]:
            for nuke in range(len(nuke_cache)):
                if game.nukes[nuke] != nuke_cache[nuke]:
                    nuke_cache[nuke] = game.nukes[nuke]
            if sound_enabled:
                a.nuke_get_sounds[random.randint(0, 4)].play()
            nukes_acquired += 1
        else:
            for nuke in range(len(nuke_cache)):
                if game.nukes[nuke] != nuke_cache[nuke]:
                    nuke_cache[nuke] = game.nukes[nuke]


def cache_player_positions(game):
    global players_moving, player_position_cache
    for player in range(1, 5):
        if not players_moving[player]:
            player_movement_started[player] = False
            player_position_cache[player] = game.players[player][0]

def cache_initial_nuke_positions(game):
    global nuke_cache, nukes_cached
    for nuke in (range(len(game.nukes))):
        nuke_cache.append(game.nukes[nuke])
    for nuke in range(len(nuke_cache)):
        if game.nukes[nuke] != nuke_cache[nuke]:
            nuke_cache[nuke] = game.nukes[nuke]
    nukes_cached = True

def check_if_player_moving(game):
    for player in range(1, 5):
        if game.players[player][3]:
            if player_position_cache[player] != game.players[player][0]:
                players_moving[player] = True


def debug_print(p, game):
    pass
    # print(game.players[p][0], ' ', end='')
    # print("Num of nukes", game.players[p][2])
    # print(game.player_to_move)
    # print(game.players[game.player_to_move][1], "to move")

def menu_screen():
    global nukes_cached, sound_enabled, shake_amount, shake_direction
    init_vars()
    explosion_group.empty()
    run = True
    if music_degraded == 0 and sound_enabled:
        pygame.mixer.music.stop()
    nukes_cached = False
    shake_amount = 0
    shake_direction = True
    explosion_easter_egg_counter = 0
    # title_ticks_passed = 0
    while run:
        # while title_ticks_passed < 2000:
        clock.tick(60)
        #     if title_ticks_passed <= 500:
        #         WIN.blit(a.TITLE1, (0, 0))
        #     if 2000 >= title_ticks_passed > 500:
        #         WIN.blit(a.TITLE2, (0, 0))
        #     pygame.display.update()
        #     title_ticks_passed += 1
        WIN.blit(a.TITLE3, (0, 0))
        # font = pygame.font.SysFont("consolas", 60)
        # text = font.render("Click to Play!", True, RED)
        START_GAME_BUTTON[0].draw()
        START_GAME_BUTTON[0].enable()
        if sound_enabled:
            # MUTE_BUTTON[0].draw()
            WIN.blit(a.UNMUTED, MUTE_BUTTON_LOCATION)
            MUTE_BUTTON[0].enable()
        else:
            # UNMUTE_BUTTON[0].draw()
            WIN.blit(a.MUTED, MUTE_BUTTON_LOCATION)
            UNMUTE_BUTTON[0].enable()
        explosion_group.draw(WIN)
        explosion_group.update()
        # blit_centered_text(text)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if START_GAME_BUTTON[0].click(pos):
                    run = False
                if MUTE_BUTTON[0].click(pos) or UNMUTE_BUTTON[0].click(pos):
                    sound_enabled = not sound_enabled
                explosion_easter_egg_counter += 1
                if explosion_easter_egg_counter > 50:
                    explosion = Explosion(WIDTH/2, HEIGHT/2)
                    explosion_group.add(explosion)

    connect()


def failed_to_connect():
    redraw_window()
    font = pygame.font.SysFont("consolas", 60)
    text = font.render("Failed to connect! :(", True, BLACK)
    blit_centered_text(text)
    pygame.display.update()
    pygame.time.delay(1500)
    menu_screen()


while True:
    # DEBUG CODE
    # draw_game_objects()
    if not debug.debug:
        menu_screen()
    else:
        connect()
