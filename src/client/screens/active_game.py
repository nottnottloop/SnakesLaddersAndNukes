import pygame
from .. import load_assets as assets
from ..button import Button
from ..explosion import Explosion
from ..utils import *
from ..constants import *
from ..networking import Network
from ...shared.game import Game

NUKE_ICON_LOCATION = (15, 635)
MOVE_TURN_ICON_LOCATION = (5, 5)

class ActiveGameScreen(ScreenStateInterface):
    def __init__(self, window: pygame.surface.Surface, state: Game):
        self.window = window
        self.state = state
        self.game = self.game
        buttons = {
            "dice_button": Button(self.window, self.state, 'roll', 550, 625, 100, 100, BLACK, WHITE, border_radius=100, sound=assets.dice),
            "nuke_button": Button(self.window, self.state, 'NUKE', 295, 615, 130, 130, RED, WHITE, border_radius=50, sound=assets.click),
        }
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and self.state.connected:
            pos = pygame.mouse.get_pos()
            for btn in self.buttons.values():
                if btn.click(pos):
                    self.state.network.send(btn.text)
    def update(self, dt):
    def draw(self):

    # nudge each of the player tokens to prevent overlapping
    def calculate_offset_nudge(self, player):
        return (player - 1) * 5

    def draw_stationary_pieces(self, player):
        # if shake_direction true, move right
        x_offset, y_offset = self.game.players[player][0][0], self.game.players[player][0][1]
        offset_nudge = calculate_offset_nudge(player)
        if self.game.piece_shake == 1:
            if shake_direction:
                shake_amount += 1
                if shake_amount == 5:
                    shake_direction = not shake_direction
            if not shake_direction:
                shake_amount -= 1
                if shake_amount == -5:
                    shake_direction = not shake_direction
        if self.game.pieces_degraded == 0:
            window.blit(assets.PIECES[self.game.players[player][1]],
                    (BOARD_START_X + x_offset * SQUARE_SIZE + offset_nudge + self.shake_amount,
                    BOARD_START_Y - y_offset * SQUARE_SIZE + offset_nudge))
        else:
            window.blit(assets.PIECESDEG[self.game.players[player][1]],
                    (BOARD_START_X + x_offset * SQUARE_SIZE + offset_nudge + self.shake_amount,
                    BOARD_START_Y - y_offset * SQUARE_SIZE + offset_nudge))

    def draw_game_pieces(self, p):
        for player in range(1, 5):
            if self.game.players[player][3] == True:
                draw_stationary_pieces(player)
                if self.players_moving[player] and not self.player_movement_started[player] and not self.game.nuke_used:
                    play_movement_animation(player, calculate_offset_nudge(player), p)


    def play_movement_animation(self, player, offset_nudge, p):
        # destination is self.game.players[player][0][0]
        # old position is player_position_cache
        ticks_passed = 0
        if self.game.player_travelled_on_movable[player]:
            # print("travelled on movable")
            # print(self.game.players_previous_space[player])
            loop_completed = False
            old_x, old_y = self.player_position_cache[player][0], self.player_position_cache[player][1]
            new_x, new_y = self.game.players_previous_space[player][0], self.game.players_previous_space[player][1]
            distance_x, distance_y = new_x - old_x, new_y - old_y
        else:
            # print("didn't")
            # print(self.game.players_previous_space[player])
            loop_completed = True
            old_x, old_y = self.player_position_cache[player][0], self.player_position_cache[player][1]
            new_x, new_y = self.game.players[player][0][0], self.game.players[player][0][1]
            distance_x, distance_y = new_x - old_x, new_y - old_y
        while self.players_moving[player]:
            self.player_movement_started[player] = True
            ticks_passed += 1
            draw_bg(window, state)
            draw_board()
            draw_dice(p)
            draw_nuke_buttons(p)
            draw_move_icon()
            draw_snakes_and_ladders()
            for hypothetical_stationary_player in range(1, 5):
                if self.game.players[hypothetical_stationary_player][1] != None:
                    if hypothetical_stationary_player != player:
                        draw_stationary_pieces(hypothetical_stationary_player)
            draw_nukes()
            if self.game.pieces_degraded == 0:
                window.blit(assets.PIECES[self.game.players[player][1]],
                        (BOARD_START_X + old_x * SQUARE_SIZE + 0.85 * ticks_passed * distance_x + offset_nudge,
                        BOARD_START_Y - old_y * SQUARE_SIZE - 0.85 * ticks_passed * distance_y + offset_nudge))
            else:
                window.blit(assets.PIECESDEG[self.game.players[player][1]],
                        (BOARD_START_X + old_x * SQUARE_SIZE + 0.85 * ticks_passed * distance_x + offset_nudge,
                        BOARD_START_Y - old_y * SQUARE_SIZE - 0.85 * ticks_passed * distance_y + offset_nudge))
            explosion_group.draw(window)
            explosion_group.update()
            pygame.display.update()
            if not loop_completed and ticks_passed == 60:
                cache_nukes(p)
                old_x, old_y = self.game.players_previous_space[player][0], self.game.players_previous_space[player][1]
                new_x, new_y = self.game.players[player][0][0], self.game.players[player][0][1]
                distance_x, distance_y = new_x - old_x, new_y - old_y
                ticks_passed = 0
                loop_completed = True
            if ticks_passed == 60 and loop_completed:
                self.players_moving[player] = False

    def draw_snakes_and_ladders(self):
        if self.game.snakes_and_ladders_degraded == 0:
            for snake in range(3, -1, -1):
                # y_offset, x_offset = calculate_offset(self.game.snakes[snake][0])
                # if self.game.snakes[snake][3] == True:
                #     x_offset += x_offset
                if snake == 0:
                    window.blit(assets.SNAKE1,
                            (117 + (self.game.snakes[snake][0][0] * 51) - 19, 517 - (self.game.snakes[snake][0][1] * 51) + 33))
                if snake == 1:
                    window.blit(assets.SNAKE2,
                            (117 + (self.game.snakes[snake][0][0] * 51) - 65, 517 - (self.game.snakes[snake][0][1] * 51) + 23))
                if snake == 2:
                    window.blit(assets.SNAKE3,
                            (117 + (self.game.snakes[snake][0][0] * 51) + 10, 517 - (self.game.snakes[snake][0][1] * 51) + 20))
                if snake == 3:
                    window.blit(assets.SNAKE4,
                            (117 + (self.game.snakes[snake][0][0] * 51) , 517 - (self.game.snakes[snake][0][1] * 51) + 28))
            for ladder in range (3, -1, -1):
                if ladder == 0:
                    window.blit(assets.LADDER1,
                            (117 + (self.game.ladders[ladder][0][0] * 51) + 15, 517 - (self.game.ladders[ladder][0][1] * 51) - 148))
                if ladder == 1:
                    window.blit(assets.LADDER2,
                            (117 + (self.game.ladders[ladder][0][0] * 51) + 15, 517 - (self.game.ladders[ladder][0][1] * 51) - 79))
                if ladder == 2:
                    window.blit(assets.LADDER3,
                            (117 + (self.game.ladders[ladder][0][0] * 51) - 41, 517 - (self.game.ladders[ladder][0][1] * 51) - 67))
                if ladder == 3:
                    window.blit(assets.LADDER4,
                            (117 + (self.game.ladders[ladder][0][0] * 51) - 17, 517 - (self.game.ladders[ladder][0][1] * 51) - 240))
        else:
            for snake in range(3, -1, -1):
                if snake == 0:
                    window.blit(assets.SNAKE1DEG,
                            (117 + (self.game.snakes[snake][0][0] * 51) - 19, 517 - (self.game.snakes[snake][0][1] * 51) + 33))
                if snake == 1:
                    window.blit(assets.SNAKE2DEG,
                            (117 + (self.game.snakes[snake][0][0] * 51) - 65, 517 - (self.game.snakes[snake][0][1] * 51) + 23))
                if snake == 2:
                    window.blit(assets.SNAKE3DEG,
                            (117 + (self.game.snakes[snake][0][0] * 51) + 10, 517 - (self.game.snakes[snake][0][1] * 51) + 20))
                if snake == 3:
                    window.blit(assets.SNAKE4DEG,
                            (117 + (self.game.snakes[snake][0][0] * 51) , 517 - (self.game.snakes[snake][0][1] * 51) + 28))
            for ladder in range (3, -1, -1):
                if ladder == 0:
                    window.blit(assets.LADDER1,
                            (117 + (self.game.ladders[ladder][0][0] * 51) + 15, 517 - (self.game.ladders[ladder][0][1] * 51) - 148))
                if ladder == 1:
                    window.blit(assets.LADDER2DEG,
                            (117 + (self.game.ladders[ladder][0][0] * 51) + 15, 517 - (self.game.ladders[ladder][0][1] * 51) - 79))
                if ladder == 2:
                    window.blit(assets.LADDER3,
                            (117 + (self.game.ladders[ladder][0][0] * 51) - 41, 517 - (self.game.ladders[ladder][0][1] * 51) - 67))
                if ladder == 3:
                    window.blit(assets.LADDER4DEG,
                            (117 + (self.game.ladders[ladder][0][0] * 51) - 17, 517 - (self.game.ladders[ladder][0][1] * 51) - 240))

    def draw_nukes(self):
        for nuke in (range(len(self.nuke_cache))):
            window.blit(assets.NUCLEARBOMB,
                    (125 + (self.nuke_cache[nuke][0] * 51), 522 - (self.nuke_cache[nuke][1] * 51)))

    def draw_nuke_buttons(self, p):
        if self.game.players[p][2] == 0:
            window.blit(assets.NUKEINACTIVE, NUKE_ICON_LOCATION)
        else:
            window.blit(assets.NUKEACTIVE, NUKE_ICON_LOCATION)
            if self.game.degraded_nuke_text == 0:
                font = pygame.font.SysFont("consolas", 120)
                text = font.render(str(self.game.players[p][2]), True, RED)
                window.blit(text, (90, 620))
            else:
                font = pygame.font.SysFont("impact", 120)
                text = font.render(str(self.game.players[p][2]), True, RED)
                window.blit(text, (90, 600))
            buttons["nuke_button"].draw()

    def draw_dice(self, p):
        if self.game.player_to_move == p:
            buttons["dice_button"].enable()
        else:
            buttons["dice_button"].disable()
        buttons["dice_button"].draw()
        if self.game.dice_degraded == 0:
            window.blit(assets.DICE[self.game.dice_pips], (550, 625))
        else:
            window.blit(assets.DICEDEG[self.game.dice_pips], (550, 625))

    def draw_move_icon(self):
        for player in range(1, len(self.game.players)):
            if player == self.game.player_to_move and self.game.pieces_degraded == 0:
                if self.game.players[player][1] == "Red":
                    window.blit(assets.BIGGERPIECERED, MOVE_TURN_ICON_LOCATION)
                if self.game.players[player][1] == "Green":
                    window.blit(assets.BIGGERPIECEGREEN, MOVE_TURN_ICON_LOCATION)
                if self.game.players[player][1] == "Blue":
                    window.blit(assets.BIGGERPIECEBLUE, MOVE_TURN_ICON_LOCATION)
                if self.game.players[player][1] == "Yellow":
                    window.blit(assets.BIGGERPIECEYELLOW, MOVE_TURN_ICON_LOCATION)
            elif player == self.game.player_to_move and self.game.pieces_degraded == 1:
                if self.game.players[player][1] == "Red":
                    window.blit(assets.BIGGERPIECEREDDEG, MOVE_TURN_ICON_LOCATION)
                if self.game.players[player][1] == "Green":
                    window.blit(assets.BIGGERPIECEGREENDEG, MOVE_TURN_ICON_LOCATION)
                if self.game.players[player][1] == "Blue":
                    window.blit(assets.BIGGERPIECEBLUEDEG, MOVE_TURN_ICON_LOCATION)
                if self.game.players[player][1] == "Yellow":
                    window.blit(assets.BIGGERPIECEYELLOWDEG, MOVE_TURN_ICON_LOCATION)

    def draw_board(self):
        window.blit(assets.BOARD[self.game.board], (WIDTH / 2 - assets.BOARD1.get_width() / 2, 30))

    def draw_winner_window(self, p):
        font = pygame.font.SysFont("consolas", 70, bold=True)
        text = font.render("ERROR", True, parse_color(self.game.players[self.game.winner][1]))
        if self.game.winner == p:
            if self.game.num_nukes_used == 0:
                text = font.render("YOU WON! :D", True, parse_color(self.game.players[self.game.winner][1]))
                if self.sound_enabled:
                    assets.pacifistwin.play()
                pygame.mixer.music.stop()
            if self.game.num_nukes_used >= 1:
                text = font.render("You won...", True, parse_color(self.game.players[self.game.winner][1]))
                if self.sound_enabled:
                    assets.nukewin.play()
                if self.music_degraded == 0:
                    pygame.mixer.music.stop()
        else:
            if self.game.num_nukes_used == 0:
                text = font.render(self.game.players[self.game.winner][1].upper() + " WON! :)", True, parse_color(self.game.players[self.game.winner][1]))
                if self.sound_enabled:
                    assets.pacifistwin.play()
                pygame.mixer.music.stop()
            if self.game.num_nukes_used >= 1:
                text = font.render(self.game.players[self.game.winner][1] + " won...", True, parse_color(self.game.players[self.game.winner][1]))
                if self.sound_enabled:
                    assets.nukewin.play()
                if self.music_degraded == 0:
                    pygame.mixer.music.stop()
        blit_centered_text(window, text, y_offset=-325)

    def draw_game_objects(self, p=None, player_position_cache=None):
        # a box on the board is 46x47 pixels at 750x750 resolution
        # moving x or y means change by 51 pixels in that direction
        # def calculate_offset(position):
        #     y_offset = position // 10
        #     x_offset = position % 10
        #     if y_offset % 2 != 0:
        #         x_offset = 9 - x_offset
        #     return y_offset, x_offset
        if self.game.started:
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

        self.nukes_acquired = 0
        while run:
            clock.tick(60)
            try:
                self.game = network.send("get")
            except Exception as e:
                run = False
                print("Couldn't get game")
                print(e)
                break
            if self.game.started:
                if not music_set and self.sound_enabled:
                    pygame.mixer.music.load(assets.papers_please)
                    pygame.mixer.music.set_volume(0.1)
                    pygame.mixer.music.play(-1)
                    music_set = True
                if nukes_used == 7 and self.music_degraded == 0:
                    pygame.mixer.music.load(assets.but_nobody_came)
                    pygame.mixer.music.set_volume(0.1)
                    pygame.mixer.music.play(-1)
                    self.music_degraded = 1
                if self.music_degraded == 1:
                    # pygame.mixer.music.load(assets.genocide)
                    pygame.mixer.music.load(assets.but_nobody_came)
                    pygame.mixer.music.set_volume(0.1)
                    pygame.mixer.music.play(-1)
                    self.music_degraded = 2
            if self.game and self.game.started and not self.nukes_cached:
                cache_initial_nuke_positions()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if self.game.started:
                        if self.game.players[p][2] > 0:
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
                            print("Position", self.game.players[p][0])
                            print("Color:", self.game.players[p][1])
                            print("Blocked colors", self.game.blocked_colors)
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

            if nukes_used == self.game.num_nukes_used:
                nuke_rendered = False
            else:
                cache_player_positions()
                nukes_used += 1
                if not nuke_rendered:
                    explosion = Explosion(WIDTH / 2, HEIGHT / 2)
                    explosion_group.add(explosion)
                    if self.sound_enabled:
                        assets.explosion.play()
                    nuke_rendered = True
            check_if_player_moving()
            redraw_window(p=p)
            if self.game and self.game.started:
                cache_nukes(p)
            cache_player_positions()
            if self.game.winner != 0:
                redraw_window(p=p, update=False)
                draw_winner_window(p)
                pygame.display.update()
                pygame.time.delay(3000)
                run = False
        del game
        self.nuke_cache.clear()

    def cache_nukes(self, p):
        for player in range(1, self.game.num_of_players + 1):
            if self.nukes_acquired != self.game.nukes_acquired[p] and not self.players_moving[p]:
                for nuke in range(len(self.nuke_cache)):
                    if self.game.nukes[nuke] != self.nuke_cache[nuke]:
                        self.nuke_cache[nuke] = self.game.nukes[nuke]
                if self.sound_enabled:
                    assets.nuke_get_sounds[random.randint(0, 4)].play()
                self.nukes_acquired += 1
            else:
                for nuke in range(len(self.nuke_cache)):
                    if self.game.nukes[nuke] != self.nuke_cache[nuke]:
                        self.nuke_cache[nuke] = self.game.nukes[nuke]


    def cache_player_positions(self):
        for player in range(1, 5):
            if not self.players_moving[player]:
                self.player_movement_started[player] = False
                self.player_position_cache[player] = self.game.players[player][0]

    def cache_initial_nuke_positions(self):
        self.nuke_cache = copy.deepcopy(self.game.nukes)
        self.nukes_cached = True

    def check_if_player_moving(self):
        for player in range(1, 5):
            if self.game.players[player][3]:
                if self.player_position_cache[player] != self.game.players[player][0]:
                    self.players_moving[player] = True
