import pygame
from src.shared.constants import *
from ..constants import *
from .. import load_assets as assets
from ..button import Button
from ..utils import *
from ...shared.game_pb2 import Player, Game

class PlayerSelectScreen(ScreenStateInterface):
    def __init__(self, window: pygame.surface.Surface, state: ClientState):
        self.window = window
        self.state = state
        self.connection_tried = False
        self.connection_failed = False
        self.color_buttons: dict[str, Button] = {
            "red": Button(window, state, 'Red', 375, 175, 200, 200, RED.color, RED.color, enabled=True),
            "green": Button(window, state, 'Green', 375, 375, 200, 200, GREEN.color, GREEN.color, enabled=True),
            "blue": Button(window, state, 'Blue', 175, 175, 200, 200, BLUE.color, BLUE.color, enabled=True),
            "yellow": Button(window, state, 'Yellow', 175, 375, 200, 200, YELLOW.color, YELLOW.color, enabled=True),
        }
        self.lobby_buttons: dict[str, Button] = {
            "ready_up_button": Button(window, state, 'Ready Up', 125, 575, 500, 150, BLACK.color, WHITE.color),
            "cycle_game_mode": Button(window, state, 'Normal', 225, 400, 300, 150, BLACK.color, WHITE.color, font_size=50, data="cycle_game_mode", border_width=3),
            "debug_toggle": Button(window, state, 'debug', 10, 10, 125, 25, WHITE.color, WHITE.color, enabled=True, sound=None),
        }
        self.buttons: dict[str, Button] = self.color_buttons | self.lobby_buttons
        self.client_event: str = "get"
    
    @property
    def game(self) -> Game:
        return self.state.game

    @property
    def player(self) -> Player:
        return self.game.players[self.state.player_id]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            for btn in self.buttons.values():
                if btn.click(pos):
                    self.client_event = btn.data
        elif event.type == FAILED_TO_CONNECT_TIMER:
            pygame.time.set_timer(FAILED_TO_CONNECT_TIMER, 0)
            pygame.event.post(pygame.event.Event(CHANGE_STATE, {"state": "menu_screen"}))

    def update(self, dt):
        if not self.connection_tried and not self.connection_failed:
            try:
                self.connection_tried = True
                self.state.network.connect()
                self.state.game = self.state.network.send(self.client_event)
            except Exception:
                self.connection_failed = True
                pygame.time.set_timer(FAILED_TO_CONNECT_TIMER, 1000)
            else:
                self.state.player_id = sorted(list(self.game.players.keys()))[-1]
                print(f"Player ID {self.state.player_id}")

        if self.connection_tried and not self.connection_failed:
            self.state.game.CopyFrom(self.state.network.send(self.client_event))
            self.client_event = "get"
            self.state.get_new_events()
            for event in self.state.server_events:
                if event == "debug":
                    self.state.server_events.remove("debug")
                    if self.game.debug:
                        self.state.play_sound(assets.sound_debug_enable)
                        self.lobby_buttons["debug_toggle"].text_color = RED.color
                    else:
                        self.state.play_sound(assets.sound_debug_disable)
                        self.lobby_buttons["debug_toggle"].text_color = WHITE.color
                else:
                    self.state.jukebox(event)
        
            if not self.player.color:
                for btn in self.color_buttons.values():
                    if TEXT_TO_ENUM_COLOR_MAP[btn.text] in self.game.taken_colors:
                        btn.disable()
                    else:
                        btn.enable()
            else:
                [color_button.disable() for color_button in self.color_buttons.values()]
                self.buttons["cycle_game_mode"].enable()

                if self.game.game_mode == "Normal":
                    self.buttons["cycle_game_mode"].text_color = BLACK.color
                    self.buttons["cycle_game_mode"].color = WHITE.color
                    self.buttons["cycle_game_mode"].border_color = BLACK.color
                elif self.game.game_mode == "Peaceful":
                    self.buttons["cycle_game_mode"].text_color = WHITE.color
                    self.buttons["cycle_game_mode"].color = GREEN.color
                    self.buttons["cycle_game_mode"].border_color = BLACK.color
                elif self.game.game_mode == "WW3":
                    self.buttons["cycle_game_mode"].text_color = WHITE.color
                    self.buttons["cycle_game_mode"].color = RED.color
                    self.buttons["cycle_game_mode"].border_color = NUKE_ORANGE.color
                self.buttons["cycle_game_mode"].text = self.game.game_mode


                if self.player.ready:
                    self.buttons["ready_up_button"].disable()
                else:
                    self.buttons["ready_up_button"].enable()

                if len(self.game.players) == 1:
                    self.buttons["ready_up_button"].text = "Play Single Player"
                else:
                    self.buttons["ready_up_button"].text = "Ready Up"

            if self.game.started:
                pygame.event.post(pygame.event.Event(CHANGE_STATE, {"state": "active_game"}))

    def draw(self):
        draw_bg(self.window, self.state)
        if not self.connection_tried and not self.connection_failed:
            self.text = FONTS[80].render("Connecting...", True, BLACK.color)
            blit_centered_text(self.window, self.text)
        elif self.connection_tried and self.connection_failed:
            text = FONTS[60].render("Failed to connect! :(", True, BLACK.color)
            blit_centered_text(self.window, text)
        elif self.connection_tried and not self.connection_failed:
            for btn in self.buttons.values():
                btn.draw()
            text = FONTS[25].render(f"Lobby: {str(self.game.game_id)}", True, BLACK.color)
            self.window.blit(text, (10, 10))
            if not self.player.color:
                text = FONTS[50].render("Choose your colour!", True, BLACK.color)
                blit_centered_text(self.window, text, -270)
            else:
                text = FONTS[25].render(ENUM_TO_COLOR_OBJECT_MAP[self.player.color].text, True, ENUM_TO_COLOR_OBJECT_MAP[self.player.color].color)
                self.window.blit(text, (10, 40))
                text = FONTS[40].render(f"Players in Lobby: {str(len(self.game.players))}/4", True, BLACK.color)
                blit_centered_text(self.window, text, -220)
                text = FONTS[50].render("Waiting for Players...", True, ENUM_TO_COLOR_OBJECT_MAP[self.player.color].color)
                blit_centered_text(self.window, text, -50)
