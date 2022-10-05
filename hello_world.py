
#import geopy
import xml.etree.ElementTree as ET

# constants

accepted_road_types = [
    "motorway",
    "trunk",
    "primary",
    "secondary",
    #"tertiary",
    #"unclassified"
]

# definitions

def find(element, value):
    return next((child.attrib["v"] for child in element if (child.tag == "tag" and child.attrib["k"] == value)), None)

class node():

    def __init__(self, longitude, latitude, id, streets):
        self.longitude = longitude
        self.latitude = latitude
        self.id = id

        self.streets = streets

    @staticmethod
    def fromId(id):
        node_element = next((child for child in root if (child.tag == "node" and child.attrib["id"] == id)), None)
        return node(
            node_element.attrib["lon"],
            node_element.attrib["lat"],
            id,
            []
        )

class way():
    def __init__(self, name, nodes):
        self.name = name
        self.nodes = nodes

    @staticmethod
    def fromElement(element):
        return way(
            find(element, "name"),
            [node.attrib["ref"] for node in element if node.tag == "nd"]
        )

    def __add__(self, other):
        name = None

        if self.name is not None:
            if other.name is not None:
                name = f"{self.name}, {other.name}"
            else:
                name = other.name
        else:
            if other.name is not None:
                name = other.name
            else:
                name = None

        return way(
            name,
            self.nodes + other.nodes
        )
# start

tree = ET.parse('map.osm')
root = tree.getroot()

# sort file out
ways = [way.fromElement(element) for element in root if element.tag == "way" and find(element, "highway") in accepted_road_types]
intersections = []

for currentWay in ways:
    for currentNode in currentWay.nodes:
        for otherWay in ways:
            for otherNode in otherWay.nodes:
                if otherNode == currentNode:
                    intersections.append(node.fromId(currentNode))

for intersection in intersections:
    print(intersection.longitude, intersection.latitude)