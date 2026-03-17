import pygame
from .. import load_assets as assets
from ..button import Button
from ..explosion import Explosion
from ..utils import *
from ..constants import *
from ..networking import Network
from ...shared.game import Game

class PlayerSelectScreen(ScreenStateInterface):
    def __init__(self, window: pygame.surface.Surface, state: Game):
        self.window = window
        self.state = state
        self.select_color_buttons = {
            "red": Button(window, state, 'Red', 375, 175, 200, 200, RED, RED, sound=assets.click),
            "green": Button(window, state, 'Green', 375, 375, 200, 200, GREEN, GREEN, sound=assets.click),
            "blue": Button(window, state, 'Blue', 175, 175, 200, 200, BLUE, BLUE, sound=assets.click),
            "yellow": Button(window, state, 'Yellow', 175, 375, 200, 200, YELLOW, YELLOW, sound=assets.click),
            "ready_up_button": Button(window, state, 'Ready Up', 225, 450, 300, 150, BLACK, WHITE, sound=assets.click),
        }
        self.draw()
        server_crash = False
        font = pygame.font.SysFont("consolas", 80)
        text = font.render("Connecting...", True, BLUE)
        blit_centered_text(self.window, text)
        pygame.display.update()
        try:
            p = int(self.network.get_p())
        except ValueError:
            print("Server crashed!")
            pygame.quit()
            server_crash = True
        except TypeError as e:
            print("Could not connect!")
            print(e)
            self.failed_to_connect()

        if not server_crash:
            print("You are player", p)
            self.main(p)

    def draw(p=None, white=True, update=True):
        if white == True:
            draw_bg(self.window, self.state)
        if state.game and p != None:
            if state.game.started == True:
                draw_game_objects(p)
            # if player has not chosen color yet
            check_and_ask_for_color(p)
            check_and_display_waiting_for_players(p)
        if update:
            pygame.display.update()

    def check_and_display_waiting_for_players(self, p):
        # checks if color selection has been made. if it has been made, display waiting for players
        if not self.state.game.started and self.state.game.players[p][1] != None:
            font = pygame.font.SysFont("consolas", 25)
            text = font.render("Lobby: " + str(self.state.game.id), True, BLACK)
            self.window.blit(text, (10, 10))
            text = font.render("Player: " + str(p), True, BLACK)
            self.window.blit(text, (10, 40))
            text = font.render(self.state.game.players[p][1], True, parse_color(self.state.game.players[p][1]))
            self.window.blit(text, (10, 70))
            font = pygame.font.SysFont("consolas", 40)
            text = font.render("Players in Lobby: (" + str(self.state.game.num_of_players) + "/4)", True, BLACK)
            blit_centered_text(self.window, text, -220)
            if self.state.game.num_of_players < 4:
                font = pygame.font.SysFont("consolas", 50)
                text = font.render("Waiting for Players...", True, BLUE)
                blit_centered_text(self.window, text, -50)
            if self.state.game.num_of_players >= 2:
                if self.state.game.players[p][3] == True:
                    self.buttons["ready_up_button"].disable()
                else:
                    self.buttons["ready_up_button"].draw()
                    self.buttons["ready_up_button"].enable()


    def check_and_ask_for_color(self, p):
        if self.state.game.players[p][1] == None:
            font = pygame.font.SysFont("consolas", 50)
            text = font.render("Choose your colour!", True, BLACK)
            blit_centered_text(self.window, text, -300)
            for btn in self.select_color_buttons.values():
                if btn.text in self.state.game.blocked_colors:
                    btn.disable()
                else:
                    btn.draw()
                    btn.enable()
        else:
            for btn in self.select_color_buttons.values():
                btn.disable()

    def failed_to_connect(self):
        self.redraw_window()
        font = pygame.font.SysFont("consolas", 60)
        text = font.render("Failed to connect! :(", True, BLACK)
        blit_centered_text(self.window, text)
        pygame.display.update()
        pygame.time.delay(1500)
        self.menu_screen()
