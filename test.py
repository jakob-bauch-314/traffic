
import pygame
import math
import random

WIDTH, HEIGHT = 1000, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("traffic sim")
unit_size = 100
shift_x, shift_y = WIDTH/2, HEIGHT/2
MAX_SPEED = 0
SPEED_PER_DIST = 0
TPS = 60

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class Crossing:
    def __init__(self, x, y, spawn_rate):
        self.x = x
        self.y = y
        self.spawn_rate = spawn_rate


class Street:
    def __init__(self, start, end, length, choose_rate):
        self.start = start
        self.end = end
        self.length = length
        self.choose_rate = choose_rate

class Vehicle:
    def __init__(self, path, length):
        self.path = path
        self.length = length

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def spawn_vehicle(crossing):
    pass


def update_vehicle(time):
    pass

def translate(x, y):
    return (x * unit_size + shift_x, y * unit_size + shift_y)

def draw_scene():
    for crossing in crossings:
        pygame.draw.circle(WIN, (0, 0, 255), translate(crossing.x, crossing.y), 7)

    for street in streets:
        pygame.draw.line(
            WIN, (255, 0, 0),
            translate(crossings[street.start].x, crossings[street.start].y),
            translate(crossings[street.end].x, crossings[street.end].y),
            5
        )

    for vehicle in vehicles:
        pass

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

crossings = [
    Crossing(-1, 0, 7),
    Crossing(0, 1, 0),
    Crossing(0, -1, 0),
    Crossing(1, 0, 0)
]

streets = [
    Street(0, 1, 1, .5),
    Street(0, 2, 1, .5),
    Street(1, 2, 1, .5),
    Street(1, 3, 1, .5),
    Street(2, 3, 1, 1)
]

vehicles = []

borders = [0, 2, 4, 5]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

run = True
clock = pygame.time.Clock()

while run:

    clock.tick(TPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    WIN.fill((0, 0, 0))
    draw_scene()
    pygame.display.update()

    for vehicle in vehicles:
        update_vehicle(1/TPS)

    for crossing in crossings:
        if (random.random()/TPS > crossing.spawn_rate):
            spawn_vehicle(crossing)

pygame.quit()