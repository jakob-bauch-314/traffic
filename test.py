
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

def translate(x, y, x_offset=0, y_offset=0):
    return (int(x * unit_size + shift_x) + x_offset, int(y * unit_size + shift_y) + y_offset)

def draw_scene():
    for crossing in crossings:
        pygame.draw.circle(WIN, (255, 255, 255), translate(crossing.x, crossing.y), 4)

    for street in streets:
        # unit vector of street, rotated by 90 degrees for street offset
        x_offset = 4 *  (crossings[street.end].y - crossings[street.start].y) / street.length
        y_offset = 4 *  -(crossings[street.end].x - crossings[street.start].x) / street.length

        pygame.draw.line(
            WIN, (255, 255, 255),
            translate(crossings[street.start].x, crossings[street.start].y, x_offset, y_offset),
            translate(crossings[street.end].x, crossings[street.end].y, x_offset, y_offset),
            4
        )

    for vehicle in vehicles:
        pass

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

crossings_amount = 50

crossings = []
for _ in range(0, crossings_amount):
    crossings.append(Crossing((random.random()*WIDTH - shift_x)/unit_size, (random.random()*HEIGHT - shift_y)/unit_size, 0.0))

streets = []
for i in range(0, crossings_amount):
    # all possible streets sorted by length
    all_streets = sorted(list(map(lambda j: Street(i, j, math.sqrt(math.pow(crossings[j].x - crossings[i].x, 2) + math.pow(crossings[j].y - crossings[i].y, 2)), 1), range(0, crossings_amount))), key = lambda street: street.length)
    # add to streets
    streets += all_streets[1:4]


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