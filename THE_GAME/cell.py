import pygame

from globals import (CELL_EDGE, DEFAULT_SETTINGS, DISP, FLAG, CELL, LRB_BORDER, TOP_BORDER)
from sprites import SPRITES


class Cell():

    def __init__(self, x: int = 0, y: int = 0, value: int = 0, hidden: bool = True) -> None:
        self.__hidden: bool = hidden
        self.__flagged: bool = False
        self.__content: int = value
        self.x: int = x
        self.y: int = y

    @property
    def hidden(self) -> bool:
        return self.__hidden

    @hidden.setter
    def hidden(self, __value):
        if self.flagged:
            raise print("Can't dehide a flagged cell")
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
            print("Can't flag a revealed cell")

    @property
    def value(self) -> int:
        return self.__content

    @value.setter
    def value(self, __value) -> None:
        self.__content = __value

    def draw(self) -> None:
        """This method draws a cell onto the display
        """
        self.rect = pygame.Rect(LRB_BORDER + self.x * CELL_EDGE,
                                TOP_BORDER + self.y * CELL_EDGE, CELL_EDGE, CELL_EDGE)
        if self.hidden:
            DISP.blit(SPRITES[FLAG if self.flagged else CELL], self.rect)
        else:
            DISP.blit(SPRITES[self.value], self.rect)
