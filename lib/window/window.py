import pygame
import os
pygame.init()

class Window:
    def __init__(self, size, caption):
        self.size = size
        self.screen = pygame.display.set_mode(size, pygame.SCALED | pygame.DOUBLEBUF, vsync = 1)
        pygame.display.set_caption(caption)
        icon_image = pygame.image.load(os.path.join(os.path.join(os.path.join("res"), "image"),"truther_icon.png"))
        pygame.display.set_icon(icon_image)
        self.clock = pygame.time.Clock()