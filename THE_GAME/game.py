import json
import random
import threading
from math import floor, sqrt
import time

import pygame

from client import client
from cell import Cell
from grid import Grid
from globals import (BG_COLOR, CELL_EDGE, COOL, LOSE, MINE, PLAYING, GEAR, DISP, DISP_H, DISP_W, LRB_BORDER, PATH,
                     RESET, SETTINGS, DEAD, SHOCKED, SMILE, TOP_BORDER, WIN, BLACK, FONT_SIZE)
from sprites import SPRITES, HOURGLASS, MINESPR
pygame.init()


class Game():

    clicked_cell: Cell = None

    def __init__(self) -> None:
        self.runing = True
        self.flagged_cells = 0
        self.elapsed_time = 0
        self.font = pygame.font.Font(
            PATH + "Font.ttf", FONT_SIZE)
        self.settings_btn = Cell(
            SETTINGS["width"] - 0.75, -2.75, value=GEAR, hidden=False, create_hitbox=True)
        self.reset_btn = Cell(
            SETTINGS["width"] / 2 - 0.5, -2, value=RESET, hidden=False, create_hitbox=True)
        self.settings_btn.create_hitbox()
        self.reset_btn.create_hitbox()
        self.clientThread: threading.Thread = None
        self.timerThread = threading.Thread(target=self.timer)
        if SETTINGS["allow_command_input"]:
            self.clientThread = threading.Thread(target=client, args=(self,))
        self.grid = Grid()

    def timer(self):
        while self.running:
            while self.grid.contents_created and self.grid.state == PLAYING:
                self.elapsed_time += 1
                time.sleep(1)

    def reveal(self, x: int, y: int):
        """This method reveals the cell at the given coordinates if possible.

        Args:
            x (int): The x coordinate of the cell.
            y (int): The y coordinate of the cell.
        """
        if not self.grid.contents_created:
            self.grid.create_layout(x, y)

        self.grid.clicked_cell = self.grid.contents[y][x]
        if self.grid.reveal_next(x, y):
            self.reset_btn.value = DEAD

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
                    if cell.value == MINE and not cell.flagged:
                        b = True
                        break

                if b:
                    break

            else:
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

        if self.reset_btn.hitbox.collidepoint(event.pos[0], event.pos[1]):
            self.reset()
        elif self.settings_btn.hitbox.collidepoint(event.pos[0], event.pos[1]) and self.grid.troll_mode:
            if self.grid.contents[0][0].hidden == False:
                self.grid.troll()
            else:
                for y in range(SETTINGS["height"]):
                    for x in range(SETTINGS["width"]):
                        self.grid.contents[y][x].hidden = False

    def highlight_cell(self, event: pygame.event.Event):
        """Reacts to cursor movement

        Args:
            game (Minesweeper.Game): The game to react in.
            event (pygame.event.Event): The event associated with the left click.
        """
        if self.reset_btn.hitbox.collidepoint(event.pos[0], event.pos[1]):
            self.reset_btn.value = SHOCKED
        elif self.grid.state == LOSE:
            self.reset_btn.value = DEAD
        elif self.reset_btn.value != RESET:
            self.reset_btn.value = RESET

    def set_settings(self):
        """This method writes the current settings configuration into settings.json in a readable format.
        """

        with open(PATH[:-6] + "settings.json", "w") as stngs:
            settings = json.dumps(SETTINGS).split(", ")
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
        self.elapsed_time = 0
        self.flagged_cells = 0
        self.grid.contents_created = False
        self.grid.troll_mode = False
        self.grid = Grid()
        self.play()

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

        if not self.timerThread.is_alive():
            self.timerThread.start()

        while self.runing:

            mines_left = self.font.render(
                str(self.grid.mines - self.flagged_cells), 0, BLACK)
            time_elapsed = self.font.render(str(self.elapsed_time), 0, BLACK)
            DISP.fill(BG_COLOR)
            DISP.blits([(MINESPR, (LRB_BORDER, LRB_BORDER)), (mines_left, (LRB_BORDER + 15, LRB_BORDER + 5)), (HOURGLASS, (LRB_BORDER,
                       LRB_BORDER * 2)), (time_elapsed, (LRB_BORDER + 15, LRB_BORDER * 2 + 5))])
            for y in range(SETTINGS["height"]):
                for x in range(SETTINGS["width"]):
                    self.grid.contents[y][x].draw()

            self.settings_btn.draw()
            self.reset_btn.draw()

            if self.grid.state != PLAYING:
                DISP.blit(SPRITES[self.grid.state], (LRB_BORDER, TOP_BORDER))

            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                DISP.blit(self.font.render("PAUSED", 0, BLACK), (DISP_W // 2, DISP_H // 2))

            for event in pygame.event.get():
                match event.type:
                    case pygame.MOUSEBUTTONDOWN:
                        self.find_affected_cell(event)
                    case pygame.MOUSEMOTION:
                        self.highlight_cell(event)
                    case pygame.QUIT:
                        self.runing = False

                    case _:
                        pass
            pygame.display.update()

        pygame.quit()
