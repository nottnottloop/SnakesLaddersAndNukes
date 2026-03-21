import pygame

from . import load_assets as assets
from .utils import *
from .constants import *
from src.shared.constants import *

from .screens.menu_screen import MenuScreen
from .screens.player_select import PlayerSelectScreen
from .screens.active_game import ActiveGameScreen

pygame.font.init()
pygame.display.set_icon(assets.ICON)
pygame.display.set_caption("Snakes, Ladders and Nukes")
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.mixer.set_num_channels(32)

window: pygame.surface.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
state = ClientState()

screen_states = {
    "menu_screen": MenuScreen(window, state),
    "player_select": PlayerSelectScreen(window, state),
    "active_game": ActiveGameScreen(window, state),
}
state.screen_state = screen_states["menu_screen"]

window.fill(WHITE.color)
pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.scancode == pygame.KSCAN_Q and event.mod & (pygame.KMOD_LSHIFT | pygame.KMOD_RSHIFT):
                pygame.mixer.music.stop()
                pygame.event.post(pygame.event.Event(CHANGE_STATE, {"state": "menu_screen"}))
            else:
                state.screen_state.handle_event(event)
        elif event.type == CHANGE_STATE:
            if event.state == "menu_screen":
                state.network.disconnect()
                state = ClientState()
            screen_states[event.state].__init__(window, state)
            state.screen_state = screen_states[event.state]
        else:
            state.screen_state.handle_event(event)
    dt = state.clock.tick(60)
    state.screen_state.update(dt)
    state.screen_state.draw()
    pygame.display.flip()
