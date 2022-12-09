import json
import threading
from math import floor

import pygame
from playsound import playsound

import Client
from cell import Cell
from grid import Grid
from globals import (BG_COLOR, DEFAULT_SETTINGS, DISP, DISP_H, DISP_W,
                     FLAGGED_CELLS, GAME_STATE_IMAGES, PATH,
                     RESTART_SPR, SETTINGS_SPR, NAUTIOUS, SHOCKED)

pygame.init()


class Game():

    def __init__(self) -> None:
        self.runing = True
        self.flagging = False
        self.settings = DEFAULT_SETTINGS
        self.settings_btn = Cell(
            self.settings["width"] - 0.75, -2.75, SETTINGS_SPR, False)
        if self.settings["width"] % 2 == 0:
            self.reset_btn = Cell(
                self.settings["width"] / 2 - 0.5, -2, RESTART_SPR, False)
        else:
            self.reset_btn = Cell(
                RESTART_SPR, self.settings["width"] / 2, -2, False)
        self.drawThread: threading.Thread = None
        self.clientThread: threading.Thread = None
        self.grid = Grid()

    def flag(self, x: int, y: int):
        """This method Flags/Unflags the cell at the given coordinates.

        Args:
            x (int): The x coordinate of the cell to flag.
            y (int): The y coordinate of the cell to
        """

        global FLAGGED_CELLS, RESTART_SPR

        if self.grid.contents[y][x].flagged:
            self.grid.contents[y][x].flagged = False
            FLAGGED_CELLS -= 1
        else:
            self.grid.contents[y][x].flagged = True
            FLAGGED_CELLS += 1

        if FLAGGED_CELLS == self.grid.num_of_mines:
            b = False
            for list in self.grid.contents:
                for cell in list:
                    if cell.content == -1 and not cell.flagged:
                        b = True
                        break

                if b:
                    break

            else:
                FLAGGED_CELLS = 0
                RESTART_SPR = 12
                self.reset_btn.content = 12
                for list in self.grid.contents:
                    for cell in list:
                        if cell.content != -1:
                            cell.hidden = False
                self.grid.state = 0

    def reveal(self, x: int, y: int):
        """This method reveals the cell at the given coordinates if possible.

        Args:
            x (int): The x coordinate of the cell.
            y (int): The y coordinate of the cell.
        """
        if not self.grid.contents_created:
            self.grid.createLayout(x, y)

        dead = self.grid.revealCell(x, y)
        if dead == -1:
            self.reset_btn.content = 13

    def restart(self):
        """Resets the given Game.

        Args:
            game (Minesweeper.Game): The game which we are trying to reset
        """
        global RESTART_SPR

        RESTART_SPR = 10
        self.grid = Grid()
        self.play()

    def setSettings(self):
        """This method writes the current settings configuration into settings.json in a readable format.
        """

        with open(PATH[:-6] + "settings.json", "w") as stngs:
            settings = json.dumps(self.settings).split(", ")
            stngs.write("{\n")
            stngs.write("    " + settings[0][1:] + ",\n")
            stngs.writelines(
                ["    " + settings[i] + ",\n" for i in range(1, len(settings) - 1)])
            stngs.write("    " + settings[len(settings) - 1][:-1] + "\n")
            stngs.write("}")

        self.restart()

    def play(self):
        """Init & Create the display, the grid and starts the relevant Threads.
        """
        self.running = True
        if self.drawThread is not None and not self.drawThread.is_alive():
            self.drawThread.start()

        if self.clientThread is not None and not self.clientThread.is_alive():
            if self.settings["allow_command_input"]:
                self.clientThread.start()

    def gameLoop(self):
        """This function has the main game loop and should occupie the drawThread of the corrasponding game.

        Args:
            game (Minesweeper.Game): The game which loop we are running
        """

        global RESTART_SPR

        while self.runing:

            DISP.fill(BG_COLOR)
            for y in range(self.settings["height"]):
                for x in range(self.settings["width"]):
                    self.grid.contents[y][x].drawCell()

            self.settings_btn.drawCell()
            self.reset_btn.drawCell()

            if self.grid.state != 1:
                DISP.blit(GAME_STATE_IMAGES[self.grid.state],
                          pygame.rect.Rect(10, 10, 10, 10))

            for event in pygame.event.get():
                match event.type:
                    case pygame.MOUSEBUTTONDOWN:
                        self.findAffectedCell(event)
                    case pygame.MOUSEMOTION:
                        self.highlightCell(event)
                    case pygame.QUIT:
                        self.exit()
                    case _:
                        pass
            pygame.display.update()

        pygame.quit()

    def findAffectedCell(self, event: pygame.event.Event):
        """Reacts to player left click

        Args:
            game (Minesweeper.Game): The game to react to.
            event (pygame.event.Event, optional): The event associated with the left click.
        """
        x = (event.pos[0] - self.settings["lrb_border_size"]) / \
            self.settings["cell_size"]
        y = (event.pos[1] - self.settings["top_border_size"]) / \
            self.settings["cell_size"]
        if self.grid.state == 1:
            if self.settings["top_border_size"] < event.pos[1] < DISP_H - self.settings["lrb_border_size"] and self.settings["lrb_border_size"] < event.pos[0] < DISP_W - self.settings["lrb_border_size"]:
                x = floor(x)
                y = floor(y)
                actions = {1: self.reveal,
                           3: self.flag,
                           }
                try:
                    actions[event.button](x, y)
                except:
                    pass

        if round(x) == round(self.reset_btn.x_pos) and floor(y) == self.reset_btn.y_pos:
            self.restart()

    def highlightCell(self, event: pygame.event.Event):
        """Reacts to cursor movement

        Args:
            game (Minesweeper.Game): The game to react in.
            event (pygame.event.Event): The event associated with the left click.
        """
        x = (event.pos[0] - self.settings["lrb_border_size"]) / \
            self.settings["cell_size"]
        y = (event.pos[1] - self.settings["top_border_size"]) / \
            self.settings["cell_size"]
        if round(x) == round(self.reset_btn.x_pos) and floor(y) == self.reset_btn.y_pos:
            self.reset_btn.content = SHOCKED
        elif self.grid.state == -1:
            self.reset_btn.content = NAUTIOUS
        elif self.reset_btn.content != RESTART_SPR:
            self.reset_btn.content = RESTART_SPR

    def initThreads(self):
        """Initializes the game's Threads

        Args:
            game (Minesweeper.Game): The game which threads we initialize.
        """
        if self.settings["allow_command_input"]:
            self.clientThread = threading.Thread(
                target=Client.client, args=(self,))
        self.drawThread = threading.Thread(target=self.gameLoop)

    def exit(self):
        """Exits the given Game.

        Args:
            game (Minesweeper.Game): The game we are trying to exit.
            event (pygame.event.Event): The event that caused the need to exit.
        """
        self.runing = False
