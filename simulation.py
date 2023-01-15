
import pygame
import math
import random
import json
import header

PPM = .25  #pixels per meter
TPS = 12  #ticks per second
PLAYBACK_SPEED = 5
BACKGROUND_COLOR = (255, 255, 255)

STREET_WIDTH = 3
LANE_DISTANCE = 2
STREET_COLOR = (200, 200, 200)
DRAW_STREETS = True

STREET_END_RADIUS = 3
STREET_END_COLOR = (255, 0, 0)
DRAW_STREET_ENDS = False

STREET_START_RADIUS = 3
STREET_START_COLOR = (0, 0, 255)
DRAW_STREET_STARTS = False

JUNCTION_RADIUS = 4
JUNCTION_COLOR = (150, 150, 150)
DRAW_JUNCTIONS = False

VEHICLE_RADIUS = 2
VEHICLE_COLOR = (0, 0, 0)
DRAW_VEHICLES = True

TRAFFIC_LIGHT_RADIUS = 4
TRAFFIC_LIGHT_COLOR = (0, 100, 255)
DRAW_TRAFFIC_LIGHTS = True

V_MAX = 16.7
D_MAX = 50
T_MAX = D_MAX / V_MAX
SPAWN_TIME = 5

# functions -----------------------------------


def translate_x(x): # translates meters to pixels
    return ((x) - min_x) * PPM


def translate_y(y):
    return (-(y) - min_y) * PPM


class Object:
    pass


class Junction(Object, header.Junction):
    def __init__(self, x, y, incoming_streets, outgoing_streets, connections):
        super().__init__(x, y, incoming_streets, outgoing_streets, connections)
    def draw(self):
        pygame.draw.circle(
            WIN, JUNCTION_COLOR,
            (
                translate_x(self.x),
                translate_y(self.y)
            ), JUNCTION_RADIUS)

    @staticmethod
    def from_dict(dic):
        return Junction(dic["x"], dic["y"], dic["incoming_streets"], dic["outgoing_streets"], dic["connections"])


class Street(Object, header.Street):
    def __init__(self, nodes):
        super().__init__(nodes)

    def draw(self):
        for i in range(0, len(self.nodes) - 1):

            x_start, y_start = self.nodes[i]
            x_end, y_end = self.nodes[i + 1]
            abs = self.lengths[i + 1] - self.lengths[i]

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

    @staticmethod
    def from_dict(dic):
        return Street(dic["nodes"])


class StreetStart(Object, header.StreetStart):
    def __init__(self, street):
        super().__init__(street)
        self.cool_down = 0
        self.T = 10

    def draw(self):
        street = streets[self.street]
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

    def update(self, time):
        if (self.cool_down <= 0):
            self.cool_down = self.T

            street = self.street
            path = []
            drive = True
            while drive:

                path.append(street)
                if street in [street_end.street for street_end in street_ends]:
                    drive = False

                options = []
                for junction in junctions:
                    try:
                        i = junction.incoming_streets.index(street)
                        options = [street for j, street in enumerate(junction.outgoing_streets) if junction.connections[i][j]]
                        break
                    except ValueError:
                        pass

                if len(options) == 0:
                    drive = False
                else:
                    street = random.choice(options)

            vehicles.append(Vehicle(path, 0))
        else:
            self.cool_down -= time

    @staticmethod
    def from_dict(dic):
        return StreetStart(dic["street"])


class StreetEnd(Object, header.StreetEnd):
    def __init__(self, street):
        super().__init__(street)

    def draw(self):
        street = streets[self.street]
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

    @staticmethod
    def from_dict(dic):
        return StreetEnd(dic["street"])


class TrafficLight(Object, header.TrafficLight):
    def __init__(self, junction, inc_n, out_n):
        super().__init__(junction, inc_n, out_n)
        self.phases = [[[i == k for i in range(0, self.inc_n)] for j in range(0, self.out_n)] for k in range(0, self.inc_n)]
        self.durations = [60 for k in range(0, self.inc_n)]
        self.phase = 0
        self.time = 0

    def draw(self):
        pygame.draw.circle(WIN, TRAFFIC_LIGHT_COLOR, (translate_x(junctions[self.junction].x), translate_y(junctions[self.junction].y)), TRAFFIC_LIGHT_RADIUS)

    def update(self, time):
        self.time += time
        duration = self.durations[self.phase]
        if self.time > duration:
            self.time -= duration
            self.phase += 1
            if self.phase >= len(self.phases):
                self.phase = 0

    @staticmethod
    def from_dict(dic):
        return TrafficLight(dic["junction"], dic["inc_n"], dic["out_n"])


