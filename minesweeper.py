from math import floor
import os
import socket
import threading
from time import sleep
from tkinter import E
from typing import List, Set

import numpy as np
import pygame
from playsound import playsound

pygame.init()

PATH = os.getcwd() + "/files/"
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

BG_COLOR = (192, 192, 192)

IMAGE_NAMES = ["empty", "cell1", "cell2", "cell3", "cell4",
               "cell5", "cell6", "cell7", "cell8", "clicked_mine", "smile", "shocked", "cool", "dead", "settings", "mine"]

SPR_LIST = [pygame.image.load(PATH + "%s.png" % name)
            for name in IMAGE_NAMES]

FLAG_SPR = pygame.image.load(PATH + "flag.png")
CELL_SPR = pygame.image.load(PATH + "cell.png")
CLICKEDMINE_SPR = pygame.image.load(PATH + "clicked_mine.png")
NOMINE_SPR = pygame.image.load(PATH + "nomine.png")


class Cell():

    def __init__(self, gameId: int, value: int = 0, hidden: bool = True) -> None:
        self.__hidden: bool = hidden
        self.__flagged: bool = False
        self.__content: int = value
        self.x_pos: int = None
        self.y_pos: int = None
        self.gameId = gameId
        self.debug = False  # Used for debugging

    @property
    def hidden(self) -> bool:
        return self.__hidden

    @hidden.setter
    def hidden(self, __value):
        if self.flagged:
            raise Exception("Can't dehide a flagged cell")
        else:
            self.__hidden = __value

    @property
    def flagged(self) -> bool:
        return self.__flagged

    @flagged.setter
    def flagged(self, __value: bool) -> None:
        if self.hidden:
            self.__flagged = __value
        else:
            raise Exception("Can't flag a revealed cell")

    @property
    def content(self) -> int:
        return self.__content

    @content.setter
    def content(self, __value) -> None:
        self.__content = __value

    def drawCell(self, x: int, y: int) -> None:
        """This method draws a cell onto the display

        Args:
            x (int): X coordinate to draw to.
            y (int): Y coordinate to draw to.
        """
        self.rect = pygame.Rect(GAMES[self.gameId].settings["lrb_border_size"] + x * GAMES[self.gameId].settings["cell_size"],
                                GAMES[self.gameId].settings["top_border_size"] + y * GAMES[self.gameId].settings["cell_size"], GAMES[self.gameId].settings["cell_size"], GAMES[self.gameId].settings["cell_size"])

        if self.debug:
            GAMES[self.gameId].gameDisplay.blit(FLAG_SPR, self.rect)
        elif self.hidden:
            if self.flagged:
                GAMES[self.gameId].gameDisplay.blit(FLAG_SPR, self.rect)
            else:
                GAMES[self.gameId].gameDisplay.blit(CELL_SPR, self.rect)
        else:
            GAMES[self.gameId].gameDisplay.blit(
                SPR_LIST[self.content], self.rect)

    def revealCell(self):
        """This method Reveals a cell and checks
        """
        try:
            self.hidden = False
            if self.content == -1:
                self.content = 9
                # threading.Thread(target=playsound, args=(PATH + "game-over.mp3",)).start()
                for list in GAMES[self.gameId].grid.contents:
                    for cell in list:
                        if not cell.flagged:
                            cell.hidden = False

                return

            cells_to_check: Set[Cell] = {self}
            checked_cells: Set[Cell] = set()
            while len(cells_to_check) > 0:
                cell = cells_to_check.pop()
                if cell.saturated():
                    for y in range(-1, 2):
                        for x in range(-1, 2):
                            if 0 <= cell.x_pos + x < GAMES[self.gameId].settings["width"] and 0 <= cell.y_pos + y < GAMES[self.gameId].settings["height"]:
                                adj_cell = GAMES[self.gameId].grid.contents[cell.y_pos +
                                                                            y][cell.x_pos + x]
                                if not adj_cell.flagged:
                                    adj_cell.hidden = False
                                    if adj_cell not in checked_cells:
                                        if cell.content == 0 or adj_cell.content == 0:
                                            cells_to_check.add(adj_cell)


                checked_cells.add(cell)
        except Exception as e:
            print(e)

    def saturated(self) -> bool:
        """This method checks if there are as much flags around a cell as the number on it.

        Returns:
            bool: True if as much flags or more, False if less or the cell is a mine.
        """
        adj_flags = 0
        if GAMES[self.gameId].grid.contents[self.y_pos][self.x_pos].content not in {0, 1, 2, 3, 4, 5, 6, 7, 8}:
            return False
        else:
            for a in range(-1, 2):
                for b in range(-1, 2):
                    if 0 <= self.x_pos + a < GAMES[self.gameId].settings["width"] and 0 <= self.y_pos + b < GAMES[self.gameId].settings["height"]:
                        if GAMES[self.gameId].grid.contents[self.y_pos + b][self.x_pos + a].flagged:
                            adj_flags += 1

            if GAMES[self.gameId].grid.contents[self.y_pos][self.x_pos].content <= adj_flags:
                return True
            else:
                return False


