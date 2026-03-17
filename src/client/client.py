import pygame
import random
import sys
import copy

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

state = ClientState()

window.fill(WHITE)
font = pygame.font.SysFont("consolas", 60)
text = font.render("LOADING", True, BLACK)
blit_centered_text(window, text)
pygame.display.update()

network = Network()
clock = pygame.time.Clock()

explosion_group = pygame.sprite.Group()

MUTE_BUTTON_LOCATION = (600, 590)
NUKE_ICON_LOCATION = (15, 635)
MOVE_TURN_ICON_LOCATION = (5, 5)

ui_buttons = {
    "mute_button": Button(window, state, 'Mute', MUTE_BUTTON_LOCATION[0], MUTE_BUTTON_LOCATION[1], 100, 100, WHITE, WHITE, sound=assets.click),
    "unmute_button": Button(window, state, 'Unmute', MUTE_BUTTON_LOCATION[0], MUTE_BUTTON_LOCATION[1], 100, 100, WHITE, WHITE, sound=assets.click),
    "start_game_button": Button(window, state, 'Start Game', 420, 450, 275, 110, BLACK, WHITE, sound=assets.click),
    "ready_up_button": Button(window, state, 'Ready Up', 225, 450, 300, 150, BLACK, WHITE, sound=assets.click),
    "dice_button": Button(window, state, 'roll', 550, 625, 100, 100, BLACK, WHITE, border_radius=100, sound=assets.dice),
    "nuke_button": Button(window, state, 'NUKE', 295, 615, 130, 130, RED, WHITE, border_radius=50, sound=assets.click),
}

select_color_buttons = {
    "red": Button(window, state, 'Red', 375, 175, 200, 200, RED, RED, sound=assets.click),
    "green": Button(window, state, 'Green', 375, 375, 200, 200, GREEN, GREEN, sound=assets.click),
    "blue": Button(window, state, 'Blue', 175, 175, 200, 200, BLUE, BLUE, sound=assets.click),
    "yellow": Button(window, state, 'Yellow', 175, 375, 200, 200, YELLOW, YELLOW, sound=assets.click),
}

buttons = ui_buttons | select_color_buttons

def check_and_display_waiting_for_players(p):
    # checks if color selection has been made. if it has been made, display waiting for players
    if not state.game.started and state.game.players[p][1] != None:
        font = pygame.font.SysFont("consolas", 25)
        text = font.render("Lobby: " + str(state.game.id), True, BLACK)
        window.blit(text, (10, 10))
        text = font.render("Player: " + str(p), True, BLACK)
        window.blit(text, (10, 40))
        text = font.render(state.game.players[p][1], True, parse_color(state.game.players[p][1]))
        window.blit(text, (10, 70))
        font = pygame.font.SysFont("consolas", 40)
        text = font.render("Players in Lobby: (" + str(state.game.num_of_players) + "/4)", True, BLACK)
        blit_centered_text(window, text, -220)
        if state.game.num_of_players < 4:
            font = pygame.font.SysFont("consolas", 50)
            text = font.render("Waiting for Players...", True, BLUE)
            blit_centered_text(window, text, -50)
        if state.game.num_of_players >= 2:
            if state.game.players[p][3] == True:
                buttons["ready_up_button"].disable()
            else:
                buttons["ready_up_button"].draw()
                buttons["ready_up_button"].enable()


def check_and_ask_for_color(p):
    if state.game.players[p][1] == None:
        font = pygame.font.SysFont("consolas", 50)
        text = font.render("Choose your colour!", True, BLACK)
        blit_centered_text(window, text, -300)
        for btn in select_color_buttons.values():
            if btn.text in state.game.blocked_colors:
                btn.disable()
            else:
                btn.draw()
                btn.enable()
    else:
        for btn in select_color_buttons.values():
            btn.disable()

    # nudge each of the player tokens to prevent overlapping
def calculate_offset_nudge(player):
    return (player - 1) * 5

def draw_stationary_pieces(player):
    # if shake_direction true, move right
    x_offset, y_offset = state.game.players[player][0][0], state.game.players[player][0][1]
    offset_nudge = calculate_offset_nudge(player)
    if state.game.piece_shake == 1:
        if shake_direction:
            shake_amount += 1
            if shake_amount == 5:
                shake_direction = not shake_direction
        if not shake_direction:
            shake_amount -= 1
            if shake_amount == -5:
                shake_direction = not shake_direction
    if state.game.pieces_degraded == 0:
        window.blit(assets.PIECES[state.game.players[player][1]],
                 (BOARD_START_X + x_offset * SQUARE_SIZE + offset_nudge + state.shake_amount,
                  BOARD_START_Y - y_offset * SQUARE_SIZE + offset_nudge))
    else:
        window.blit(assets.PIECESDEG[state.game.players[player][1]],
                 (BOARD_START_X + x_offset * SQUARE_SIZE + offset_nudge + state.shake_amount,
                  BOARD_START_Y - y_offset * SQUARE_SIZE + offset_nudge))

