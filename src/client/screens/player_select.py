import pygame
from src.shared.constants import *
from ..constants import *
from .. import load_assets as assets
from ..button import Button
from ..utils import *
from src.shared.game import Game, Player
from src.shared.debug import DEBUG_FLAGS

class PlayerSelectScreen(ScreenStateInterface):
    def __init__(self, window: pygame.surface.Surface, state: ClientState):
        self.window = window
        self.state = state
        self.connection_tried = False
        self.connection_failed = False
        self.color_buttons: dict[str, Button] = {
            "red": Button(window, state, 'Red', 375, 175, 200, 200, RED.color, RED.color, sound=assets.click, enabled=True),
            "green": Button(window, state, 'Green', 375, 375, 200, 200, GREEN.color, GREEN.color, sound=assets.click, enabled=True),
            "blue": Button(window, state, 'Blue', 175, 175, 200, 200, BLUE.color, BLUE.color, sound=assets.click, enabled=True),
            "yellow": Button(window, state, 'Yellow', 175, 375, 200, 200, YELLOW.color, YELLOW.color, sound=assets.click, enabled=True),
        }
        self.lobby_buttons: dict[str, Button] = {
            "ready_up_button": Button(window, state, 'Ready Up', 225, 450, 300, 150, BLACK.color, WHITE.color, sound=assets.click),
        }
        self.buttons: dict[str, Button] = self.color_buttons | self.lobby_buttons
    
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
        elif event.type == FAILED_TO_CONNECT_TIMER:
            pygame.time.set_timer(FAILED_TO_CONNECT_TIMER, 0)
            pygame.event.post(pygame.event.Event(CHANGE_STATE, {"state": "menu_screen"}))

    def update(self, dt):
        if not self.connection_tried and not self.connection_failed:
            try:
                self.connection_tried = True
                self.state.network.connect()
                self.state.game = self.state.network.send("get")
            except Exception:
                self.connection_failed = True
                pygame.time.set_timer(FAILED_TO_CONNECT_TIMER, 1000)
            else:
                self.state.player_id = next(reversed(self.game.players.values())).player_id
                print(f"Player ID {self.state.player_id}")

        if self.connection_tried and not self.connection_failed:
            self.state.game = self.state.network.send("get")
            if not self.player.color:
                for btn in self.color_buttons.values():
                    if btn.text in self.game.taken_colors:
                        btn.disable()
                    else:
                        btn.enable()
            else:
                [color_button.disable() for color_button in self.color_buttons.values()]
                if self.player.ready:
                    self.buttons["ready_up_button"].disable()
                else:
                    self.buttons["ready_up_button"].enable()
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
                blit_centered_text(self.window, text, -300)
            else:
                text = FONTS[25].render(self.player.color.text, True, self.player.color.color)
                self.window.blit(text, (10, 40))
                text = FONTS[40].render(f"Players in Lobby: {str(len(self.game.players))}/4", True, BLACK.color)
                blit_centered_text(self.window, text, -220)
                text = FONTS[50].render("Waiting for Players...", True, self.player.color.color)
                blit_centered_text(self.window, text, -50)
