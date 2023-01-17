
import pygame
import math
import random
import json
import header
import os

# constants - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

PPM = 1  #pixels per meter
TPS = 5  #ticks per second
PLAYBACK_SPEED = 100
BACKGROUND_COLOR = (255, 255, 255)
V_MAX = 13.88
D_MAX = 23
D_MIN = 6.6
SPAWN_TIME = 6

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
TRAFFIC_LIGHT_COLOR = (70, 130, 180)
DRAW_TRAFFIC_LIGHTS = True

RUNTIME = 3600

# functions -----------------------------------


def translate_x(x): # translates meters to pixels
    return ((.5 * x) - min_x) * PPM


def translate_y(y):
    return (-(.5 * y) - min_y) * PPM


class Object:
    pass


class Junction(Object, header.Junction):
    def __init__(self, x, y, incs, outs, connections, traffic_lights):
        super().__init__(x, y, incs, outs, connections, traffic_lights)
    def draw(self):
        pygame.draw.circle(
            WIN, JUNCTION_COLOR,
            (
                translate_x(self.x),
                translate_y(self.y)
            ), JUNCTION_RADIUS)

    @staticmethod
    def from_dict(dic):
        return Junction(dic["x"], dic["y"], dic["incs"], dic["outs"], dic["connections"], dic["traffic_lights"])


class Street(Object, header.Street):
    def __init__(self, nodes, start_junction, start_id, end_junction, end_id):
        super().__init__(nodes, start_junction, start_id, end_junction, end_id)

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
        return Street(dic["nodes"], dic["start_junction_idx"], dic["out_idx"], dic["end_junction_idx"], dic["inc_idx"])


class StreetStart(Object, header.StreetStart):
    def __init__(self, street):
        super().__init__(street)
        self.cool_down = 0
        self.T = SPAWN_TIME

    def draw(self):
        street = streets[self.street_idx]
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

    def update(self, dt):
        if (self.cool_down <= 0):
            self.cool_down = self.T

            # generate vehicle path
            street_idx = self.street_idx
            path = []
            drive = True
            while drive:
                path.append(street_idx)
                junction = junctions[streets[street_idx].end_junction_idx]
                i = streets[street_idx].inc_idx
                options = [street for j, street in enumerate(junction.outs) if junction.connections[i][j]]
                if len(options) == 0:
                    drive = False
                else:
                    street_idx = random.choice(options)

            # create new vehicle
            vehicles.append(Vehicle(path))
        else:
            self.cool_down -= dt

    @staticmethod
    def from_dict(dic):
        return StreetStart(dic["street_idx"])


class StreetEnd(Object, header.StreetEnd):
    def __init__(self, street):
        super().__init__(street)

    def draw(self):
        street = streets[self.street_idx]
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
        return StreetEnd(dic["street_idx"])


class TrafficLight(Object, header.TrafficLight):
    def __init__(self, junction, phases, durations, phase_idx, time):
        super().__init__(junction, phases, durations, phase_idx, time)
        #self.phases = [[[inc_idx == phase_idx for out_idx in range(0, self.out_n)] for inc_idx in range(0, self.inc_n)] for phase_idx in range(0, self.inc_n)]
        #self.durations = [PHASE_TIME for phase_idx in range(0, self.inc_n)]

    def draw(self):
        pygame.draw.circle(WIN, TRAFFIC_LIGHT_COLOR, (translate_x(junctions[self.junction_idx].x), translate_y(junctions[self.junction_idx].y)), TRAFFIC_LIGHT_RADIUS)

    def update(self, dt):
        self.time += dt
        duration = self.durations[self.phase_idx]
        if self.time > duration:
            self.time -= duration
            self.phase_idx += 1
            if self.phase_idx >= len(self.phases):
                self.phase_idx = 0

    @staticmethod
    def from_dict(dic):
        return TrafficLight(dic["junction_idx"], dic["phases"], dic["durations"], dic["phase_idx"], dic["time"])


class Vehicle:
    def __init__(self, path):
        self.path = path
        self.path_idx = 0
        self.pos = 0

    def draw(self):

        street = streets[self.path[self.path_idx]]
        i = 0
        for i in range(0, len(street.nodes)):
            if street.lengths[i] > self.pos:
                break
        i -= 1
        l = street.lengths[i + 1] - street.lengths[i]

        if l!= 0:
            x1, y1 = street.nodes[i]
            x2, y2 = street.nodes[i + 1]
            d = (self.pos - street.lengths[i])/l
            x = (1-d) * x1 + d * x2
            y = (1-d) * y1 + d * y2
            x_offset = LANE_DISTANCE * (y2 - y1) / l
            y_offset = LANE_DISTANCE * (x2 - x1) / l
            pygame.draw.circle(WIN, VEHICLE_COLOR, (translate_x(x) + x_offset, translate_y(y) + y_offset), VEHICLE_RADIUS)


    def update(self, dt):

        street_idx = self.path[self.path_idx]
        street = streets[street_idx]

        d = min(
            [d for d in
             [other.pos - self.pos for other in vehicles if other.path[other.path_idx] == street_idx and other != self]
             if 0 < d < D_MAX],
            default=D_MAX)

        red_light = False
        if self.path_idx < len(self.path) - 1:
            next_street_idx = self.path[self.path_idx + 1]
            next_street = streets[next_street_idx]
            for traffic_light_idx in junctions[street.end_junction_idx].traffic_lights:
                traffic_light = traffic_lights[traffic_light_idx]
                if not traffic_light.phases[traffic_light.phase_idx][street.inc_idx][next_street.out_idx]:
                    red_light = True

        if red_light:
            d = min(d, street.length - self.pos)

        self.pos += dt * (d - D_MIN) * (V_MAX / (D_MAX - D_MIN))

        street_length = streets[self.path[self.path_idx]].length
        if self.pos > street_length:
            self.pos -= street_length
            self.path_idx += 1
            if self.path_idx >= len(self.path):
                self.path_idx -= 1
                return True
        return False

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

def update(dt):

    global vehicle_sum
    global time_step_sum
    global street_lengths
    global time
    global run

    time += dt
    time_step_sum += 1
    if (time > RUNTIME):
        run = False
    vehicle_sum += len(vehicles)

    destroyed_vehicle_indices = []
    for i, vehicle in enumerate(vehicles):
        if vehicle.update(dt):
            destroyed_vehicle_indices.append(i)
    for i in sorted(destroyed_vehicle_indices, reverse=True):
        del vehicles[i]

    for street_start in street_starts:
        street_start.update(dt)

    for traffic_light in traffic_lights:
        traffic_light.update(dt)

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

vehicle_sum = 0
time_step_sum = 0
street_lengths = sum(street.length for street in streets)
time = 0

WIDTH = (map.max_x - map.min_x) * PPM
HEIGHT = (map.max_y - map.min_y) * PPM

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("traffic simumation")

# adjust traffic lights --------------------------------------------

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

print(1000 * (vehicle_sum / time_step_sum) / street_lengths)