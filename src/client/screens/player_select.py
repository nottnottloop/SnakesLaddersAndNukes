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
        self.buttons = {
            "red": Button(window, state, 'Red', 375, 175, 200, 200, RED, RED, sound=assets.click),
            "green": Button(window, state, 'Green', 375, 375, 200, 200, GREEN, GREEN, sound=assets.click),
            "blue": Button(window, state, 'Blue', 175, 175, 200, 200, BLUE, BLUE, sound=assets.click),
            "yellow": Button(window, state, 'Yellow', 175, 375, 200, 200, YELLOW, YELLOW, sound=assets.click),
            "ready_up_button": Button(window, state, 'Ready Up', 225, 450, 300, 150, BLACK, WHITE, sound=assets.click),
        }
        self.fonts = {
            25: pygame.font.SysFont("consolas", 25),
            40: pygame.font.SysFont("consolas", 40),
            50: pygame.font.SysFont("consolas", 50),
            60: pygame.font.SysFont("consolas", 60),
            80: pygame.font.SysFont("consolas", 80),
        }
        self.text = self.fonts[80].render("Connecting...", True, BLUE)
        blit_centered_text(self.window, self.text)

    def handle_event(self, event):
        pass

    def update(self, dt):
        if not self.state.connected:
            try:
                self.state.network.connect()
                self.game = self.state.network.send("get")
            except ValueError:
                print("Server crashed!")
            except TypeError as e:
                print("Could not connect!")
                print(e)
                self.failed_to_connect()
            finally:
                self.state.player_id = self.game.num_of_players
                print("You are player", self.state.player_id)
    
    def draw(self):
        draw_bg(self.window, self.state)
        self.check_and_ask_for_color(self.state.player_id)
        self.check_and_display_waiting_for_players(self.state.player_id)


    def check_and_display_waiting_for_players(self, p):
        # checks if color selection has been made. if it has been made, display waiting for players
        if not self.game.started and self.game.players[p][1] != None:
            text = self.fonts[25].render("Lobby: " + str(self.self.game.id), True, BLACK)
            self.window.blit(text, (10, 10))
            text = self.fonts[25].render("Player: " + str(p), True, BLACK)
            self.window.blit(text, (10, 40))
            text = self.fonts[25].render(self.self.game.players[p][1], True, parse_color(self.self.game.players[p][1]))
            self.window.blit(text, (10, 70))
            text = self.fonts[40].render("Players in Lobby: (" + str(self.self.game.num_of_players) + "/4)", True, BLACK)
            blit_centered_text(self.window, text, -220)
            if self.game.num_of_players < 4:
                text = self.fonts[50].render("Waiting for Players...", True, BLUE)
                blit_centered_text(self.window, text, -50)
            if self.game.num_of_players >= 2:
                if self.game.players[p][3] == True:
                    self.buttons["ready_up_button"].disable()
                else:
                    self.buttons["ready_up_button"].draw()
                    self.buttons["ready_up_button"].enable()


    def check_and_ask_for_color(self, p):
        if self.game.players[p][1] == None:
            text = self.fonts[50].render("Choose your colour!", True, BLACK)
            blit_centered_text(self.window, text, -300)
            for btn in self.buttons.values():
                if btn.text in self.game.blocked_colors:
                    btn.disable()
                else:
                    btn.draw()
                    btn.enable()
        else:
            for btn in self.buttons.values():
                btn.disable()

    def failed_to_connect(self):
        self.redraw_window()
        text = self.fonts[60].render("Failed to connect! :(", True, BLACK)
        blit_centered_text(self.window, text)
        pygame.display.update()
        pygame.time.delay(1500)
        self.menu_screen()
