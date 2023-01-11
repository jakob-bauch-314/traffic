
import pygame
import math
import random
import json
import header

PPM = .25  #pixels per meter
TPS = 60 #ticks per second
PLAYBACK_SPEED = 1
STREET_WIDTH = 1
LANE_DISTANCE = 0

with open('map.json', 'r') as f:
    MAP = header.Map.from_dict(json.load(f))

WIDTH = (MAP.max_x - MAP.min_x) * PPM
HEIGHT = (MAP.max_y - MAP.min_y) * PPM

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("traffic sim")

def translate_x(x): # translates meters to pixels
    return (x - MAP.min_x) * PPM

def translate_y(y):
    return (-y - MAP.min_y) * PPM

def draw():
    for crossing in MAP.crossings:
        pygame.draw.circle(
            WIN, (255, 255, 255),
            (
                translate_x(crossing.x),
                translate_y(crossing.y)
            ), 4)

    for street in MAP.streets:
        # unit vector of street, rotated by 90 degrees for street offset
        x_offset = LANE_DISTANCE * (MAP.crossings[street.end].y - MAP.crossings[street.start].y) / street.length
        y_offset = LANE_DISTANCE * -(MAP.crossings[street.end].x - MAP.crossings[street.start].x) / street.length

        pygame.draw.line(
            WIN, (255, 255, 255),
            (
                translate_x(MAP.crossings[street.start].x) + x_offset,
                translate_y(MAP.crossings[street.start].y) + y_offset
            ),
            (
                translate_x(MAP.crossings[street.end].x) + x_offset,
                translate_y(MAP.crossings[street.end].y) + y_offset
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