class Vehicle:
    def __init__(self, path, length):
        self.path = path
        self.length = length
        self.street = 0
        self.position_in_street = 0

    def street_and_position_in_street(self):
        sum = 0
        i = 0
        for i in self.path:
            street = streets[i]
            sum += street.length
            if sum >= self.length:
                break
        return i, self.length - (sum - street.length)

    def draw(self):
        idx, position_in_street = self.street_and_position_in_street()
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

        x_start, y_start = street.nodes[i]
        x_end, y_end = street.nodes[i + 1]
        abs = street.lengths[i + 1] - street.lengths[i]

        if abs != 0:
            x_offset = LANE_DISTANCE * (y_end - y_start) / abs
            y_offset = LANE_DISTANCE * (x_end - x_start) / abs

            pygame.draw.circle(WIN, VEHICLE_COLOR, (translate_x(x) + x_offset, translate_y(y) + y_offset), VEHICLE_RADIUS)

    def update(self, time):

        street, position_in_street = self.street_and_position_in_street()
        try:
            traffic_light = traffic_lights[[traffic_light.junction for traffic_light in traffic_lights].index(next(i for i, junction in enumerate(junctions) if street in junction.incoming_streets))]
        except:
            pass
        min_dist = \
            min([d for d in [
                pair[1] - position_in_street for pair in [
                    other_vehicle.street_and_position_in_street() for other_vehicle in vehicles]
                if pair[0] == street]
                 if 0 < d < D_MAX], default=D_MAX)

        self.length += (min_dist / T_MAX) * time

        return self.length >= sum([streets[street].length for street in self.path])

def dict_to_object(dictionary, object_class):
    empty_object = Object()
    for key in dictionary:
        setattr(empty_object, key, dictionary[key])
    empty_object.__class__ = object_class
    return empty_object


class Map(header.Map):
    def __init__(self, junctions, streets, street_starts, street_ends, traffic_lights, min_x, min_y, max_x, max_y, vehicles):
        super().__init__(junctions, streets, street_starts, street_ends, traffic_lights, min_x, min_y, max_x, max_y)
        self.vehicles = vehicles

    @staticmethod
    def from_dict(dictionary):
        return Map(
            [Junction.from_dict(dic) for dic in dictionary["junctions"]],
            [Street.from_dict(dic) for dic in dictionary["streets"]],
            [StreetStart.from_dict(dic) for dic in dictionary["street_starts"]],
            [StreetEnd.from_dict(dic) for dic in dictionary["street_ends"]],
            [TrafficLight.from_dict(dic) for dic in dictionary["traffic_lights"]],
            dictionary["min_x"],
            dictionary["min_y"],
            dictionary["max_x"],
            dictionary["max_y"],
            []
        )

def draw():
    WIN.fill(BACKGROUND_COLOR)

    if DRAW_STREETS:
        for street in streets:
            street.draw()

    if DRAW_JUNCTIONS:
        for junction in junctions:
            junction.draw()

    if DRAW_STREET_ENDS:
        for street_end in street_ends:
            street_end.draw()

    if DRAW_STREET_STARTS:
        for street_start in street_starts:
            street_start.draw()

    if DRAW_VEHICLES:
        for vehicle in vehicles:
            vehicle.draw()

    if DRAW_TRAFFIC_LIGHTS:
        for traffic_light in traffic_lights:
            traffic_light.draw()


def update(time):

    destroyed_vehicle_indices = []
    for i, vehicle in enumerate(vehicles):
        if vehicle.update(time):
            destroyed_vehicle_indices.append(i)
    for i in sorted(destroyed_vehicle_indices, reverse=True):
        del vehicles[i]

    for street_start in street_starts:
        street_start.update(time)

    for traffic_light in traffic_lights:
        traffic_light.update(time)

# unpacking data ---------------------

with open('map.json', 'r') as f:
    map = Map.from_dict(json.load(f))

junctions = map.junctions
streets = map.streets
street_starts = map.street_starts
street_ends = map.street_ends
traffic_lights = map.traffic_lights
vehicles = map.vehicles

min_x = map.min_x
min_y = map.min_y
max_x = map.max_x
max_y = map.max_y

WIDTH = (map.max_x - map.min_x) * PPM
HEIGHT = (map.max_y - map.min_y) * PPM

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("traffic sim")

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