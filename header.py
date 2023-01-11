
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


class Crossing(Empty):
    def __init__(self, x, y):
        self.x = x
        self.y = y



class Street(Empty):
    def __init__(self, start, end, nodes):
        self.start = start
        self.end = end
        self.nodes = nodes

        self.lengt = sum([
            math.sqrt(math.pow(nodes[i + 1][0] - nodes[i][0], 2) + math.pow(nodes[i + 1][1] - nodes[i][1], 2))
            for i in range(0, len(nodes) - 1)
        ])

class Road_end(Empty):
    def __init__(self, crossing):
        self.crossing = crossing

class Traffic_light(Empty):
    def __init__(self, crossing):
        self.crossing = crossing

class Map:
    def __init__(self, crossings, streets, road_ends, traffic_lights, min_x, min_y, max_x, max_y):
        self.crossings = crossings
        self.streets = streets
        self.road_ends = road_ends
        self.traffic_lights = traffic_lights
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

    def to_dict(self):
        return {
            "crossings": [object_to_dict(crossing) for crossing in self.crossings],
            "streets": [object_to_dict(street) for street in self.streets],
            "road_ends": [object_to_dict(road_end) for road_end in self.road_ends],
            "traffic_lights": [object_to_dict(traffic_light) for traffic_light in self.traffic_lights],
            "min_x": self.min_x, "min_y": self.min_y, "max_x": self.max_x, "max_y": self.max_y
        }

    @staticmethod
    def from_dict(dictionary):
        return Map(
            [dict_to_object(crossing, Crossing) for crossing in dictionary["crossings"]],
            [dict_to_object(street, Street) for street in dictionary["streets"]],
            [dict_to_object(road_end, Road_end) for road_end in dictionary["road_ends"]],
            [dict_to_object(traffic_light, Traffic_light) for traffic_light in dictionary["traffic_lights"]],
            dictionary["min_x"],
            dictionary["min_y"],
            dictionary["max_x"],
            dictionary["max_y"]
        )

class Vehicle:
    def __init__(self, path, length):
        self.path = path
        self.length = length


def get_attribute(element, attribute):
    return next((child.attrib["v"] for child in element if (child.tag == "tag" and child.attrib["k"] == attribute)), None)


class Way:
    def __init__(self, nodes, oneway):
        self.nodes = nodes
        self.oneway = oneway
    @staticmethod
    def from_element(element):
        return Way([node.attrib["ref"] for node in element if node.tag == "nd"], get_attribute(element, "oneway") == "yes")

    def __add__(self, other):
        if self.oneway != other.oneway:
            raise Exception("cant join oneway and not-oneway together")
        return Way(self.nodes + other.nodes, self.oneway)

    def __neg__(self):
        return Way(list(reversed(self.nodes)), self.oneway)

    def __sub__(self, other):
        return self + (-other)

    def __iadd__(self, other):
        if (self.oneway != other.oneway):
            raise Exception("cant join oneway and not-oneway together")
        self.nodes += other.nodes

    def __isub__(self, other):
        if (self.oneway != other.oneway):
            raise Exception("cant join oneway and not-oneway together")
        self.nodes += list(reversed(other.nodes))

    def start(self):
        return self.nodes[0]

    def end(self):
        return self.nodes[-1]

    def slice(self, start, end):
        return Way(self.nodes[start:end], self.oneway)