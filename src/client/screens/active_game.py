import pygame
from .. import load_assets as assets
from ..button import Button
from ..explosion import Explosion
from ..utils import *
from ..constants import *
from ..networking import Network
from ...shared.game import Game

class ActiveGameScreen(ScreenStateInterface):
    def __init__(self, window: pygame.surface.Surface, state: ClientState):
        self.window = window
        self.state = state
        self.buttons: dict[str, Button] = {
            "dice_button": Button(window, state, 'roll', 550, 625, 100, 100, BLACK, WHITE, border_radius=100, sound=assets.dice),
            "nuke_button": Button(window, state, 'NUKE', 295, 615, 130, 130, RED, WHITE, border_radius=50, sound=assets.click),
        }

    @property
    def game(self) -> Game:
        return self.state.game

    @property
    def player(self) -> Player:
        return self.state.player

            #if self.game.started:
            #    if not music_set and self.sound_enabled:
            #        pygame.mixer.music.load(assets.papers_please)
            #        pygame.mixer.music.set_volume(0.1)
            #        pygame.mixer.music.play(-1)
            #        music_set = True
            #    if nukes_used == 7 and self.music_degraded == 0:
            #        pygame.mixer.music.load(assets.but_nobody_came)
            #        pygame.mixer.music.set_volume(0.1)
            #        pygame.mixer.music.play(-1)
            #        self.music_degraded = 1
            #    if self.music_degraded == 1:
            #        # pygame.mixer.music.load(assets.genocide)
            #        pygame.mixer.music.load(assets.but_nobody_came)
            #        pygame.mixer.music.set_volume(0.1)
            #        pygame.mixer.music.play(-1)
            #        self.music_degraded = 2
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and self.state.connected:
            pos = pygame.mouse.get_pos()
            for btn in self.buttons.values():
                if btn.click(pos):
                    self.state.network.send(btn.text)

    def update(self, dt):
        try:
            self.state.game = self.state.network.send("get")
        except Exception:
            print("Couldn't get game, booting back to menu screen")
            pygame.event.post(pygame.event.Event(CHANGE_STATE, {"state": "menu_screen"}))
        self.state.explosion_group.update()

        # Dice
        if self.game.player_to_move == self.player:
            if self.game.deg_dice == 0:
                self.buttons["dice_button"].image = assets.DICE[self.game.dice_pips]
            else:
                self.buttons["dice_button"].image = assets.DICEDEG[self.game.dice_pips]
            self.buttons["dice_button"].enable()
        else:
            self.buttons["dice_button"].disable()

    def draw(self):
        # a box on the board is 46x47 pixels at 750x750 resolution
        # moving x or y means change by 51 pixels in that direction
        draw_bg(self.window, self.state)
        self.window.blit(assets.BOARD[self.game.deg_board], (WIDTH / 2 - assets.BOARD1.get_width() / 2, 30))

        # Game pieces
        for nuke in self.game.nukes:
            self.window.blit(assets.NUCLEARBOMB, (125 + (nuke.x * 51), 522 - (nuke.y * 51)))

        # UI
        for btn in self.buttons.values():
            btn.draw()
        if not self.game.deg_color:
            self.window.blit(assets.BIGGERPIECES[self.game.player_to_move.color.text], (5, 5))
        else:
            self.window.blit(assets.BIGGERPIECESDEG[self.game.player_to_move.color.text], (5, 5))
        # Nuke icon (not button)
        if self.player.nukes > 0:
            self.window.blit(assets.NUKEACTIVE, (15, 635))
        else:
            self.window.blit(assets.NUKEINACTIVE, (15, 635))
        if not self.game.deg_nuke_text:
            text = FONTS[120].render(str(self.player.nukes), True, RED.color)
            self.window.blit(text, (90, 620))
        else:
            text = DEG_NUKE_FONT.render(str(self.player.nukes), True, RED.color)
            self.window.blit(text, (90, 600))

        self.state.explosion_group.draw(self.window)


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
        if self.game.deg_pieces == 0:
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

    def draw_snakes_and_ladders(self):
        if self.game.deg_snakes_and_ladders == 0:
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
                if self.game.deg_music == 0:
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
                if self.game.deg_music == 0:
                    pygame.mixer.music.stop()
        blit_centered_text(window, text, y_offset=-325)
