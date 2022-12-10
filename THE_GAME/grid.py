import threading
from typing import List, Set

import numpy as np
from playsound import playsound

from cell import Cell
from globals import CLICKED_MINE, DEAD, LOSE, PLAYING, SETTINGS, MINE, NOMINE, PATH


class Grid():

    clicked_cell: Cell = None

    def __init__(self) -> None:
        self.state: int = PLAYING  # 1 for playing, 14 for win, 15 for lose.
        self.contents_created: bool = False
        self.tiles = SETTINGS["width"] * SETTINGS["height"]
        self.mines = int(self.tiles * SETTINGS["mines"] / 100)
        self.contents: np.ndarray = np.array([Cell(x, y) for x in range(
            SETTINGS["width"]) for y in range(SETTINGS["height"])])
        self.contents = np.reshape(
            self.contents, (SETTINGS["height"], SETTINGS["width"]), 'F')

    def create_layout(self, x: int = None, y: int = None) -> None:
        """Creates the grid layout for the game and stores it in self.contents

        Args:
            x (int, optional): The x location for a safe start. Defaults to None.
            y (int, optional): The y location for a safe start. Defaults to None.
        """
        if not self.contents[y][x].flagged:

            self.contents = np.array([Cell for _ in range(self.tiles)])

            for i in range(self.tiles):
                if i < self.mines:
                    self.contents[i] = Cell(value=-1)
                else:
                    self.contents[i] = Cell()

            np.random.shuffle(self.contents)
            self.contents: List[List[Cell]] = list(self.contents.reshape(
                SETTINGS["height"], SETTINGS["width"]))

            if SETTINGS["easy_start"]:
                for b in range(-1, 2):
                    for a in range(-1, 2):
                        if 0 <= x + a < SETTINGS["width"] and 0 <= y + b < SETTINGS["height"]:
                            if self.contents[y + b][x + a].value != 0:
                                self.contents[y + b][x + a].value = 0

            for y in range(SETTINGS["height"]):
                for x in range(SETTINGS["width"]):
                    self.contents[y][x].x = x
                    self.contents[y][x].y = y
                    self.contents[y][x].value = self.assign_value(x, y)

            self.contents_created = True

    def assign_value(self, x_index: int, y_index: int) -> int:
        """Returns the number of adjacent mines to the cell at the given index.

        Args:
            x_index (int): The x index of the cell.
            y_index (int): The y index of the cell.

        Returns:
            int: The number of mines adjacent to the cell.
        """
        if self.contents[y_index][x_index].value != -1:
            num_of_adj_mines = 0
            # print("\nNew\n")
            for y in range(-1, 2):
                for x in range(-1, 2):
                    if 0 <= x_index + x < SETTINGS["width"] and 0 <= y_index + y < SETTINGS["height"]:
                        if self.contents[y_index + y][x_index + x].value == -1:
                            # print("Mine at:", x_index + x, y_index + y)
                            num_of_adj_mines += 1

            return num_of_adj_mines
        else:
            return -1

    def reveal_next(self, x: int, y: int):
        """This method has the reveal algo.
        """
        global RESTART_SPR

        try:
            cell = self.contents[y][x]
            if cell.value == MINE:
                cell.value = CLICKED_MINE
                self.state = LOSE
                RESTART_SPR = DEAD
                if SETTINGS["play_sounds"]:
                    threading.Thread(target=playsound, args=(
                        PATH + "game-over.mp3",)).start()

                for list in self.contents:
                    for cell in list:
                        if not cell.flagged:
                            cell.hidden = False
                        elif cell.value != MINE:
                            cell.value = NOMINE
                            cell.flagged = False
                            cell.hidden = False

                return -1

            if not self.check_cell(cell.x, cell.y):
                cell.hidden = False
                if self.check_saturation(cell.x, cell.y):
                    for y in range(-1, 2):
                        for x in range(-1, 2):
                            if 0 <= cell.x + x < SETTINGS["width"] and 0 <= cell.y + y < SETTINGS["height"]:
                                adj_cell = self.contents[cell.y +
                                                         y][cell.x + x]
                                if not adj_cell.flagged:
                                    self.reveal_next(adj_cell.x, adj_cell.y)
        except Exception as e:
            raise Exception(e)

    def check_saturation(self, x: int, y: int) -> bool:
        """This method checks if there are as much flags around a cell as the number on it.

        Returns:
            bool: True if as much flags, False if less or the cell is a mine.
        """
        adj_flags = 0
        if self.contents[y][x].value not in {0, 1, 2, 3, 4, 5, 6, 7, 8}:
            return False
        else:
            for a in range(-1, 2):
                for b in range(-1, 2):
                    if 0 <= x + a < SETTINGS["width"] and 0 <= y + b < SETTINGS["height"]:
                        if self.contents[y + b][x + a].flagged:
                            adj_flags += 1

            if self.contents[y][x].value == adj_flags:
                return True
            else:
                return False

    def check_cell(self, x: int, y: int) -> bool:
        if self.contents[y][x].hidden or self.clicked_cell == self.contents[y][x]:
            self.clicked_cell = None
            return False
        return True
