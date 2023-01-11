
import pygame
import math
import random
import json
import header

import scraper

PPM = .25   #pixels per meter
TPS = 60  #ticks per second
PLAYBACK_SPEED = 1
STREET_WIDTH = 3
LANE_DISTANCE = 3

# unpacking data ---------------------------------------------

with open('map.json', 'r') as f:
    MAP = header.Map.from_dict(json.load(f))
crossings = MAP.crossings
streets = MAP.streets
vehicles = []
min_x = MAP.min_x
min_y = MAP.min_y
max_x = MAP.max_x
max_y = MAP.max_y

WIDTH = (MAP.max_x - MAP.min_x) * PPM
HEIGHT = (MAP.max_y - MAP.min_y) * PPM

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("traffic sim")

# functions -----------------------------------

def translate_x(x): # translates meters to pixels
    return ((.75 * x) - min_x) * PPM

def translate_y(y):
    return (-(.75 * y) - min_y) * PPM

def draw():
    """
    for crossing in MAP.crossings:
        pygame.draw.circle(
            WIN, (255, 255, 255),
            (
                translate_x(crossing.x),
                translate_y(crossing.y)
            ), 4)
    """
    for street in MAP.streets:
        for i in range(0, len(street.nodes)-1):

            x_start, y_start = street.nodes[i]
            x_end, y_end = street.nodes[i + 1]
            abs = math.sqrt(math.pow(x_end - x_start, 2) + math.pow(y_end - y_start, 2))

            if abs != 0:

                x_offset = LANE_DISTANCE * (y_end - y_start) / abs
                y_offset = LANE_DISTANCE * (x_end - x_start) / abs

                pygame.draw.line(
                    WIN, (255, 255, 255),
                    (
                        translate_x(x_start) + x_offset,
                        translate_y(y_start) + y_offset
                    ),
                    (
                        translate_x(x_end) + x_offset,
                        translate_y(y_end) + y_offset
                    ),
                    STREET_WIDTH
                )

# game loop -----------------------

run = True
clock = pygame.time.Clock()

while run:

    clock.tick(TPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    WIN.fill((0, 0, 0))
    draw()
    pygame.display.update()

pygame.quit()