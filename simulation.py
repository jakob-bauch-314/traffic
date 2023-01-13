
import pygame
import math
import random
import json
import header

PPM = .25  #pixels per meter
TPS = 5  #ticks per second
PLAYBACK_SPEED = 10
BACKGROUND_COLOR = (255, 255, 255)

STREET_WIDTH = 3
LANE_DISTANCE = 2
STREET_COLOR = (200, 200, 200)

STREET_END_RADIUS = 3
STREET_END_COLOR = (255, 0, 0)

STREET_START_RADIUS = 3
STREET_START_COLOR = (0, 0, 255)

JUNCTION_RADIUS = 4
JUNCTION_COLOR = (150, 150, 150)

VEHICLE_RADIUS = 3
VEHICLE_COLOR = (0, 0, 0)
VEHICLE_SPEED = 16.7

# unpacking data ---------------------------------------------

with open('map.json', 'r') as f:
    MAP = header.Map.from_dict(json.load(f))

junctions = MAP.junctions
streets = MAP.streets
street_starts = MAP.street_starts
street_ends = MAP.street_ends
traffic_lights = MAP.traffic_lights

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

class Vehicle:
    def __init__(self, path, length):
        self.path = path
        self.length = length
    def street_and_position_in_street(self):
        sum = 0
        for i in self.path:
            street = streets[i]
            sum += street.length
            if sum >= self.length:
                return i, self.length - (sum - street.length)

def translate_x(x): # translates meters to pixels
    return ((.75 * x) - min_x) * PPM

def translate_y(y):
    return (-(.75 * y) - min_y) * PPM

def draw():
    WIN.fill(BACKGROUND_COLOR)

    for street in streets:
        for i in range(0, len(street.nodes)-1):

            x_start, y_start = street.nodes[i]
            x_end, y_end = street.nodes[i + 1]
            abs = street.lengths[i + 1] - street.lengths[i]

            if abs != 0:

                x_offset = LANE_DISTANCE * (y_end - y_start) / abs
                y_offset = LANE_DISTANCE * (x_end - x_start) / abs

                pygame.draw.line(
                    WIN, STREET_COLOR,
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
    """
    for junction in MAP.junctions:
        pygame.draw.circle(
            WIN, JUNCTION_COLOR,
            (
                translate_x(junction.x),
                translate_y(junction.y)
            ), JUNCTION_RADIUS)
    """
    for street_end in MAP.street_ends:

        street = streets[street_end.street]
        x, y = street.nodes[-1]

        x_start, y_start = x, y
        x_end, y_end = street.nodes[-2]
        abs = street.lengths[-2] - street.lengths[-1]

        if abs != 0:
            x_offset = LANE_DISTANCE * (y_end - y_start) / abs
            y_offset = LANE_DISTANCE * (x_end - x_start) / abs

            pygame.draw.circle(
                WIN, STREET_END_COLOR,
                (
                    translate_x(x) + x_offset,
                    translate_y(y) + y_offset
                ), STREET_END_RADIUS)

    for street_start in MAP.street_starts:

        street = streets[street_start.street]
        x, y = street.nodes[0]

        x_start, y_start = x, y
        x_end, y_end = street.nodes[1]
        abs = street.lengths[1] - street.lengths[0]

        if abs != 0:
            x_offset = LANE_DISTANCE * (y_end - y_start) / abs
            y_offset = LANE_DISTANCE * (x_end - x_start) / abs

            pygame.draw.circle(
                WIN, STREET_START_COLOR,
                (
                    translate_x(x) + x_offset,
                    translate_y(y) + y_offset
                ), STREET_START_RADIUS)

    for vehicle in vehicles:

        # calculate position of vehicle

        idx, position_in_street = vehicle.street_and_position_in_street()
        street = streets[idx]
        i = 0
        for i in range(0, len(street.nodes)):
            if street.lengths[i] > position_in_street:
                i -= 1
                break
        x1, y1 = street.nodes[i]
        x2, y2 = street.nodes[i + 1]
        d = 0
        if (street.lengths[i + 1] - street.lengths[i]) != 0:
            d = (position_in_street - street.lengths[i])/(street.lengths[i+1] - street.lengths[i])
        x = (1-d) * x1 + d * x2
        y = (1-d) * y1 + d * y2

        #calculate offset of vehicle
        x_start, y_start = street.nodes[i]
        x_end, y_end = street.nodes[i + 1]
        abs = street.lengths[i + 1] - street.lengths[i]

        if abs != 0:
            x_offset = LANE_DISTANCE * (y_end - y_start) / abs
            y_offset = LANE_DISTANCE * (x_end - x_start) / abs

            pygame.draw.circle(WIN, VEHICLE_COLOR, (translate_x(x) + x_offset, translate_y(y) + y_offset), VEHICLE_RADIUS)

def update(time):

    destroyed_vehicle_indices = []
    for i, vehicle in enumerate(vehicles):
        vehicle.length += VEHICLE_SPEED * time
        if vehicle.length >= sum([streets[street].length for street in vehicle.path]):
            destroyed_vehicle_indices.append(i)
    for i in sorted(destroyed_vehicle_indices, reverse=True):
        del vehicles[i]

    for street_start in street_starts:
        if (street_start.cool_down <= 0):
            street_start.cool_down = street_start.T

            street = street_start.street
            path = []
            drive = True
            while drive:

                path.append(street)
                if street in [street_end.street for street_end in street_ends]:
                    drive = False

                options = []
                for junction in junctions:
                    if street in junction.incoming_streets:
                        options = junction.outgoing_streets
                        break

                if len(options) == 0:
                    drive = False
                else:
                    street = random.choice(options)

            vehicles.append(Vehicle(path, 0))
        else:
            street_start.cool_down -= time

# game loop -----------------------

run = True
clock = pygame.time.Clock()

while run:

    clock.tick(TPS*PLAYBACK_SPEED)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    update(1/TPS)
    draw()
    pygame.display.update()

pygame.quit()