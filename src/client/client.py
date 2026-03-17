import pygame
import random
import sys

from . import load_assets as assets
from .button import Button
from .explosion import Explosion
from .utils import *
from .constants import *
from .networking import Network
from ..shared.game import Game

pygame.font.init()
pygame.display.set_icon(assets.ICON)

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snakes, Ladders and Nukes")

client_state = ClientState()

window.fill(WHITE)
font = pygame.font.SysFont("consolas", 60)
text = font.render("LOADING", True, BLACK)
blit_centered_text(window, text)
pygame.display.update()

network = Network()
clock = pygame.time.Clock()

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

explosion_group = pygame.sprite.Group()

SELECT_COLOR_BUTTONS = (
    Button(window, client_state, 'Red', 375, 175, 200, 200, RED, RED, sound=assets.click),
    Button(window, client_state, 'Green', 375, 375, 200, 200, GREEN, GREEN, sound=assets.click),
    Button(window, client_state, 'Blue', 175, 175, 200, 200, BLUE, BLUE, sound=assets.click),
    Button(window, client_state, 'Yellow', 175, 375, 200, 200, YELLOW, YELLOW, sound=assets.click),
)

MUTE_BUTTON_LOCATION = (600, 590)
MUTE_BUTTON = (Button(window, client_state, 'Mute', MUTE_BUTTON_LOCATION[0], MUTE_BUTTON_LOCATION[1], 100, 100, WHITE, WHITE, sound=assets.click),)
UNMUTE_BUTTON = (Button(window, client_state, 'Unmute', MUTE_BUTTON_LOCATION[0], MUTE_BUTTON_LOCATION[1], 100, 100, WHITE, WHITE, sound=assets.click),)

START_GAME_BUTTON = (Button(window, client_state, 'Start Game', 420, 450, 275, 110, BLACK, WHITE, sound=assets.click),)

READY_UP_BUTTON = (Button(window, client_state, 'Ready Up', 225, 450, 300, 150, BLACK, WHITE, sound=assets.click),)

DICE_BUTTON = (Button(window, client_state, 'roll', 550, 625, 100, 100, BLACK, WHITE, border_radius=100, sound=assets.dice),)

NUKE_BUTTON = (Button(window, client_state, 'NUKE', 295, 615, 130, 130, RED, WHITE, border_radius=50, sound=assets.click),)

BUTTONS = SELECT_COLOR_BUTTONS + READY_UP_BUTTON + DICE_BUTTON + NUKE_BUTTON

NUKE_ICON_LOCATION = (15, 635)
MOVE_TURN_ICON_LOCATION = (5, 5)

