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

from .screens.main_menu import MenuScreen

pygame.font.init()
pygame.display.set_icon(assets.ICON)
pygame.display.set_caption("Snakes, Ladders and Nukes")

window: pygame.surface.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
state = ClientState()
menu_screen = MenuScreen(window, state)
state.screen_state = menu_screen

NUKE_ICON_LOCATION = (15, 635)
MOVE_TURN_ICON_LOCATION = (5, 5)

buttons = {
    "dice_button": Button(window, state, 'roll', 550, 625, 100, 100, BLACK, WHITE, border_radius=100, sound=assets.dice),
    "nuke_button": Button(window, state, 'NUKE', 295, 615, 130, 130, RED, WHITE, border_radius=50, sound=assets.click),
}

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
        draw_bg(window, state)
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

#window.fill(WHITE)
#font = pygame.font.SysFont("consolas", 60)
#text = font.render("LOADING", True, BLACK)
#blit_centered_text(window, text)
#pygame.display.update()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            state.screen_state.handle_event(event)
    dt = state.clock.tick(60)
    state.screen_state.update(dt)
    state.screen_state.draw()
    pygame.display.flip()