def draw_game_pieces(p):
    for player in range(1, 5):
        if state.game.players[player][3] == True:
            draw_stationary_pieces(player)
            if state.players_moving[player] and not state.player_movement_started[player] and not state.game.nuke_used:
                play_movement_animation(player, calculate_offset_nudge(player), p)


def play_movement_animation(player, offset_nudge, p):
    # destination is state.game.players[player][0][0]
    # old position is player_position_cache
    ticks_passed = 0
    if state.game.player_travelled_on_movable[player]:
        # print("travelled on movable")
        # print(state.game.players_previous_space[player])
        loop_completed = False
        old_x, old_y = state.player_position_cache[player][0], state.player_position_cache[player][1]
        new_x, new_y = state.game.players_previous_space[player][0], state.game.players_previous_space[player][1]
        distance_x, distance_y = new_x - old_x, new_y - old_y
    else:
        # print("didn't")
        # print(state.game.players_previous_space[player])
        loop_completed = True
        old_x, old_y = state.player_position_cache[player][0], state.player_position_cache[player][1]
        new_x, new_y = state.game.players[player][0][0], state.game.players[player][0][1]
        distance_x, distance_y = new_x - old_x, new_y - old_y
    while state.players_moving[player]:
        state.player_movement_started[player] = True
        ticks_passed += 1
        draw_bg()
        draw_board()
        draw_dice(p)
        draw_nuke_buttons(p)
        draw_move_icon()
        draw_snakes_and_ladders()
        for hypothetical_stationary_player in range(1, 5):
            if state.game.players[hypothetical_stationary_player][1] != None:
                if hypothetical_stationary_player != player:
                    draw_stationary_pieces(hypothetical_stationary_player)
        draw_nukes()
        if state.game.pieces_degraded == 0:
            window.blit(assets.PIECES[state.game.players[player][1]],
                     (BOARD_START_X + old_x * SQUARE_SIZE + 0.85 * ticks_passed * distance_x + offset_nudge,
                      BOARD_START_Y - old_y * SQUARE_SIZE - 0.85 * ticks_passed * distance_y + offset_nudge))
        else:
            window.blit(assets.PIECESDEG[state.game.players[player][1]],
                     (BOARD_START_X + old_x * SQUARE_SIZE + 0.85 * ticks_passed * distance_x + offset_nudge,
                      BOARD_START_Y - old_y * SQUARE_SIZE - 0.85 * ticks_passed * distance_y + offset_nudge))
        explosion_group.draw(window)
        explosion_group.update()
        pygame.display.update()
        if not loop_completed and ticks_passed == 60:
            cache_nukes(p)
            old_x, old_y = state.game.players_previous_space[player][0], state.game.players_previous_space[player][1]
            new_x, new_y = state.game.players[player][0][0], state.game.players[player][0][1]
            distance_x, distance_y = new_x - old_x, new_y - old_y
            ticks_passed = 0
            loop_completed = True
        if ticks_passed == 60 and loop_completed:
            state.players_moving[player] = False