def check_and_display_waiting_for_players(game, p):
    # checks if color selection has been made. if it has been made, display waiting for players
    if not game.started and game.players[p][1] != None:
        font = pygame.font.SysFont("consolas", 25)
        text = font.render("Lobby: " + str(game.id), True, BLACK)
        window.blit(text, (10, 10))
        text = font.render("Player: " + str(p), True, BLACK)
        window.blit(text, (10, 40))
        text = font.render(game.players[p][1], True, parse_color(game.players[p][1]))
        window.blit(text, (10, 70))
        font = pygame.font.SysFont("consolas", 40)
        text = font.render("Players in Lobby: (" + str(game.num_of_players) + "/4)", True, BLACK)
        blit_centered_text(window, text, -220)
        if game.num_of_players < 4:
            font = pygame.font.SysFont("consolas", 50)
            text = font.render("Waiting for Players...", True, BLUE)
            blit_centered_text(window, text, -50)
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
        blit_centered_text(window, text, -300)
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
        window.blit(assets.PIECES[game.players[player][1]],
                 (BOARD_START_X + x_offset * SQUARE_SIZE + offset_nudge + shake_amount,
                  BOARD_START_Y - y_offset * SQUARE_SIZE + offset_nudge))
    else:
        window.blit(assets.PIECESDEG[game.players[player][1]],
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
        draw_move_icon()
        draw_snakes_and_ladders()
        for hypothetical_stationary_player in range(1, 5):
            if game.players[hypothetical_stationary_player][1] != None:
                if hypothetical_stationary_player != player:
                    draw_stationary_pieces(hypothetical_stationary_player)
        draw_nukes()
        if game.pieces_degraded == 0:
            window.blit(assets.PIECES[game.players[player][1]],
                     (BOARD_START_X + old_x * SQUARE_SIZE + 0.85 * ticks_passed * distance_x + offset_nudge,
                      BOARD_START_Y - old_y * SQUARE_SIZE - 0.85 * ticks_passed * distance_y + offset_nudge))
        else:
            window.blit(assets.PIECESDEG[game.players[player][1]],
                     (BOARD_START_X + old_x * SQUARE_SIZE + 0.85 * ticks_passed * distance_x + offset_nudge,
                      BOARD_START_Y - old_y * SQUARE_SIZE - 0.85 * ticks_passed * distance_y + offset_nudge))
        explosion_group.draw(window)
        explosion_group.update()
        pygame.display.update()
        if not loop_completed and ticks_passed == 60:
            cache_nukes(p, game)
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
                window.blit(assets.SNAKE1,
                         (117 + (game.snakes[snake][0][0] * 51) - 19, 517 - (game.snakes[snake][0][1] * 51) + 33))
            if snake == 1:
                window.blit(assets.SNAKE2,
                         (117 + (game.snakes[snake][0][0] * 51) - 65, 517 - (game.snakes[snake][0][1] * 51) + 23))
            if snake == 2:
                window.blit(assets.SNAKE3,
                         (117 + (game.snakes[snake][0][0] * 51) + 10, 517 - (game.snakes[snake][0][1] * 51) + 20))
            if snake == 3:
                window.blit(assets.SNAKE4,
                         (117 + (game.snakes[snake][0][0] * 51) , 517 - (game.snakes[snake][0][1] * 51) + 28))
        for ladder in range (3, -1, -1):
            if ladder == 0:
                window.blit(assets.LADDER1,
                         (117 + (game.ladders[ladder][0][0] * 51) + 15, 517 - (game.ladders[ladder][0][1] * 51) - 148))
            if ladder == 1:
                window.blit(assets.LADDER2,
                         (117 + (game.ladders[ladder][0][0] * 51) + 15, 517 - (game.ladders[ladder][0][1] * 51) - 79))
            if ladder == 2:
                window.blit(assets.LADDER3,
                         (117 + (game.ladders[ladder][0][0] * 51) - 41, 517 - (game.ladders[ladder][0][1] * 51) - 67))
            if ladder == 3:
                window.blit(assets.LADDER4,
                         (117 + (game.ladders[ladder][0][0] * 51) - 17, 517 - (game.ladders[ladder][0][1] * 51) - 240))
    else:
        for snake in range(3, -1, -1):
            if snake == 0:
                window.blit(assets.SNAKE1DEG,
                         (117 + (game.snakes[snake][0][0] * 51) - 19, 517 - (game.snakes[snake][0][1] * 51) + 33))
            if snake == 1:
                window.blit(assets.SNAKE2DEG,
                         (117 + (game.snakes[snake][0][0] * 51) - 65, 517 - (game.snakes[snake][0][1] * 51) + 23))
            if snake == 2:
                window.blit(assets.SNAKE3DEG,
                         (117 + (game.snakes[snake][0][0] * 51) + 10, 517 - (game.snakes[snake][0][1] * 51) + 20))
            if snake == 3:
                window.blit(assets.SNAKE4DEG,
                         (117 + (game.snakes[snake][0][0] * 51) , 517 - (game.snakes[snake][0][1] * 51) + 28))
        for ladder in range (3, -1, -1):
            if ladder == 0:
                window.blit(assets.LADDER1,
                         (117 + (game.ladders[ladder][0][0] * 51) + 15, 517 - (game.ladders[ladder][0][1] * 51) - 148))
            if ladder == 1:
                window.blit(assets.LADDER2DEG,
                         (117 + (game.ladders[ladder][0][0] * 51) + 15, 517 - (game.ladders[ladder][0][1] * 51) - 79))
            if ladder == 2:
                window.blit(assets.LADDER3,
                         (117 + (game.ladders[ladder][0][0] * 51) - 41, 517 - (game.ladders[ladder][0][1] * 51) - 67))
            if ladder == 3:
                window.blit(assets.LADDER4DEG,
                         (117 + (game.ladders[ladder][0][0] * 51) - 17, 517 - (game.ladders[ladder][0][1] * 51) - 240))

def draw_nukes():
    # window.blit(assets.NUCLEARBOMB,
    #          (117 + (game.ladders[ladder][0][0] * 51) - 17, 517 - (game.ladders[ladder][0][1] * 51) - 240))
    for nuke in (range(len(nuke_cache))):
        window.blit(assets.NUCLEARBOMB,
                 (125 + (nuke_cache[nuke][0] * 51), 522 - (nuke_cache[nuke][1] * 51)))

def draw_nuke_buttons(p):
    if game.players[p][2] == 0:
        window.blit(assets.NUKEINACTIVE, NUKE_ICON_LOCATION)
    else:
        window.blit(assets.NUKEACTIVE, NUKE_ICON_LOCATION)
        if game.degraded_nuke_text == 0:
            font = pygame.font.SysFont("consolas", 120)
            text = font.render(str(game.players[p][2]), True, RED)
            window.blit(text, (90, 620))
        else:
            font = pygame.font.SysFont("impact", 120)
            text = font.render(str(game.players[p][2]), True, RED)
            window.blit(text, (90, 600))
        NUKE_BUTTON[0].draw()

def draw_dice(p):
    if game.player_to_move == p:
        DICE_BUTTON[0].enable()
    else:
        DICE_BUTTON[0].disable()
    DICE_BUTTON[0].draw()
    if game.dice_degraded == 0:
        window.blit(assets.DICE[game.dice_pips], (550, 625))
    else:
        window.blit(assets.DICEDEG[game.dice_pips], (550, 625))

def draw_move_icon():
    for player in range(1, len(game.players)):
        if player == game.player_to_move and game.pieces_degraded == 0:
            if game.players[player][1] == "Red":
                window.blit(assets.BIGGERPIECERED, MOVE_TURN_ICON_LOCATION)
            if game.players[player][1] == "Green":
                window.blit(assets.BIGGERPIECEGREEN, MOVE_TURN_ICON_LOCATION)
            if game.players[player][1] == "Blue":
                window.blit(assets.BIGGERPIECEBLUE, MOVE_TURN_ICON_LOCATION)
            if game.players[player][1] == "Yellow":
                window.blit(assets.BIGGERPIECEYELLOW, MOVE_TURN_ICON_LOCATION)
        elif player == game.player_to_move and game.pieces_degraded == 1:
            if game.players[player][1] == "Red":
                window.blit(assets.BIGGERPIECEREDDEG, MOVE_TURN_ICON_LOCATION)
            if game.players[player][1] == "Green":
                window.blit(assets.BIGGERPIECEGREENDEG, MOVE_TURN_ICON_LOCATION)
            if game.players[player][1] == "Blue":
                window.blit(assets.BIGGERPIECEBLUEDEG, MOVE_TURN_ICON_LOCATION)
            if game.players[player][1] == "Yellow":
                window.blit(assets.BIGGERPIECEYELLOWDEG, MOVE_TURN_ICON_LOCATION)

def draw_board(game):
    window.blit(assets.BOARD[game.board], (WIDTH / 2 - assets.BOARD1.get_width() / 2, 30))

def draw_winner_window(p, game):
    font = pygame.font.SysFont("consolas", 70, bold=True)
    text = font.render("ERROR", True, parse_color(game.players[game.winner][1]))
    if game.winner == p:
        #, parse_color(game.players[game.winner][1])
        if game.num_nukes_used == 0:
            text = font.render("YOU WON! :D", True, parse_color(game.players[game.winner][1]))
            if client_state.client_state.sound_enabled:
                assets.pacifistwin.play()
            pygame.mixer.music.stop()
        if game.num_nukes_used >= 1:
            text = font.render("You won...", True, parse_color(game.players[game.winner][1]))
            if client_state.sound_enabled:
                assets.nukewin.play()
            if client_state.music_degraded == 0:
                pygame.mixer.music.stop()
    else:
        if game.num_nukes_used == 0:
            text = font.render(game.players[game.winner][1].upper() + " WON! :)", True, parse_color(game.players[game.winner][1]))
            if client_state.sound_enabled:
                assets.pacifistwin.play()
            pygame.mixer.music.stop()
        if game.num_nukes_used >= 1:
            text = font.render(game.players[game.winner][1] + " won...", True, parse_color(game.players[game.winner][1]))
            if client_state.sound_enabled:
                assets.nukewin.play()
            if client_state.music_degraded == 0:
                pygame.mixer.music.stop()
    blit_centered_text(window, text, y_offset=-325)
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
    draw_move_icon()
    draw_snakes_and_ladders()
    draw_nukes()
    draw_game_pieces(game, p)
    explosion_group.draw(window)
    explosion_group.update()
    # if game.winner != 0:
    #     draw_winner_window(p)

    # pygame.draw.rect(window, BLACK, (122,522,46,47))
    # pygame.draw.rect(window, BLACK, (173,522,46,47))
    # pygame.draw.rect(window, BLACK, (122,471,46,47))
    # DEBUG CODE
    # redraw_window(white = False)

def draw_bg(game=None):
    if game == None or game.discoloration == 0:
        window.fill(WHITE)
    if game != None:
        if game.discoloration == 1:
            window.fill((192, 192, 192))
        elif game.discoloration == 2:
            window.fill((128, 128, 128))
        elif game.discoloration == 3:
            window.fill((64, 64, 64))
        elif game.discoloration == 4:
            window.fill((102, 0, 0))
        elif game.discoloration >= 5:
            window.fill((0, 0, 0))

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
    font = pygame.font.SysFont("consolas", 80)
    text = font.render("Connecting...", True, BLUE)
    blit_centered_text(window, text)
    pygame.display.update()
    try:
        p = int(network.get_p())
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
    global players_moving, player_position_cache, game, nukes_acquired
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
            game = network.send("get")
        except Exception as e:
            run = False
            print("Couldn't get game")
            print(e)
            break
        if game.started:
            if not music_set and client_state.sound_enabled:
                pygame.mixer.music.load(assets.papers_please)
                pygame.mixer.music.set_volume(0.1)
                pygame.mixer.music.play(-1)
                music_set = True
            if nukes_used == 7 and client_state.music_degraded == 0:
                pygame.mixer.music.load(assets.but_nobody_came)
                pygame.mixer.music.set_volume(0.1)
                pygame.mixer.music.play(-1)
                client_state.music_degraded = 1
            if client_state.music_degraded == 1:
                # pygame.mixer.music.load(assets.genocide)
                pygame.mixer.music.load(assets.but_nobody_came)
                pygame.mixer.music.set_volume(0.1)
                pygame.mixer.music.play(-1)
                client_state.music_degraded = 2
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
                        game = network.send(btn.text)
                        print("Clicked:", btn.text)
                        print("Position", game.players[p][0])
                        print("Color:", game.players[p][1])
                        print("Blocked colors", game.blocked_colors)
            #if event.type == pygame.KEYUP and debug.movement and game.started:
            #    if event.key == pygame.K_1:
            #        game = n.send("1")
            #        debug_print(p, game)
            #    if event.key == pygame.K_2:
            #        game = n.send("2")
            #        debug_print(p, game)
            #    if event.key == pygame.K_3:
            #        game = n.send("3")
            #        debug_print(p, game)
            #    if event.key == pygame.K_4:
            #        game = n.send("4")
            #        debug_print(p, game)
            #    if event.key == pygame.K_5:
            #        game = n.send("5")
            #        debug_print(p, game)
            #    if event.key == pygame.K_6:
            #        game = n.send("6")
            #        debug_print(p, game)
            #    if event.key == pygame.K_8:
            #        game = n.send("-1")
            #        debug_print(p, game)
            #    if event.key == pygame.K_UP:
            #        game = n.send("Up")
            #        debug_print(p, game)
            #    if event.key == pygame.K_DOWN:
            #        game = n.send("Down")
            #        debug_print(p, game)
            #    if event.key == pygame.K_LEFT:
            #        game = n.send("Left")
            #        debug_print(p, game)
            #    if event.key == pygame.K_RIGHT:
            #        game = n.send("Right")
            #        debug_print(p, game)
            #    if event.key == pygame.K_h:
            #        game = n.send("killme")
            #        debug_print(p, game)

        if snakes_gone_down != game.snakes_gone_down:
            if client_state.sound_enabled:
                assets.snake.play()
            snakes_gone_down += 1
        if ladders_gone_up != game.ladders_gone_up:
            if client_state.sound_enabled:
                assets.ladder.play()
            ladders_gone_up += 1

        if nukes_used == game.num_nukes_used:
            nuke_rendered = False
        else:
            cache_player_positions(game)
            nukes_used += 1
            if not nuke_rendered:
                explosion = Explosion(WIDTH / 2, HEIGHT / 2)
                explosion_group.add(explosion)
                if client_state.sound_enabled:
                    assets.explosion.play()
                nuke_rendered = True
        check_if_player_moving(game)
        redraw_window(game=game, p=p)
        cache_nukes(p, game)
        cache_player_positions(game)
        if game.winner != 0:
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
            if client_state.sound_enabled:
                assets.nuke_get_sounds[random.randint(0, 4)].play()
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


def menu_screen():
    global nukes_cached, shake_amount, shake_direction
    init_vars()
    run = True
    if client_state.music_degraded == 0 and client_state.sound_enabled:
        pygame.mixer.music.stop()
    nukes_cached = False
    shake_amount = 0
    shake_direction = True
    explosion_easter_egg_counter = 0
    while run:
        clock.tick(60)
        window.blit(assets.TITLE3, (0, 0))
        START_GAME_BUTTON[0].draw()
        START_GAME_BUTTON[0].enable()
        if client_state.sound_enabled:
            window.blit(assets.UNMUTED, MUTE_BUTTON_LOCATION)
            MUTE_BUTTON[0].enable()
        else:
            window.blit(assets.MUTED, MUTE_BUTTON_LOCATION)
            UNMUTE_BUTTON[0].enable()
        explosion_group.draw(window)
        explosion_group.update()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if START_GAME_BUTTON[0].click(pos):
                    run = False
                if MUTE_BUTTON[0].click(pos) or UNMUTE_BUTTON[0].click(pos):
                    client_state.sound_enabled = not client_state.sound_enabled
                explosion_easter_egg_counter += 1
                if explosion_easter_egg_counter > 10:
                    explosion = Explosion(WIDTH/2, HEIGHT/2)
                    explosion_group.add(explosion)
    connect()


def failed_to_connect():
    redraw_window()
    font = pygame.font.SysFont("consolas", 60)
    text = font.render("Failed to connect! :(", True, BLACK)
    blit_centered_text(window, text)
    pygame.display.update()
    pygame.time.delay(1500)
    menu_screen()


menu_screen()
