import pygame
import math
import random
from pygame import transform, image

# Initialize pygame
pygame.init()

# Game constants
fps = 60
WIDTH = 640
HEIGHT = 480
screen = pygame.display.set_mode([WIDTH, HEIGHT])
clock = pygame.time.Clock()



run = True
while run:
    clock.tick(fps)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False