def draw_snakes_and_ladders():
    if state.game.snakes_and_ladders_degraded == 0:
        for snake in range(3, -1, -1):
            # y_offset, x_offset = calculate_offset(state.game.snakes[snake][0])
            # if state.game.snakes[snake][3] == True:
            #     x_offset += x_offset
            if snake == 0:
                window.blit(assets.SNAKE1,
                         (117 + (state.game.snakes[snake][0][0] * 51) - 19, 517 - (state.game.snakes[snake][0][1] * 51) + 33))
            if snake == 1:
                window.blit(assets.SNAKE2,
                         (117 + (state.game.snakes[snake][0][0] * 51) - 65, 517 - (state.game.snakes[snake][0][1] * 51) + 23))
            if snake == 2:
                window.blit(assets.SNAKE3,
                         (117 + (state.game.snakes[snake][0][0] * 51) + 10, 517 - (state.game.snakes[snake][0][1] * 51) + 20))
            if snake == 3:
                window.blit(assets.SNAKE4,
                         (117 + (state.game.snakes[snake][0][0] * 51) , 517 - (state.game.snakes[snake][0][1] * 51) + 28))
        for ladder in range (3, -1, -1):
            if ladder == 0:
                window.blit(assets.LADDER1,
                         (117 + (state.game.ladders[ladder][0][0] * 51) + 15, 517 - (state.game.ladders[ladder][0][1] * 51) - 148))
            if ladder == 1:
                window.blit(assets.LADDER2,
                         (117 + (state.game.ladders[ladder][0][0] * 51) + 15, 517 - (state.game.ladders[ladder][0][1] * 51) - 79))
            if ladder == 2:
                window.blit(assets.LADDER3,
                         (117 + (state.game.ladders[ladder][0][0] * 51) - 41, 517 - (state.game.ladders[ladder][0][1] * 51) - 67))
            if ladder == 3:
                window.blit(assets.LADDER4,
                         (117 + (state.game.ladders[ladder][0][0] * 51) - 17, 517 - (state.game.ladders[ladder][0][1] * 51) - 240))
    else:
        for snake in range(3, -1, -1):
            if snake == 0:
                window.blit(assets.SNAKE1DEG,
                         (117 + (state.game.snakes[snake][0][0] * 51) - 19, 517 - (state.game.snakes[snake][0][1] * 51) + 33))
            if snake == 1:
                window.blit(assets.SNAKE2DEG,
                         (117 + (state.game.snakes[snake][0][0] * 51) - 65, 517 - (state.game.snakes[snake][0][1] * 51) + 23))
            if snake == 2:
                window.blit(assets.SNAKE3DEG,
                         (117 + (state.game.snakes[snake][0][0] * 51) + 10, 517 - (state.game.snakes[snake][0][1] * 51) + 20))
            if snake == 3:
                window.blit(assets.SNAKE4DEG,
                         (117 + (state.game.snakes[snake][0][0] * 51) , 517 - (state.game.snakes[snake][0][1] * 51) + 28))
        for ladder in range (3, -1, -1):
            if ladder == 0:
                window.blit(assets.LADDER1,
                         (117 + (state.game.ladders[ladder][0][0] * 51) + 15, 517 - (state.game.ladders[ladder][0][1] * 51) - 148))
            if ladder == 1:
                window.blit(assets.LADDER2DEG,
                         (117 + (state.game.ladders[ladder][0][0] * 51) + 15, 517 - (state.game.ladders[ladder][0][1] * 51) - 79))
            if ladder == 2:
                window.blit(assets.LADDER3,
                         (117 + (state.game.ladders[ladder][0][0] * 51) - 41, 517 - (state.game.ladders[ladder][0][1] * 51) - 67))
            if ladder == 3:
                window.blit(assets.LADDER4DEG,
                         (117 + (state.game.ladders[ladder][0][0] * 51) - 17, 517 - (state.game.ladders[ladder][0][1] * 51) - 240))

def draw_nukes():
    for nuke in (range(len(state.nuke_cache))):
        window.blit(assets.NUCLEARBOMB,
                 (125 + (state.nuke_cache[nuke][0] * 51), 522 - (state.nuke_cache[nuke][1] * 51)))

def draw_nuke_buttons(p):
    if state.game.players[p][2] == 0:
        window.blit(assets.NUKEINACTIVE, NUKE_ICON_LOCATION)
    else:
        window.blit(assets.NUKEACTIVE, NUKE_ICON_LOCATION)
        if state.game.degraded_nuke_text == 0:
            font = pygame.font.SysFont("consolas", 120)
            text = font.render(str(state.game.players[p][2]), True, RED)
            window.blit(text, (90, 620))
        else:
            font = pygame.font.SysFont("impact", 120)
            text = font.render(str(state.game.players[p][2]), True, RED)
            window.blit(text, (90, 600))
        buttons["nuke_button"].draw()

def draw_dice(p):
    if state.game.player_to_move == p:
        buttons["dice_button"].enable()
    else:
        buttons["dice_button"].disable()
    buttons["dice_button"].draw()
    if state.game.dice_degraded == 0:
        window.blit(assets.DICE[state.game.dice_pips], (550, 625))
    else:
        window.blit(assets.DICEDEG[state.game.dice_pips], (550, 625))

