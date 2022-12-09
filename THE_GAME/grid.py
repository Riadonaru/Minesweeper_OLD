import threading
from typing import List, Set

import numpy as np

from cell import Cell
from globals import DEFAULT_SETTINGS, PATH
from playsound import playsound

class Grid():

    def __init__(self) -> None:
        self.overall_tiles = DEFAULT_SETTINGS["width"] * \
            DEFAULT_SETTINGS["height"]
        self.num_of_mines = int(DEFAULT_SETTINGS["width"] *
                                DEFAULT_SETTINGS["height"] * DEFAULT_SETTINGS["mines"] / 100)
        self.contents_created: bool = False
        self.contents: np.ndarray = np.array([Cell(x, y) for x in range(
            DEFAULT_SETTINGS["width"]) for y in range(DEFAULT_SETTINGS["height"])])
        self.contents = np.reshape(self.contents, (DEFAULT_SETTINGS["height"], DEFAULT_SETTINGS["width"]))
        self.state: int = 1 # 1 for playing, 0 for win, -1 for lose.


    def createLayout(self, x: int = None, y: int = None) -> None:
        """Creates the grid layout for the game and stores it in self.contents

        Args:
            x (int, optional): The x location for a safe start. Defaults to None.
            y (int, optional): The y location for a safe start. Defaults to None.
        """
        if not self.contents[y][x].flagged:

            self.contents = np.array([Cell for _ in range(self.overall_tiles)])

            for i in range(self.overall_tiles):
                if i < self.num_of_mines:
                    self.contents[i] = Cell(value=-1)
                else:
                    self.contents[i] = Cell()

            np.random.shuffle(self.contents)
            self.contents: List[List[Cell]] = list(self.contents.reshape(DEFAULT_SETTINGS["height"], DEFAULT_SETTINGS["width"]))

            if DEFAULT_SETTINGS["easy_start"]:
                for b in range(-1, 2):
                    for a in range(-1, 2):
                        if 0 <= x + a < DEFAULT_SETTINGS["width"] and 0 <= y + b < DEFAULT_SETTINGS["height"]:
                            if self.contents[y + b][x + a].content != 0:
                                self.contents[y + b][x + a].content = 0

            for y in range(DEFAULT_SETTINGS["height"]):
                for x in range(DEFAULT_SETTINGS["width"]):
                    self.contents[y][x].x_pos = x
                    self.contents[y][x].y_pos = y
                    self.contents[y][x].content = self.checkAdjMines(x, y)

            self.contents_created = True

    def revealCell(self, x: int, y: int):
        """This method has the reveal algo.
        """
        global RESTART_SPR

        try:
            cell = self.contents[y][x]
            cell.hidden = False
            if cell.content == -1:
                cell.content = 9
                self.state = -1
                RESTART_SPR = 13
                if DEFAULT_SETTINGS["play_sounds"]:
                    threading.Thread(target=playsound, args=(PATH + "game-over.mp3",)).start()
                
                for list in self.contents:
                    for cell in list:
                        if not cell.flagged:
                            cell.hidden = False

                return -1

            cells_to_check: Set[Cell] = {cell}
            while len(cells_to_check) > 0:
                cell = cells_to_check.pop()
                if self.check_saturation(cell.x_pos, cell.y_pos):
                    for y in range(-1, 2):
                        for x in range(-1, 2):
                            if 0 <= cell.x_pos + x < DEFAULT_SETTINGS["width"] and 0 <= cell.y_pos + y < DEFAULT_SETTINGS["height"]:
                                adj_cell = self.contents[cell.y_pos +
                                                              y][cell.x_pos + x]
                                if not adj_cell.flagged:
                                    adj_cell.hidden = False
                                    if not self.check_cell(adj_cell.x_pos, adj_cell.y_pos):
                                        if cell.content == 0 or adj_cell.content == 0:
                                            cells_to_check.add(adj_cell)

        except Exception as e:
            raise Exception(e)

    def checkAdjMines(self, x_index: int, y_index: int) -> int:
        """Returns the number of adjacent mines to the cell at the given index.

        Args:
            x_index (int): The x index of the cell.
            y_index (int): The y index of the cell.

        Returns:
            int: The number of mines adjacent to the cell.
        """
        if self.contents[y_index][x_index].content != -1:
            num_of_adj_mines = 0
            # print("\nNew\n")
            for y in range(-1, 2):
                for x in range(-1, 2):
                    if 0 <= x_index + x < DEFAULT_SETTINGS["width"] and 0 <= y_index + y < DEFAULT_SETTINGS["height"]:
                        if self.contents[y_index + y][x_index + x].content == -1:
                            # print("Mine at:", x_index + x, y_index + y)
                            num_of_adj_mines += 1

            return num_of_adj_mines
        else:
            return -1

    def check_saturation(self, x: int, y: int) -> bool:
        """This method checks if there are as much flags around a cell as the number on it.

        Returns:
            bool: True if as much flags or more, False if less or the cell is a mine.
        """
        adj_flags = 0
        if self.contents[y][x].content not in {0, 1, 2, 3, 4, 5, 6, 7, 8}:
            return False
        else:
            for a in range(-1, 2):
                for b in range(-1, 2):
                    if 0 <= x + a < DEFAULT_SETTINGS["width"] and 0 <= y + b < DEFAULT_SETTINGS["height"]:
                        if self.contents[y + b][x + a].flagged:
                            adj_flags += 1

            if self.contents[y][x].content <= adj_flags:
                return True
            else:
                return False

    def check_cell(self, x: int, y: int) -> bool:
        for a in range(-1, 2):
            for b in range(-1, 2):
                if 0 <= x + b < DEFAULT_SETTINGS["width"] and 0 <= y + a < DEFAULT_SETTINGS["height"]:
                    adj_cell = self.contents[y + a][x + b]
                    if adj_cell.hidden:
                        return False

        return True
