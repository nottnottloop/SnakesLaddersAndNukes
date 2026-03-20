import pygame
import random
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
            "dice_button": Button(window, state, 'roll', 550, 625, 100, 100, BLACK.color, WHITE.color, border_radius=100, sound=assets.sound_dice),
            "nuke_button": Button(window, state, 'NUKE', 295, 615, 130, 130, RED.color, WHITE.color, border_radius=50),
        }
        self.explosion_group = pygame.sprite.Group()
        self.started_music = False

    @property
    def game(self) -> Game:
        return self.state.game

    @property
    def player(self) -> Player:
        return self.state.player

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            for btn in self.buttons.values():
                if btn.click(pos):
                    self.state.network.send(btn.text)
        elif event.type == WINNER:
            pygame.time.set_timer(WINNER, 0)
            pygame.event.post(pygame.event.Event(CHANGE_STATE, {"state": "menu_screen"}))

    def update(self, dt):
        try:
            self.state.game = self.state.network.send("get")
        except Exception:
            print("Couldn't get game, booting back to menu screen")
            pygame.event.post(pygame.event.Event(CHANGE_STATE, {"state": "menu_screen"}))
        
        self.explosion_group.update()

        for event in self.game.events:
            if event == "winner":
                pygame.time.set_timer(WINNER, 5000)
                if self.game.nukes_used == 0:
                    self.state.play_sound(assets.sound_pacifistwin)
                else:
                    self.state.play_sound(assets.sound_nukewin)
                pygame.mixer.music.stop()
            elif event == "nuke_collected":
                self.state.play_sound(assets.nuke_get_sounds[random.randint(0, len(assets.nuke_get_sounds)) - 1])
            elif event == "nuke_used":
                self.state.play_sound(assets.sound_explosion)
                self.explosion_group.add(Explosion())
            elif event == "snake":
                self.state.play_sound(assets.sound_snake)
            elif event == "ladder":
                self.state.play_sound(assets.sound_ladder)
            elif event == "music_change":
                self.state.play_music(assets.music_but_nobody_came)

        if not self.started_music:
            self.state.play_music(assets.music_papers_please)
            self.started_music = True

        # Dice
        if self.game.player_to_move == self.player:
            if self.game.deg_dice == 0:
                self.buttons["dice_button"].image = assets.DICE[self.game.dice_pips]
            else:
                self.buttons["dice_button"].image = assets.DICEDEG[self.game.dice_pips]
            self.buttons["dice_button"].enable()
        else:
            self.buttons["dice_button"].disable()

        # Nuke Button
        if self.player.nukes > 0:
            self.buttons["nuke_button"].enable()
        else:
            self.buttons["nuke_button"].disable()
        
        # Pieces
        if self.game.deg_piece_shake:
            if self.state.shake_direction:
                self.state.shake_amount += 1
            else:
                self.state.shake_amount -= 1
            if abs(self.state.shake_amount) == 5:
                self.state.shake_direction = not self.state.shake_direction

    def draw(self):
        # a box on the board is 46x47 pixels at 750x750 resolution
        # moving x or y means change by 51 pixels in that direction
        draw_bg(self.window, self.state)
        self.window.blit(assets.BOARD[self.game.deg_board], (WIDTH / 2 - assets.BOARD1.get_width() / 2, 30))

        # Game pieces
        for nuke in self.game.nukes:
            self.window.blit(assets.NUCLEARBOMB, (125 + (nuke.x * 51), 522 - (nuke.y * 51)))

        for movable in self.game.movables:
            movable_draw_data = MOVABLE_DRAW_DATA[movable.sprite]
            if not self.game.deg_snakes_and_ladders:
                movable_sprite_to_draw = movable_draw_data.regular_sprite
            else:
                movable_sprite_to_draw = movable_draw_data.deg_sprite
            self.window.blit(movable_sprite_to_draw, (117 + (movable.position.x * 51) + movable_draw_data.offset.x, 517 - (movable.position.y * 51) + movable_draw_data.offset.y))

        for i, player in enumerate(self.game.players.values()):
            # nudge each of the player tokens to prevent overlapping
            offset_nudge = i * 5
            if self.game.deg_pieces == 0:
                self.window.blit(assets.PIECES[player.color.text], (BOARD_START_X + player.position.x * SQUARE_SIZE + offset_nudge + self.state.shake_amount, BOARD_START_Y - player.position.y * SQUARE_SIZE + offset_nudge))
            else:
                self.window.blit(assets.PIECESDEG[player.color.text], (BOARD_START_X + player.position.x * SQUARE_SIZE + offset_nudge + self.state.shake_amount, BOARD_START_Y - player.position.y * SQUARE_SIZE + offset_nudge))

        # UI
        for btn in self.buttons.values():
            btn.draw()
        if not self.game.deg_pieces:
            self.window.blit(assets.BIGGERPIECES[self.game.player_to_move.color.text], (5, 5))
        else:
            self.window.blit(assets.BIGGERPIECESDEG[self.game.player_to_move.color.text], (5, 5))
        # Nuke icon (not button)
        if self.player.nukes > 0:
            self.window.blit(assets.NUKEACTIVE, (15, 635))
        else:
            self.window.blit(assets.NUKEINACTIVE, (15, 635))
        if self.player.nukes > 0:
            if not self.game.deg_nuke_text:
                text = FONTS[120].render(str(self.player.nukes), True, RED.color)
                self.window.blit(text, (90, 620))
            else:
                text = DEG_NUKE_FONT.render(str(self.player.nukes), True, RED.color)
                self.window.blit(text, (90, 600))

        if self.game.winner:
            text = FONTS[90].render("ERROR", True, self.game.winner.color.color)
            if self.game.winner == self.player:
                if self.game.nukes_used == 0:
                    text = FONTS[90].render("YOU WON! :D", True, self.game.winner.color.color)
                else:
                    text = FONTS[90].render("You won...", True, self.game.winner.color.color)
            else:
                if self.game.num_nukes_used == 0:
                    text = FONTS[90].render(f"{self.game.winner} WON! :)", True, self.game.winner.color.color)
                else:
                    text = FONTS[90].render(f"{self.game.winner} won...", True, self.game.winner.color.color)
            blit_centered_text(self.window, text, y_offset=-325)

        self.explosion_group.draw(self.window)
