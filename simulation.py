
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

def translate(x, y):
    return (x * unit_size + shift_x, y * unit_size + shift_y)

class Town:
    def __init__(self, crossings):
        self.crossings = crossings
        self.vehicles = 0
    def update(self):
        for crossing in self.crossings:
            crossing.update()
    def draw(self):
        for crossing in self.crossings:
            crossing.draw()

class Crossing:
    def __init__(self, x, y, streets, spawn_rate, town):
        self.x = x
        self.y = y
        self.streets = streets
        self.spawn_rate = spawn_rate
        self.town = town
    def spawn(self):
        self.town.vehicles += 1
        random.choice(self.streets).vehicles.append(Vehicle(0, 0.01))
    def draw(self):
        for street in self.streets:
            street.draw()
        #pygame.draw.circle(WIN, (0, 0, 255), translate(self.x, self.y), 7)
    def update(self):
        if (self.spawn_rate > 0):
            if (random.random() < self.spawn_rate):
                self.spawn()
        for street in self.streets:
            street.update()

class Street:
    def __init__(self, start, end, vehicles):
        self.start = start
        self.end = end
        self.length = math.sqrt(math.pow((self.end.x - self.start.x), 2) + math.pow((self.end.y - self.start.y), 2))
        self.vehicles = vehicles

    def draw(self):
        pygame.draw.line(WIN, (255, 0, 0), translate(self.start.x, self.start.y), translate(self.end.x, self.end.y), 5)
        for vehicle in self.vehicles:
            x = (vehicle.position / self.length) * (self.end.x - self.start.x) + self.start.x
            y = (vehicle.position / self.length) * (self.end.y - self.start.y) + self.start.y
            pygame.draw.circle(WIN, (255, 255, 255), translate(x, y), 5)

    def update(self):

        deleted_vehicles = []
        for vehicle in self.vehicles:

            if (vehicle.position >= self.length):
                deleted_vehicles.append(vehicle)
            else:
                #min_dist = self.length - vehicle.position
                min_dist = 10
                for other_vehicle in self.vehicles:
                    dist = other_vehicle.position - vehicle.position
                    if (dist > 0 and dist < min_dist):
                        min_dist = dist
                vehicle.update(min_dist)
        for deleted_vehicle in deleted_vehicles:
            self.vehicles.pop(self.vehicles.index(deleted_vehicle))
            if (len(self.end.streets) > 0):
                deleted_vehicle.position = 0
                random.choice(self.end.streets).vehicles.append(deleted_vehicle)
            else:
                self.start.town.vehicles -= 1

class Vehicle:
    def __init__(self, position, desired_speed):
        self.position = position
        self.desired_speed = desired_speed
    def update(self, dist):
        allowed_speed = dist / 50
        speed = min(allowed_speed, self.desired_speed)
        self.position += speed
    def draw(self):
        pass

town = Town([])

crossing1 = Crossing(-3, 0, [], 0.03, town)
crossing2 = Crossing(-2, 0, [], 0, town)
crossing3 = Crossing(0, 1, [], 0, town)
crossing4 = Crossing(0, -1, [], 0, town)
crossing5 = Crossing(2, 0, [], 0, town)
crossing6 = Crossing(3, 0, [], 0, town)

street1 = Street(crossing1, crossing2, [])
street2 = Street(crossing2, crossing3, [])
street3 = Street(crossing2, crossing4, [])
street4 = Street(crossing3, crossing5, [])
street5 = Street(crossing4, crossing5, [])
street6 = Street(crossing5, crossing6, [])
street7 = Street(crossing2, crossing5, [])

crossing1.streets.append(street1)
crossing2.streets.append(street2)
crossing2.streets.append(street3)
crossing3.streets.append(street4)
crossing4.streets.append(street5)
crossing5.streets.append(street6)
crossing2.streets.append(street7)

town.crossings.append(crossing1)
town.crossings.append(crossing2)
town.crossings.append(crossing3)
town.crossings.append(crossing4)
town.crossings.append(crossing5)
town.crossings.append(crossing6)

n = 0
run = True
clock = pygame.time.Clock()
while run:
    clock.tick(TPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    WIN.fill((0, 0, 0))
    town.draw()
    town.update()
    pygame.display.update()

    print(town.vehicles)

pygame.quit()