import socket
from telnetlib import GA
import threading
from math import floor
from typing import List, Set

import numpy as np
import pygame
from playsound import playsound

pygame.init()


HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

PATH = __file__[:-14] + "files/"
IMAGE_NAMES = ["empty", "cell1", "cell2", "cell3", "cell4",
               "cell5", "cell6", "cell7", "cell8", "clicked_mine", "smile", "shocked", "cool", "dead", "settings", "mine"]

SPR_LIST = [pygame.image.load(PATH + "%s.png" % name)
            for name in IMAGE_NAMES]

FLAG_SPR = pygame.image.load(PATH + "flag.png")
CELL_SPR = pygame.image.load(PATH + "cell.png")
CLICKEDMINE_SPR = pygame.image.load(PATH + "clicked_mine.png")
NOMINE_SPR = pygame.image.load(PATH + "nomine.png")

BG_COLOR = (192, 192, 192)


class Cell():

    def __init__(self, value: int = 0, hidden: bool = True) -> None:
        self.__hidden: bool = hidden
        self.__flagged: bool = False
        self.__content: int = value
        self.x_pos: int = None
        self.y_pos: int = None
        self.debug = False  # Used for debugging

    @property
    def hidden(self) -> bool:
        return self.__hidden

    @hidden.setter
    def hidden(self, __value):
        if self.flagged:
            raise Exception("Can't dehide a flagged cell")
        elif self.content == -1:
            # threading.Thread(target=playsound, args=(PATH + "game-over.mp3",)).start()
            for list in GAME.grid.contents:
                for cell in list:
                    if not cell.flagged:
                        cell.__hidden = False
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
        self.rect = pygame.Rect(GAME.settings["lrb_border_size"] + x * GAME.settings["cell_size"],
                                GAME.settings["top_border_size"] + y * GAME.settings["cell_size"], GAME.settings["cell_size"], GAME.settings["cell_size"])

        if self.debug:
            GAME.gameDisplay.blit(FLAG_SPR, self.rect)
        elif self.hidden:
            if self.flagged:
                GAME.gameDisplay.blit(FLAG_SPR, self.rect)
            else:
                GAME.gameDisplay.blit(CELL_SPR, self.rect)
        else:
            GAME.gameDisplay.blit(
                SPR_LIST[self.content], self.rect)

    def revealCell(self):
        """This method Reveals a cell and checks
        """
        try:
            self.hidden = False    
            if self.content == -1:
                self.content = 9
                GAME.playing = False
                return

            cells_to_check: Set[Cell] = {self}
            while len(cells_to_check) > 0:
                cell = cells_to_check.pop()
                if cell.saturated():
                    for y in range(-1, 2):
                        for x in range(-1, 2):
                            if 0 <= cell.x_pos + x < GAME.settings["width"] and 0 <= cell.y_pos + y < GAME.settings["height"]:
                                adj_cell = GAME.grid.contents[cell.y_pos +
                                                                            y][cell.x_pos + x]
                                if not adj_cell.flagged:
                                    adj_cell.hidden = False
                                    if not adj_cell.checked():
                                        if cell.content == 0 or adj_cell.content == 0:
                                            cells_to_check.add(adj_cell)

        except Exception as e:
            print(e)

    def saturated(self) -> bool:
        """This method checks if there are as much flags around a cell as the number on it.

        Returns:
            bool: True if as much flags or more, False if less or the cell is a mine.
        """
        adj_flags = 0
        if GAME.grid.contents[self.y_pos][self.x_pos].content not in {0, 1, 2, 3, 4, 5, 6, 7, 8}:
            return False
        else:
            for a in range(-1, 2):
                for b in range(-1, 2):
                    if 0 <= self.x_pos + a < GAME.settings["width"] and 0 <= self.y_pos + b < GAME.settings["height"]:
                        if GAME.grid.contents[self.y_pos + b][self.x_pos + a].flagged:
                            adj_flags += 1

            if GAME.grid.contents[self.y_pos][self.x_pos].content <= adj_flags:
                return True
            else:
                return False


    def checked(self) -> bool:
        for y in range(-1, 2):
            for x in range(-1, 2):
                if 0 <= self.x_pos + x < GAME.settings["width"] and 0 <= self.y_pos + y < GAME.settings["height"]:
                    adj_cell = GAME.grid.contents[self.y_pos +
                                                                y][self.x_pos + x]
                    if adj_cell.hidden:
                        return False
        
        return True


