import pygame

from globals import (CELL_SPR, DEFAULT_SETTINGS, DISP, FLAG_SPR,
                     SPR_LIST)


class Cell():

    def __init__(self, x: int = 0, y: int = 0, value: int = 0, hidden: bool = True) -> None:
        self.__hidden: bool = hidden
        self.__flagged: bool = False
        self.__content: int = value
        self.x_pos: int = x
        self.y_pos: int = y

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
    def content(self) -> int:
        return self.__content

    @content.setter
    def content(self, __value) -> None:
        self.__content = __value

    def drawCell(self) -> None:
        """This method draws a cell onto the display
        """
        self.rect = pygame.Rect(DEFAULT_SETTINGS["lrb_border_size"] + self.x_pos * DEFAULT_SETTINGS["cell_size"],
                                DEFAULT_SETTINGS["top_border_size"] + self.y_pos * DEFAULT_SETTINGS["cell_size"], DEFAULT_SETTINGS["cell_size"], DEFAULT_SETTINGS["cell_size"])
        if self.hidden:
            if self.flagged:
                DISP.blit(FLAG_SPR, self.rect)
            else:
                DISP.blit(CELL_SPR, self.rect)
        else:
            DISP.blit(
                SPR_LIST[self.content], self.rect)
