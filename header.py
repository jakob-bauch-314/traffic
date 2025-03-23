
import pygame
import math

def object_to_dict(object):
    return dict((key, value) for (key, value) in object.__dict__.items())

class Junction:
    def __init__(self, x, y, incs, outs, connections, traffic_lights):
        self.x = x
        self.y = y
        self.incs = incs
        self.outs = outs
        self.connections = connections
        self.traffic_lights = traffic_lights


class Street:
    def __init__(self, nodes, start_junction_idx, out_idx, end_junction_idx, inc_idx):

        self.lengths = [0]
        length = 0
        for i in range(0, len(nodes) - 1):
            length += math.sqrt(math.pow(nodes[i + 1][0] - nodes[i][0], 2) + math.pow(nodes[i + 1][1] - nodes[i][1], 2))
            self.lengths.append(length)
        self.length = length
        self.start_junction_idx = start_junction_idx
        self.out_idx = out_idx
        self.end_junction_idx = end_junction_idx
        self.inc_idx = inc_idx

        self.nodes = nodes


class StreetStart:
    def __init__(self, street_idx):
        self.street_idx = street_idx

class StreetEnd:
    def __init__(self, street_idx):
        self.street_idx = street_idx


class TrafficLight:
    def __init__(self, junction_idx, phases, durations, phase_idx, time):
        self.junction_idx = junction_idx
        self.phases = phases
        self.durations = durations
        self.phase_idx = phase_idx
        self.time = time

class Map:
    def __init__(self, junctions, streets, street_starts, street_ends, traffic_lights, min_x, min_y, max_x, max_y):
        self.junctions = junctions
        self.streets = streets
        self.street_ends = street_ends
        self.street_starts = street_starts
        self.traffic_lights = traffic_lights
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

    def to_dict(self):
        return {
            "junctions": [object_to_dict(junction) for junction in self.junctions],
            "streets": [object_to_dict(street) for street in self.streets],
            "street_starts": [object_to_dict(street_start) for street_start in self.street_starts],
            "street_ends": [object_to_dict(street_end) for street_end in self.street_ends],
            "traffic_lights": [object_to_dict(traffic_light) for traffic_light in self.traffic_lights],
            "min_x": self.min_x, "min_y": self.min_y, "max_x": self.max_x, "max_y": self.max_y
        }