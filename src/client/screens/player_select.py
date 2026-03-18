import pygame
from .. import load_assets as assets
from ..button import Button
from ..explosion import Explosion
from ..utils import *
from ..constants import *
from ..networking import Network
from ...shared.game import Game

class PlayerSelectScreen(ScreenStateInterface):
    def __init__(self, window: pygame.surface.Surface, state: ClientState):
        self.window = window
        self.state = state
        self.game: Game = None
        self.color_buttons = {
            "red": Button(window, state, 'Red', 375, 175, 200, 200, RED, RED, sound=assets.click),
            "green": Button(window, state, 'Green', 375, 375, 200, 200, GREEN, GREEN, sound=assets.click),
            "blue": Button(window, state, 'Blue', 175, 175, 200, 200, BLUE, BLUE, sound=assets.click),
            "yellow": Button(window, state, 'Yellow', 175, 375, 200, 200, YELLOW, YELLOW, sound=assets.click),
        }
        self.lobby_buttons = {
            "ready_up_button": Button(window, state, 'Ready Up', 225, 450, 300, 150, BLACK, WHITE, sound=assets.click, enabled=False, visible=False),
        }
        self.active_buttons = self.color_buttons
        self.fonts = {
            25: pygame.font.SysFont("consolas", 25),
            40: pygame.font.SysFont("consolas", 40),
            50: pygame.font.SysFont("consolas", 50),
            60: pygame.font.SysFont("consolas", 60),
            80: pygame.font.SysFont("consolas", 80),
        }
        self.connection_failed = False
        self.text = self.fonts[80].render("Connecting...", True, BLUE)
        blit_centered_text(self.window, self.text)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and self.state.connected:
            pos = pygame.mouse.get_pos()
            for btn in self.active_buttons.values():
                if btn.click(pos):
                    game = self.state.network.send(btn.text)
                    print("Clicked:", btn.text)
                    print("Position", game.players[self.state.player_id][0])
                    print("Color:", game.players[self.state.player_id][1])
                    print("Blocked colors", game.blocked_colors)
        elif event.type == FAILED_TO_CONNECT_TIMER:
            pygame.event.post(pygame.event.Event(CHANGE_STATE, {"state": "menu_screen"}))

    def update(self, dt):
        if not self.state.connected and not self.connection_failed:
            try:
                self.state.network.connect()
                self.game = self.state.network.send("get")
            except Exception as e:
                self.update_connection_failed(e)
            else:
                self.state.connected = True
                self.state.player_id = self.game.num_of_players
                print("You are player", self.state.player_id)
        self.game = self.state.network.send("get")
    
    def draw(self):
        draw_bg(self.window, self.state)
        if self.connection_failed:
            self.draw_connection_failed()
        else:
            if self.game.players[self.state.player_id][1] == None:
                self.draw_ask_for_color()
            else:
                self.draw_waiting_for_players()

    def draw_ask_for_color(self):
        self.active_buttons = self.color_buttons
        text = self.fonts[50].render("Choose your colour!", True, BLACK)
        blit_centered_text(self.window, text, -300)
        for btn in self.color_buttons.values():
            if btn.text in self.game.blocked_colors:
                btn.disable()
            else:
                btn.draw()

    def draw_waiting_for_players(self):
        self.active_buttons = self.lobby_buttons
        if not self.game.started:
            text = self.fonts[25].render("Lobby: " + str(self.game.game_id), True, BLACK)
            self.window.blit(text, (10, 10))
            text = self.fonts[25].render("Player: " + str(self.state.player_id), True, BLACK)
            self.window.blit(text, (10, 40))
            text = self.fonts[25].render(self.game.players[self.state.player_id][1], True, parse_color(self.game.players[self.state.player_id][1]))
            self.window.blit(text, (10, 70))
            text = self.fonts[40].render("Players in Lobby: (" + str(self.game.num_of_players) + "/4)", True, BLACK)
            blit_centered_text(self.window, text, -220)
            if self.game.num_of_players < 4:
                text = self.fonts[50].render("Waiting for Players...", True, parse_color(self.game.players[self.state.player_id][1]))
                blit_centered_text(self.window, text, 25)
            if self.game.num_of_players >= 2:
                if self.game.players[self.state.player_id][3] == True:
                    self.lobby_buttons["ready_up_button"].disable()
                else:
                    self.lobby_buttons["ready_up_button"].draw()
                    self.lobby_buttons["ready_up_button"].enable()


    def update_connection_failed(self, e):
        print(e)
        print("Could not connect!")
        self.connection_failed = True
        pygame.time.set_timer(FAILED_TO_CONNECT_TIMER, 1000)

    def draw_connection_failed(self):
        text = self.fonts[60].render("Failed to connect! :(", True, BLACK)
        blit_centered_text(self.window, text)