class Grid():

    def __init__(self, gameId: int) -> None:
        self.gameId = gameId
        self.overall_tiles = GAMES[self.gameId].settings["width"] * \
            GAMES[self.gameId].settings["height"]
        self.num_of_mines = int(GAMES[self.gameId].settings["width"] *
                                GAMES[self.gameId].settings["height"] * GAMES[self.gameId].settings["mines"] / 100)
        self.contents_created: bool = False
        self.contents: List[List[Cell]] = [[Cell(self.gameId) for _ in range(
            GAMES[self.gameId].settings["width"])] for _ in range(GAMES[self.gameId].settings["height"])]

    def createLayout(self, x: int = None, y: int = None) -> None:
        """Creates the grid layout for the game and stores it in self.contents

        Args:
            x (int, optional): The x location for a safe start. Defaults to None.
            y (int, optional): The y location for a safe start. Defaults to None.
        """
        arr = np.array([Cell for _ in range(self.overall_tiles)])

        for i in range(self.overall_tiles):
            if i < self.num_of_mines:
                arr[i] = Cell(self.gameId, -1)
            else:
                arr[i] = Cell(self.gameId)

        np.random.shuffle(arr)
        self.contents: List[List[Cell]] = list(
            arr.reshape(GAMES[self.gameId].settings["height"], GAMES[self.gameId].settings["width"]))

        if GAMES[self.gameId].settings["easy_start"]:
            for b in range(-1, 2):
                for a in range(-1, 2):
                    if self.contents[y + b][x + a].content != 0:
                        self.contents[y + b][x + a].content = 0

        for y in range(GAMES[self.gameId].settings["height"]):
            for x in range(GAMES[self.gameId].settings["width"]):
                self.contents[y][x].x_pos = x
                self.contents[y][x].y_pos = y
                self.contents[y][x].content = self.checkAdjMines(x, y)

        self.contents_created = True

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
                    if 0 <= x_index + x < GAMES[self.gameId].settings["width"] and 0 <= y_index + y < GAMES[self.gameId].settings["height"]:
                        if self.contents[y_index + y][x_index + x].content == -1:
                            # print("Mine at:", x_index + x, y_index + y)
                            num_of_adj_mines += 1

            return num_of_adj_mines
        else:
            return -1


