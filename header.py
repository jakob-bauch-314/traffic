
import pygame
import math

class Empty:
    pass


def object_to_dict(object):
    return dict((key, value) for (key, value) in object.__dict__.items())


def dict_to_object(dictionary, object_class):
    empty_object = Empty()
    for key in dictionary:
        setattr(empty_object, key, dictionary[key])
    empty_object.__class__ = object_class
    return empty_object


class Junction(Empty):
    def __init__(self, x, y, incoming_streets, outgoing_streets, connections):
        self.x = x
        self.y = y
        self.incoming_streets = incoming_streets
        self.outgoing_streets = outgoing_streets
        self.connections = connections


class Street(Empty):
    def __init__(self, nodes):

        self.lengths = [0]
        length = 0
        for i in range(0, len(nodes) - 1):
            length += math.sqrt(math.pow(nodes[i + 1][0] - nodes[i][0], 2) + math.pow(nodes[i + 1][1] - nodes[i][1], 2))
            self.lengths.append(length)
        self.nodes = nodes

        self.length = length

class StreetStart():
    def __init__(self, street):
        self.street = street
        self.cool_down = 0
        self.T = 30

class StreetEnd():
    def __init__(self, street):
        self.street = street

class TrafficLight():
    pass

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

    @staticmethod
    def from_dict(dictionary):
        return Map(
            [dict_to_object(junction, Junction) for junction in dictionary["junctions"]],
            [dict_to_object(street, Street) for street in dictionary["streets"]],
            [dict_to_object(street_start, StreetStart) for street_start in dictionary["street_starts"]],
            [dict_to_object(street_end, StreetEnd) for street_end in dictionary["street_ends"]],
            [dict_to_object(traffic_light, TrafficLight) for traffic_light in dictionary["traffic_lights"]],
            dictionary["min_x"],
            dictionary["min_y"],
            dictionary["max_x"],
            dictionary["max_y"]
        )