class Grid():

    def __init__(self) -> None:
        self.overall_tiles = GAME.settings["width"] * \
            GAME.settings["height"]
        self.num_of_mines = int(GAME.settings["width"] *
                                GAME.settings["height"] * GAME.settings["mines"] / 100)
        self.contents_created: bool = False
        self.contents: List[List[Cell]] = [[Cell() for _ in range(
            GAME.settings["width"])] for _ in range(GAME.settings["height"])]

    def createLayout(self, x: int = None, y: int = None) -> None:
        """Creates the grid layout for the game and stores it in self.contents

        Args:
            x (int, optional): The x location for a safe start. Defaults to None.
            y (int, optional): The y location for a safe start. Defaults to None.
        """
        arr = np.array([Cell for _ in range(self.overall_tiles)])

        for i in range(self.overall_tiles):
            if i < self.num_of_mines:
                arr[i] = Cell(-1)
            else:
                arr[i] = Cell()

        np.random.shuffle(arr)
        self.contents: List[List[Cell]] = list(
            arr.reshape(GAME.settings["height"], GAME.settings["width"]))

        if GAME.settings["easy_start"]:
            for b in range(-1, 2):
                for a in range(-1, 2):
                    if self.contents[y + b][x + a].content != 0:
                        self.contents[y + b][x + a].content = 0

        for y in range(GAME.settings["height"]):
            for x in range(GAME.settings["width"]):
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
                    if 0 <= x_index + x < GAME.settings["width"] and 0 <= y_index + y < GAME.settings["height"]:
                        if self.contents[y_index + y][x_index + x].content == -1:
                            # print("Mine at:", x_index + x, y_index + y)
                            num_of_adj_mines += 1

            return num_of_adj_mines
        else:
            return -1


class Game():

    def __init__(self) -> None:
        self.runing = True
        self.playing = True
        self.flagging = False
        self.settings = {
            "easy_start": True,
            "width": 20,
            "height": 25,
            "mines": 25,  # Percentage
            "open_for_clients": True,
            # Size of one cell (WARNING: make sure to change the images dimension as well)
            "cell_size": 32,
            "top_border_size": 100,  # Size of top border
            "lrb_border_size": 16,  # Left, Right, Bottom border
        }
        self.settings_button = Cell(14, False)
        self.restart_button = Cell(10, False)
        self.settings_pos = (self.settings["width"] - 0.75, -2.75)
        self.drawThread = threading.Thread(target=self.gameLoop)
        self.clientThread = threading.Thread(target=self.client)
        if self.settings["width"] % 2 == 0:
            self.restart_pos = (self.settings["width"] / 2 - 0.5, -2)
        else:
            self.restart_pos = self.settings["width"] / 2


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
        if self.playing:
            if self.settings["top_border_size"] < event.pos[1] < self.disp_height - self.settings["lrb_border_size"] and self.settings["lrb_border_size"] < event.pos[0] < self.disp_width - self.settings["lrb_border_size"]:
                x = floor(x)
                y = floor(y)
                actions = {1: self.reveal,
                        3: self.flag,
                        }
                actions[event.button](x, y)

        if round(x) == round(self.restart_pos[0]) and floor(y) == self.restart_pos[1]:
            self.restart()

    def gameLoop(self):

        while self.runing:

            GAME.gameDisplay.fill(BG_COLOR)
            for y in range(GAME.settings["height"]):
                for x in range(GAME.settings["width"]):
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
                    pass

        pygame.quit()


    def client(self):


        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'minesweeper')
            data = str(s.recv(2048), "ascii")
            print(data)
            myId = int(data.split()[-1])
            while self.runing:
                try:
                    data = str(s.recv(2048), "ascii").split(maxsplit=1)
                    if not data:
                        break
                    
                    match data[0]:

                        case "say":
                            print(data[1])
                            s.sendall(b'aquired by client')

                        case"client":
                            if int(data[1]) == myId:
                                s.sendall(bytes('Successfully Connected to Client %s' % (myId), 'ascii'))

                        case "reveal":
                            data = data[1].split()
                            GAME.reveal(int(data[0]), int(data[1]))

                        case "setting":
                            data = data[1].split()
                            GAME.settings[data[0]] = int(data[1])
                            GAME.restart()


                except Exception as e:
                    print(e)


    def play(self):
        
        self.disp_width = self.settings["cell_size"] * self.settings["width"] + \
            self.settings["lrb_border_size"] * 2  # Display width
        self.disp_height = self.settings["cell_size"] * self.settings["height"] + \
            self.settings["lrb_border_size"] + \
            self.settings["top_border_size"]  # Display height

        self.gameDisplay = pygame.display.set_mode(
            (self.disp_width, self.disp_height))  # Create display
        pygame.display.set_caption("Minesweeper")
        
        self.grid = Grid()
        self.drawThread.start()
        self.clientThread.start()
        if self.settings["open_for_clients"]:
            pass
        # TODO
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
        self.grid = Grid()
        self.playing = True
        self.play()



    def exit(self, event: pygame.event.Event):
        """Exits the game
        """
        self.runing = False




    event_types = {
        pygame.MOUSEBUTTONDOWN: findAffectedCell,
        pygame.MOUSEMOTION: highlightCell,
        pygame.QUIT: exit
    }

GAME = Game()
GAME.play()