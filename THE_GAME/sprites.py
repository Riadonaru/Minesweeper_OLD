import pygame
from globals import BG_COLOR, DEFAULT_SETTINGS, PATH


class Spritesheet(object):

    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert_alpha()

        
    def getImage(self, x, width, height, scale: int = 1):
        image = pygame.Surface((width, height)).convert_alpha()
        image.fill(BG_COLOR)
        image.blit(self.sheet, (0, 0), (x * width + 1, 1, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey(BG_COLOR)
        return image
    
SPRITES = [Spritesheet(PATH + "spritesheet.png").getImage(x, 34, 34, DEFAULT_SETTINGS["scale"]) for x in range(19)]
WIN_LOSE = [pygame.image.load(PATH + "%s.png" % name) for name in ("win", "game_over")]