class Game():

    def __init__(self, id: int) -> None:
        self.gameId = id
        self.settings = {
            "easy_start": True,
            "width": 20,
            "height": 25,
            "mines": 25,  # Percentage
            "open_for_clients": False,
            # Size of one cell (WARNING: make sure to change the images dimension as well)
            "cell_size": 32,
            "top_border_size": 100,  # Size of top border
            "lrb_border_size": 16,  # Left, Right, Bottom border
        }
        self.settings_button = Cell(self.gameId, 14, False)
        self.restart_button = Cell(self.gameId, 10, False)
        self.settings_pos = (self.settings["width"] - 0.75, -2.75)
        if self.settings["width"] % 2 == 0:
            self.restart_pos = (self.settings["width"] / 2 - 0.5, -2)
        else:
            self.restart_pos = self.settings["width"] / 2

    def listener(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while self.playing:
                    data = conn.recv(1024)
                    if not data:
                        break
                    data = str(data, "ascii").split(", ")
                    print(data)
                    try:
                        if data[2] == "hide":
                            self.grid.contents[int(data[0])][int(
                                data[1])].hidden = True
                        elif data[2] == "reveal":
                            self.grid.contents[int(data[0])][int(
                                data[1])].revealCell()
                        elif data[2] == "flag":
                            self.flag(int(data[0]), int(data[1]))
                        conn.sendall(b"Success!")
                    except Exception as e:
                        print(e)
                        conn.sendall(b"Fail!")

    def highlightCell(self, event: pygame.event.Event):
        x = (event.pos[0] - self.settings["lrb_border_size"]) / \
            self.settings["cell_size"]
        y = (event.pos[1] - self.settings["top_border_size"]) / \
            self.settings["cell_size"]
        if round(x) == round(self.restart_pos[0]) and floor(y) == self.restart_pos[1]:
            self.restart_button.content = 11
        elif self.restart_button.content != 10:
            self.restart_button.content = 10

    def findAffectedCell(self, event: pygame.event.Event = None):
        """Reacts to player left click

        Args:
            event (pygame.event.Event): The event that caused the function to fire.
        """
        x = (event.pos[0] - self.settings["lrb_border_size"]) / \
            self.settings["cell_size"]
        y = (event.pos[1] - self.settings["top_border_size"]) / \
            self.settings["cell_size"]
        if self.settings["top_border_size"] < event.pos[1] < self.disp_height - self.settings["lrb_border_size"] and self.settings["lrb_border_size"] < event.pos[0] < self.disp_width - self.settings["lrb_border_size"]:
            x = floor(x)
            y = floor(y)
            actions = {1: self.reveal,
                       3: self.flag,
                       }
            actions[event.button](x, y)
        elif round(x) == round(self.restart_pos[0]) and floor(y) == self.restart_pos[1]:
            self.restart()


    def reveal(self, x: int, y: int):
        if not self.grid.contents_created:
            self.grid.createLayout(x, y)
        self.grid.contents[y][x].revealCell()

    def flag(self, x: int, y: int):
        """Toggles the flagging option.

        Args:
            event (pygame.event.Event): The event that caused the function to fire.
        """
        if self.grid.contents[y][x].flagged:
            self.grid.contents[y][x].flagged = False
        else:
            self.grid.contents[y][x].flagged = True

    def restart(self):
        self.grid = Grid(self.gameId)

    def exit(self, event: pygame.event.Event):
        """Exits the game
        """
        self.playing = False

    def play(self):
        self.drawThread = threading.Thread(target=self.gameLoop)
        self.drawThread.start()
        if self.settings["open_for_clients"]:
            self.listenThread = threading.Thread(target=self.listener)
            self.listenThread.start()

    def gameLoop(self):

        self.disp_width = self.settings["cell_size"] * self.settings["width"] + \
            self.settings["lrb_border_size"] * 2  # Display width
        self.disp_height = self.settings["cell_size"] * self.settings["height"] + \
            self.settings["lrb_border_size"] + \
            self.settings["top_border_size"]  # Display height

        self.gameDisplay = pygame.display.set_mode(
            (self.disp_width, self.disp_height))  # Create display
        pygame.display.set_caption("Minesweeper")

        self.playing = True
        self.flagging = False
        self.grid = Grid(self.gameId)

        while self.playing:

            GAMES[self.gameId].gameDisplay.fill(BG_COLOR)
            for y in range(GAMES[self.gameId].settings["height"]):
                for x in range(GAMES[self.gameId].settings["width"]):
                    self.grid.contents[y][x].drawCell(x, y)

            self.settings_button.drawCell(
                self.settings_pos[0], self.settings_pos[1])
            self.restart_button.drawCell(
                self.restart_pos[0], self.restart_pos[1])

            pygame.display.update()

            for event in pygame.event.get():
                try:
                    Game.event_types[event.type](self, event)
                except Exception as e:
                    e

        pygame.quit()

    event_types = {
        pygame.MOUSEBUTTONDOWN: findAffectedCell,
        pygame.MOUSEMOTION: highlightCell,
        pygame.QUIT: exit
    }


GAMES: List[Game] = []
GAMES.append(Game(0))
GAMES[0].play()