def draw_move_icon():
    for player in range(1, len(state.game.players)):
        if player == state.game.player_to_move and state.game.pieces_degraded == 0:
            if state.game.players[player][1] == "Red":
                window.blit(assets.BIGGERPIECERED, MOVE_TURN_ICON_LOCATION)
            if state.game.players[player][1] == "Green":
                window.blit(assets.BIGGERPIECEGREEN, MOVE_TURN_ICON_LOCATION)
            if state.game.players[player][1] == "Blue":
                window.blit(assets.BIGGERPIECEBLUE, MOVE_TURN_ICON_LOCATION)
            if state.game.players[player][1] == "Yellow":
                window.blit(assets.BIGGERPIECEYELLOW, MOVE_TURN_ICON_LOCATION)
        elif player == state.game.player_to_move and state.game.pieces_degraded == 1:
            if state.game.players[player][1] == "Red":
                window.blit(assets.BIGGERPIECEREDDEG, MOVE_TURN_ICON_LOCATION)
            if state.game.players[player][1] == "Green":
                window.blit(assets.BIGGERPIECEGREENDEG, MOVE_TURN_ICON_LOCATION)
            if state.game.players[player][1] == "Blue":
                window.blit(assets.BIGGERPIECEBLUEDEG, MOVE_TURN_ICON_LOCATION)
            if state.game.players[player][1] == "Yellow":
                window.blit(assets.BIGGERPIECEYELLOWDEG, MOVE_TURN_ICON_LOCATION)

def draw_board():
    window.blit(assets.BOARD[state.game.board], (WIDTH / 2 - assets.BOARD1.get_width() / 2, 30))

def draw_winner_window(p):
    font = pygame.font.SysFont("consolas", 70, bold=True)
    text = font.render("ERROR", True, parse_color(state.game.players[state.game.winner][1]))
    if state.game.winner == p:
        if state.game.num_nukes_used == 0:
            text = font.render("YOU WON! :D", True, parse_color(state.game.players[state.game.winner][1]))
            if state.sound_enabled:
                assets.pacifistwin.play()
            pygame.mixer.music.stop()
        if state.game.num_nukes_used >= 1:
            text = font.render("You won...", True, parse_color(state.game.players[state.game.winner][1]))
            if state.sound_enabled:
                assets.nukewin.play()
            if state.music_degraded == 0:
                pygame.mixer.music.stop()
    else:
        if state.game.num_nukes_used == 0:
            text = font.render(state.game.players[state.game.winner][1].upper() + " WON! :)", True, parse_color(state.game.players[state.game.winner][1]))
            if state.sound_enabled:
                assets.pacifistwin.play()
            pygame.mixer.music.stop()
        if state.game.num_nukes_used >= 1:
            text = font.render(state.game.players[state.game.winner][1] + " won...", True, parse_color(state.game.players[state.game.winner][1]))
            if state.sound_enabled:
                assets.nukewin.play()
            if state.music_degraded == 0:
                pygame.mixer.music.stop()
    blit_centered_text(window, text, y_offset=-325)

def draw_game_objects(p=None, player_position_cache=None):
    # a box on the board is 46x47 pixels at 750x750 resolution
    # moving x or y means change by 51 pixels in that direction
    # def calculate_offset(position):
    #     y_offset = position // 10
    #     x_offset = position % 10
    #     if y_offset % 2 != 0:
    #         x_offset = 9 - x_offset
    #     return y_offset, x_offset
    if state.game.started:
        buttons["ready_up_button"].disable()
    draw_board()
    draw_dice(p)
    draw_nuke_buttons(p)
    draw_move_icon()
    draw_snakes_and_ladders()
    draw_nukes()
    draw_game_pieces(p)
    explosion_group.draw(window)
    explosion_group.update()

def draw_bg():
    if state.game == None or state.game.discoloration == 0:
        window.fill(WHITE)
    if state.game != None:
        if state.game.discoloration == 1:
            window.fill((192, 192, 192))
        elif state.game.discoloration == 2:
            window.fill((128, 128, 128))
        elif state.game.discoloration == 3:
            window.fill((64, 64, 64))
        elif state.game.discoloration == 4:
            window.fill((102, 0, 0))
        elif state.game.discoloration >= 5:
            window.fill((0, 0, 0))

