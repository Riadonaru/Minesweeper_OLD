import json
import pygame

PATH = __file__[:-10] + "files/"
with open(PATH[:-6] + "settings.json", "r") as stngs:
    DEFAULT_SETTINGS = json.loads(stngs.read())


BG_COLOR = (192, 192, 192)

CELL: int = -5
FLAG: int = -4
CLICKED_MINE: int = -3
NOMINE: int = -2
MINE: int = -1
SMILE: int = 9
SHOCKED: int = 10
COOL: int = 11
DEAD: int = 12
SETTINGS_SPR = 13
RESET_SPR: int = SMILE
CELL_EDGE: int = 34 * DEFAULT_SETTINGS["scale"]
TOP_BORDER: int = 100 * DEFAULT_SETTINGS["scale"]
LRB_BORDER: int = 16 * DEFAULT_SETTINGS["scale"]



DISP_W = CELL_EDGE * DEFAULT_SETTINGS["width"] + LRB_BORDER * 2
DISP_H = CELL_EDGE * DEFAULT_SETTINGS["height"] + LRB_BORDER + TOP_BORDER

DISP = pygame.display.set_mode((DISP_W, DISP_H))
pygame.display.set_caption("Minesweeper")
