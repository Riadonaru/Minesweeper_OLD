import json
import pygame


PATH = __file__[:-10] + "files/"
IMAGE_NAMES = ["empty", "cell1", "cell2", "cell3", "cell4",
                "cell5", "cell6", "cell7", "cell8", "clicked_mine",
                "smile", "shocked", "cool", "dead", "settings", "mine"]

SPR_LIST = [pygame.image.load(PATH + "%s.png" % name)
            for name in IMAGE_NAMES]

FLAG_SPR = pygame.image.load(PATH + "flag.png")
CELL_SPR = pygame.image.load(PATH + "cell.png")
CLICKEDMINE_SPR = pygame.image.load(PATH + "clicked_mine.png")
NOMINE_SPR = pygame.image.load(PATH + "nomine.png")
GAME_STATE_IMAGES = [pygame.image.load(
    PATH + "%s.png" % name) for name in ("win", "game_over")]

BG_COLOR = (192, 192, 192)

INPUT_SOURCE: str = "server"

RESTART_SPR: int = 10
SHOCKED: int = 11
COOL: int = 12
NAUTIOUS: int = 13
SETTINGS_SPR = 14
FLAGGED_CELLS: int = 0

with open(PATH[:-6] + "settings.json", "r") as stngs:
    DEFAULT_SETTINGS = json.loads(stngs.read())


DISP_W = DEFAULT_SETTINGS["cell_size"] * DEFAULT_SETTINGS["width"] + \
    DEFAULT_SETTINGS["lrb_border_size"] * 2  # Display width
DISP_H = DEFAULT_SETTINGS["cell_size"] * DEFAULT_SETTINGS["height"] + \
    DEFAULT_SETTINGS["lrb_border_size"] + \
    DEFAULT_SETTINGS["top_border_size"]  # Display height

DISP = pygame.display.set_mode(
    (DISP_W, DISP_H))  # Create display
pygame.display.set_caption("Minesweeper")

