import threading
from math import floor

import pygame

import Client
import Minesweeper


def gameLoop(game: Minesweeper.Game):
    """This function has the main game loop and should occupie the drawThread of the corrasponding game.

    Args:
        game (Minesweeper.Game): The game which loop we are running
    """
    while game.runing:

        game.gameDisplay.fill(Minesweeper.BG_COLOR)
        for y in range(game.settings["height"]):
            for x in range(game.settings["width"]):
                game.grid.contents[y][x].drawCell(x, y)

        game.settings_button.drawCell(
            game.settings_pos[0], game.settings_pos[1])
        game.restart_button.drawCell(
            game.restart_pos[0], game.restart_pos[1])

        if game.condition != 1:
            game.gameDisplay.blit(Minesweeper.GAME_STATE_IMAGES[game.condition], pygame.rect.Rect(10, 10, 10, 10))

        pygame.display.update()
        for event in pygame.event.get():
            try:
                EVENT_TYPES[event.type](game, event)
            except Exception as e:
                pass

    pygame.quit()


def findAffectedCell(game: Minesweeper.Game, event: pygame.event.Event):
    """Reacts to player left click

    Args:
        game (Minesweeper.Game): The game to react to.
        event (pygame.event.Event, optional): The event associated with the left click.
    """
    x = (event.pos[0] - game.settings["lrb_border_size"]) / \
        game.settings["cell_size"]
    y = (event.pos[1] - game.settings["top_border_size"]) / \
        game.settings["cell_size"]
    if game.condition == 1:
        if game.settings["top_border_size"] < event.pos[1] < game.disp_height - game.settings["lrb_border_size"] and game.settings["lrb_border_size"] < event.pos[0] < game.disp_width - game.settings["lrb_border_size"]:
            x = floor(x)
            y = floor(y)
            actions = {1: game.reveal,
                    3: game.flag,
                    }
            actions[event.button](x, y)

    if round(x) == round(game.restart_pos[0]) and floor(y) == game.restart_pos[1]:
        game.restart()



def highlightCell(game: Minesweeper.Game, event: pygame.event.Event):
    """Reacts to cursor movement

    Args:
        game (Minesweeper.Game): The game to react in.
        event (pygame.event.Event): The event associated with the left click.
    """
    x = (event.pos[0] - game.settings["lrb_border_size"]) / \
        game.settings["cell_size"]
    y = (event.pos[1] - game.settings["top_border_size"]) / \
        game.settings["cell_size"]
    if round(x) == round(game.restart_pos[0]) and floor(y) == game.restart_pos[1]:
        game.restart_button.content = 11
    elif game.restart_button.content != 10:
        game.restart_button.content = Minesweeper.RESTART_SPR


def initThreads(game: Minesweeper.Game):
    """Initializes the game's Threads

    Args:
        game (Minesweeper.Game): The game which threads we initialize.
    """
    if game.settings["allow_command_input"]:
        game.clientThread = threading.Thread(target=Client.client, args=(game,))
    game.drawThread = threading.Thread(target=gameLoop, args=(game,))


def exit(game: Minesweeper.Game, event: pygame.event.Event):
    """Exits the given Game.

    Args:
        game (Minesweeper.Game): The game we are trying to exit.
        event (pygame.event.Event): The event that caused the need to exit.
    """
    game.runing = False


def hardReset():
    Minesweeper.GAME.runing = False
    Minesweeper.GAME = Minesweeper.Game()
    initThreads(Minesweeper.GAME)
    Minesweeper.GAME.play()


EVENT_TYPES = {
    pygame.MOUSEBUTTONDOWN: findAffectedCell,
    pygame.MOUSEMOTION: highlightCell,
    pygame.QUIT: exit
}


initThreads(Minesweeper.GAME)
Minesweeper.GAME.play()