def redraw_window(p=None, white=True, update=True):
    if white == True:
        draw_bg()
    if state.game and p != None:
        if state.game.started == True:
            draw_game_objects(p)
        # if player has not chosen color yet
        check_and_ask_for_color(p)
        check_and_display_waiting_for_players(p)
    if update:
        pygame.display.update()

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
    run = True
    nuke_rendered = False
    nukes_used = 0
    music_set = False

    state.nukes_acquired = 0
    while run:
        clock.tick(60)
        try:
            state.game = network.send("get")
        except Exception as e:
            run = False
            print("Couldn't get game")
            print(e)
            break
        if state.game.started:
            if not music_set and state.sound_enabled:
                pygame.mixer.music.load(assets.papers_please)
                pygame.mixer.music.set_volume(0.1)
                pygame.mixer.music.play(-1)
                music_set = True
            if nukes_used == 7 and state.music_degraded == 0:
                pygame.mixer.music.load(assets.but_nobody_came)
                pygame.mixer.music.set_volume(0.1)
                pygame.mixer.music.play(-1)
                state.music_degraded = 1
            if state.music_degraded == 1:
                # pygame.mixer.music.load(assets.genocide)
                pygame.mixer.music.load(assets.but_nobody_came)
                pygame.mixer.music.set_volume(0.1)
                pygame.mixer.music.play(-1)
                state.music_degraded = 2
        if state.game and state.game.started and not state.nukes_cached:
            cache_initial_nuke_positions()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if state.game.started:
                    if state.game.players[p][2] > 0:
                        buttons["nuke_button"].enable()
                    else:
                        buttons["nuke_button"].disable()
                else:
                    buttons["dice_button"].disable()
                    buttons["nuke_button"].disable()
                for btn in buttons.values():
                    if btn.click(pos):
                        game = network.send(btn.text)
                        print("Clicked:", btn.text)
                        print("Position", state.game.players[p][0])
                        print("Color:", state.game.players[p][1])
                        print("Blocked colors", state.game.blocked_colors)
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

        if nukes_used == state.game.num_nukes_used:
            nuke_rendered = False
        else:
            cache_player_positions()
            nukes_used += 1
            if not nuke_rendered:
                explosion = Explosion(WIDTH / 2, HEIGHT / 2)
                explosion_group.add(explosion)
                if state.sound_enabled:
                    assets.explosion.play()
                nuke_rendered = True
        check_if_player_moving()
        redraw_window(p=p)
        if state.game and state.game.started:
            cache_nukes(p)
        cache_player_positions()
        if state.game.winner != 0:
            redraw_window(p=p, update=False)
            draw_winner_window(p)
            pygame.display.update()
            pygame.time.delay(3000)
            run = False
    del game
    state.nuke_cache.clear()

def cache_nukes(p):
    for player in range(1, state.game.num_of_players + 1):
        if state.nukes_acquired != state.game.nukes_acquired[p] and not state.players_moving[p]:
            for nuke in range(len(state.nuke_cache)):
                if state.game.nukes[nuke] != state.nuke_cache[nuke]:
                    state.nuke_cache[nuke] = state.game.nukes[nuke]
            if state.sound_enabled:
                assets.nuke_get_sounds[random.randint(0, 4)].play()
            state.nukes_acquired += 1
        else:
            for nuke in range(len(state.nuke_cache)):
                if state.game.nukes[nuke] != state.nuke_cache[nuke]:
                    state.nuke_cache[nuke] = state.game.nukes[nuke]


def cache_player_positions():
    for player in range(1, 5):
        if not state.players_moving[player]:
            state.player_movement_started[player] = False
            state.player_position_cache[player] = state.game.players[player][0]

def cache_initial_nuke_positions():
    state.nuke_cache = copy.deepcopy(state.game.nukes)
    state.nukes_cached = True

def check_if_player_moving():
    for player in range(1, 5):
        if state.game.players[player][3]:
            if state.player_position_cache[player] != state.game.players[player][0]:
                state.players_moving[player] = True

def menu_screen():
    run = True
    if state.music_degraded == 0 and state.sound_enabled:
        pygame.mixer.music.stop()
    explosion_easter_egg_counter = 0
    while run:
        clock.tick(60)
        window.blit(assets.TITLE3, (0, 0))
        buttons["start_game_button"].draw()
        buttons["start_game_button"].enable()
        if state.sound_enabled:
            window.blit(assets.UNMUTED, MUTE_BUTTON_LOCATION)
            buttons["mute_button"].enable()
        else:
            window.blit(assets.MUTED, MUTE_BUTTON_LOCATION)
            buttons["unmute_button"].enable()
        explosion_group.draw(window)
        explosion_group.update()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if buttons["start_game_button"].click(pos):
                    buttons["mute_button"].enabled = False
                    buttons["unmute_button"].enabled = False
                    buttons["start_game_button"].enabled = False
                    run = False
                if buttons["mute_button"].click(pos) or buttons["unmute_button"].click(pos):
                    state.sound_enabled = not state.sound_enabled
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
