import pygame

from . import load_assets as assets
from .utils import *
from .constants import *

from .screens.main_menu import MenuScreen
from .screens.player_select import PlayerSelectScreen
from .screens.active_game import ActiveGameScreen

pygame.font.init()
pygame.display.set_icon(assets.ICON)
pygame.display.set_caption("Snakes, Ladders and Nukes")

window: pygame.surface.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
state = ClientState()

screen_states = {
    "menu_screen": MenuScreen(window, state),
    "player_select": PlayerSelectScreen(window, state),
    #"active_game": ActiveGameScreen(window, state),
}
state.screen_state = screen_states["menu_screen"]

window.fill(WHITE)
pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == CHANGE_STATE:
            state.screen_state = screen_states[event.state]
        else:
            state.screen_state.handle_event(event)
    dt = state.clock.tick(60)
    state.screen_state.update(dt)
    state.screen_state.draw()
    pygame.display.flip()
