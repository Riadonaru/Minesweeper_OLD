import json
import threading
from math import floor

import pygame

from client import client
from cell import Cell
from grid import Grid
from globals import (BG_COLOR, CELL_EDGE, COOL, LOSE, PLAYING, GEAR, DISP, DISP_H, DISP_W, LRB_BORDER, PATH,
                     RESET, SETTINGS, DEAD, SHOCKED, SMILE, TOP_BORDER, WIN)
from sprites import SPRITES
pygame.init()


class Game():

    clicked_cell: Cell = None

    def __init__(self) -> None:
        self.runing = True
        self.flagging = False
        self.flagged_cells = 0
        self.settings_btn = Cell(SETTINGS["width"] - 0.75, -2.75, GEAR, False)
        if SETTINGS["width"] % 2 == 0:
            self.reset_btn = Cell(
                SETTINGS["width"] / 2 - 0.5, -2, RESET, False)
        else:
            self.reset_btn = Cell(RESET, SETTINGS["width"] / 2, -2, False)
        self.clientThread: threading.Thread = None
        if SETTINGS["allow_command_input"]:
            self.clientThread = threading.Thread(target=client, args=(self,))
        self.grid = Grid()

    def reveal(self, x: int, y: int):
        """This method reveals the cell at the given coordinates if possible.

        Args:
            x (int): The x coordinate of the cell.
            y (int): The y coordinate of the cell.
        """
        if not self.grid.contents_created:
            self.grid.create_layout(x, y)

        self.grid.clicked_cell = self.grid.contents[y][x]
        dead = self.grid.reveal_next(x, y)
        if dead == -1:
            self.reset_btn.value = SHOCKED

    def flag(self, x: int, y: int):
        """This method Flags/Unflags the cell at the given coordinates.

        Args:
            x (int): The x coordinate of the cell to flag.
            y (int): The y coordinate of the cell to
        """

        global RESET

        if self.grid.contents[y][x].hidden:
            if self.grid.contents[y][x].flagged:
                self.grid.contents[y][x].flagged = False
                self.flagged_cells -= 1
            else:
                self.grid.contents[y][x].flagged = True
                self.flagged_cells += 1

        if self.flagged_cells == self.grid.mines:
            b = False
            for list in self.grid.contents:
                for cell in list:
                    if cell.value == -1 and not cell.flagged:
                        b = True
                        break

                if b:
                    break

            else:
                self.flagged_cells = 0
                RESET = COOL
                self.reset_btn.value = COOL
                for list in self.grid.contents:
                    for cell in list:
                        if cell.value != -1:
                            cell.hidden = False
                self.grid.state = WIN

    def find_affected_cell(self, event: pygame.event.Event):
        """Reacts to player left click

        Args:
            game (Minesweeper.Game): The game to react to.
            event (pygame.event.Event, optional): The event associated with the left click.
        """
        x = (event.pos[0] - LRB_BORDER) / CELL_EDGE
        y = (event.pos[1] - TOP_BORDER) / CELL_EDGE
        if self.grid.state == PLAYING:
            if TOP_BORDER < event.pos[1] < DISP_H - LRB_BORDER and LRB_BORDER < event.pos[0] < DISP_W - LRB_BORDER:
                x = floor(x)
                y = floor(y)
                actions = {1: self.reveal,
                           3: self.flag,
                           }
                try:
                    actions[event.button](x, y)
                except:
                    pass

        if round(x) == round(self.reset_btn.x) and floor(y) == self.reset_btn.y:
            self.reset()

    def highlight_cell(self, event: pygame.event.Event):
        """Reacts to cursor movement

        Args:
            game (Minesweeper.Game): The game to react in.
            event (pygame.event.Event): The event associated with the left click.
        """
        x = (event.pos[0] - LRB_BORDER) / CELL_EDGE
        y = (event.pos[1] - TOP_BORDER) / CELL_EDGE
        if round(x) == round(self.reset_btn.x) and floor(y) == self.reset_btn.y:
            self.reset_btn.value = SHOCKED
        elif self.grid.state == LOSE:
            self.reset_btn.value = DEAD
        elif self.reset_btn.value != RESET:
            self.reset_btn.value = RESET

    def set_settings(self):
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

        self.reset()

    def reset(self):
        """Resets the given Game.

        Args:
            game (Minesweeper.Game): The game which we are trying to reset
        """
        global RESET

        RESET = SMILE
        self.grid = Grid()
        self.play()

    def exit(self):
        """Exits the given Game.

        Args:
            game (Minesweeper.Game): The game we are trying to exit.
            event (pygame.event.Event): The event that caused the need to exit.
        """
        self.runing = False

    def play(self):
        """This function has the main game loop and should occupie the drawThread of the corrasponding game.

        Args:
            game (Minesweeper.Game): The game which loop we are running
        """

        global RESET

        self.running = True
        if self.clientThread is not None and not self.clientThread.is_alive():
            if SETTINGS["allow_command_input"]:
                self.clientThread.start()

        while self.runing:

            DISP.fill(BG_COLOR)
            for y in range(SETTINGS["height"]):
                for x in range(SETTINGS["width"]):
                    self.grid.contents[y][x].draw()

            self.settings_btn.draw()
            self.reset_btn.draw()

            if self.grid.state != PLAYING:
                DISP.blit(SPRITES[self.grid.state], (LRB_BORDER, TOP_BORDER))

            for event in pygame.event.get():
                match event.type:
                    case pygame.MOUSEBUTTONDOWN:
                        self.find_affected_cell(event)
                    case pygame.MOUSEMOTION:
                        self.highlight_cell(event)
                    case pygame.QUIT:
                        self.exit()
                    case _:
                        pass
            pygame.display.update()

        pygame.quit()
