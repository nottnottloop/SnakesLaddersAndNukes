import pygame
import random
from .. import load_assets as assets
from ..button import Button
from ..explosion import Explosion
from ..utils import *
from ..constants import *
from ..networking import Network
from ...shared import game_pb2
from ...shared.game_pb2 import Player

class ActiveGameScreen(ScreenStateInterface):
    def __init__(self, window: pygame.surface.Surface, state: ClientState):
        self.window = window
        self.state: ClientState = state
        self.buttons: dict[str, Button] = {
            "dice_button": Button(window, state, 'roll', 550, 625, 100, 100, BLACK.color, WHITE.color, border_radius=100, sound=None),
            "nuke_button": Button(window, state, 'NUKE', 295, 615, 130, 130, RED.color, WHITE.color, border_radius=50, border_width=3),
        }
        self.explosion_group = pygame.sprite.Group()
        self.player_to_move: Player = None
        self.winner: Player = None
        self.client_event: str = "get"

    @property
    def game(self) -> game_pb2:
        return self.state.game

    @property
    def player(self):
        return self.game.players[self.state.player_id]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if not self.winner:
                for btn in self.buttons.values():
                    if btn.click(pos):
                        self.client_event = btn.text
        elif event.type == pygame.KEYDOWN:
            if not self.winner:
                if event.scancode == pygame.KSCAN_R:
                    self.client_event = self.buttons["dice_button"].text
                    self.buttons["dice_button"].play_button_sound()
                elif event.scancode == pygame.KSCAN_N:
                    self.client_event = self.buttons["nuke_button"].text
                    if self.player.nukes > 0:
                        self.buttons["nuke_button"].play_button_sound()
            # Debug
            if event.scancode == pygame.KSCAN_UP or event.scancode == pygame.KSCAN_W:
                self.client_event = "Up"
            elif event.scancode == pygame.KSCAN_DOWN or event.scancode == pygame.KSCAN_S:
                self.client_event = "Down"
            elif event.scancode == pygame.KSCAN_RIGHT or event.scancode == pygame.KSCAN_D:
                self.client_event = "Right"
            elif event.scancode == pygame.KSCAN_LEFT or event.scancode == pygame.KSCAN_A:
                self.client_event = "Left"
            elif event.scancode == pygame.KSCAN_K:
                self.client_event = "generate_objects"
            elif event.scancode == pygame.KSCAN_J:
                self.client_event = "reset_deg"
        elif event.type == WINNER:
            pygame.time.set_timer(WINNER, 0)
            pygame.event.post(pygame.event.Event(CHANGE_STATE, {"state": "menu_screen"}))

    def update(self, dt):
        try:
            self.state.game = self.state.network.send(self.client_event)
            self.client_event = "get"
        except Exception:
            print("Couldn't get game, booting back to menu screen")
            pygame.event.post(pygame.event.Event(CHANGE_STATE, {"state": "menu_screen"}))
        
        self.state.server_events.extend(self.game.events)
        self.player_to_move = self.game.players[self.game.player_to_move_id]
        self.winner = self.game.players.get(self.game.winner_id)

        # Debug
        keys = pygame.key.get_pressed()
        if keys[pygame.key.key_code("l")]:
            self.state.network.send("generate_objects")
        
        self.explosion_group.update()

        while self.state.server_events:
            event = self.state.server_events.pop()
            if event == "winner":
                pygame.time.set_timer(WINNER, 5000)
                pygame.mixer.music.stop()
                if self.game.nukes_used == 0:
                    self.state.play_sound(assets.sound_pacifistwin)
                else:
                    self.state.play_sound(assets.sound_nukewin)
            elif event == "dice_rolled":
                self.state.play_sound(assets.sound_dice)
            elif event == "snake":
                self.state.play_sound(assets.sound_snake)
            elif event == "ladder":
                self.state.play_sound(assets.sound_ladder)
            elif event == "nuke_collected":
                self.state.play_sound(assets.nuke_get_sounds[random.randint(0, len(assets.nuke_get_sounds) - 1)])
            elif event == "nuke_used":
                self.state.play_sound(assets.sound_explosion)
                self.explosion_group.add(Explosion())
            elif event == "papers_please":
                self.state.play_music(assets.music_papers_please)
            elif event == "but_nobody_came":
                self.state.play_music(assets.music_but_nobody_came)
            elif event == "genocide":
                self.state.play_music(assets.music_genocide)

        # Dice
        if self.player_to_move == self.player:
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

        # UI
        for btn in self.buttons.values():
            btn.draw()

        # Movables
        for movable in self.game.movables:
            movable_draw_data = MOVABLE_DRAW_DATA[movable.sprite]
            if not self.game.deg_snakes_and_ladders:
                movable_sprite_to_draw = movable_draw_data.regular_sprite
            else:
                movable_sprite_to_draw = movable_draw_data.deg_sprite
            self.window.blit(movable_sprite_to_draw, (117 + (movable.position.x * 51) + movable_draw_data.offset.x, 517 - (movable.position.y * 51) + movable_draw_data.offset.y))

        # Player pieces
        for i, player in enumerate(self.game.players.values()):
            # nudge each of the player tokens to prevent overlapping
            offset_nudge = i * 5
            player_color = ENUM_TO_COLOR_OBJECT_MAP[player.color].text
            if self.game.deg_pieces == 0:
                self.window.blit(assets.PIECES[player_color], (BOARD_START_X + player.position.x * SQUARE_SIZE + offset_nudge + self.state.shake_amount, BOARD_START_Y - player.position.y * SQUARE_SIZE + offset_nudge))
            else:
                self.window.blit(assets.PIECESDEG[player_color], (BOARD_START_X + player.position.x * SQUARE_SIZE + offset_nudge + self.state.shake_amount, BOARD_START_Y - player.position.y * SQUARE_SIZE + offset_nudge))

        player_to_move_color = ENUM_TO_COLOR_OBJECT_MAP[self.player_to_move.color].text
        if not self.game.deg_pieces:
            self.window.blit(assets.BIGGERPIECES[player_to_move_color], (5, 5))
        else:
            self.window.blit(assets.BIGGERPIECESDEG[player_to_move_color], (5, 5))

        # Nukes
        for nuke in self.game.nukes:
            self.window.blit(assets.NUCLEARBOMB, (125 + (nuke.position.x * 51), 522 - (nuke.position.y * 51)))


        # Nuke icon and counter
        if self.player.nukes > 0:
            self.window.blit(assets.NUKEACTIVE, (15, 635))
        else:
            self.window.blit(assets.NUKEINACTIVE, (15, 635))
        if self.player.nukes > 0:
            if not self.game.deg_nuke_text:
                text = FONTS[120].render(str(self.player.nukes), True, RED.color)
                self.window.blit(text, (80, 615))
            else:
                text = DEG_NUKE_FONT.render(str(self.player.nukes), True, RED.color)
                self.window.blit(text, (80, 615))

        # Winner text
        if self.winner:
            winner_name = ENUM_TO_COLOR_OBJECT_MAP[self.winner.color].text
            winner_color = ENUM_TO_COLOR_OBJECT_MAP[self.winner.color].color
            if self.winner == self.player:
                if self.game.nukes_used == 0:
                    text = FONTS[90].render("YOU WON! :D", True, winner_color, WHITE.color)
                else:
                    text = FONTS[90].render("You won...", True, winner_color, BLACK.color)
            else:
                if self.game.nukes_used == 0:
                    text = FONTS[90].render(f"{winner_name} WON! :)", True, winner_color, WHITE.color)
                else:
                    text = FONTS[90].render(f"{winner_name} won...", True, winner_color, BLACK.color)
            blit_centered_text(self.window, text, y_offset=-325)

        self.explosion_group.draw(self.window)
