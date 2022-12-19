import json
import pygame

PATH = __file__[:-10] + "files/"

with open(PATH[:-6] + "settings.json", "r") as stngs:
    SETTINGS = json.loads(stngs.read())

BLACK = (0, 0, 0)
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

PLAYING: int = 1
WIN: int = 14
LOSE: int = 15

GEAR: int = 13
RESET: int = SMILE

CELL_EDGE: int = 34 * SETTINGS["scale"]
TOP_BORDER: int = 100 * SETTINGS["scale"]
LRB_BORDER: int = 16 * SETTINGS["scale"]

FONT_SIZE = int(12 * SETTINGS["scale"])

HOST = "10.100.102.24"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

DISP_W = CELL_EDGE * SETTINGS["width"] + LRB_BORDER * 2
DISP_H = CELL_EDGE * SETTINGS["height"] + LRB_BORDER + TOP_BORDER

DISP = pygame.display.set_mode((DISP_W, DISP_H))
pygame.display.set_caption("Minesweeper")
