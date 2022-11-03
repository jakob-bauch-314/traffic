
#import geopy
import xml.etree.ElementTree as ET
import json

# constants

LON0 = 0
LON1 = 1
LAT0 = 0
LAT1 = 1

accepted_road_types = [
    "motorway",
    "trunk",
    "primary",
    "secondary",
    "tertiabry",
    "residential"
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
    def fromId(id, streets):
        node_element = next((child for child in root if (child.tag == "node" and child.attrib["id"] == id)), None)
        return node(
            node_element.attrib["lon"],
            node_element.attrib["lat"],
            id,
            streets
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

#make graph

for i in range(0, len(ways)):
    currentWay = ways[i]
    for currentNode in currentWay.nodes:
        for j in range(0, i):
            otherWay = ways[j]
            for otherNode in otherWay.nodes:
                if otherNode == currentNode:
                    intersection = next((intersection for intersection in intersections if (intersection.id == currentNode)), None)
                    if intersection is None:
                        intersections.append(node.fromId(currentNode, [currentWay, otherWay]))
                    else:
                        if currentWay not in intersection.streets:
                            intersection.streets.append(currentWay) # old way would be there already anyway


#cut ways apart
for intersection in intersections:
    new_streets = []
    for street in intersection.streets:
        index = street.nodes.index(intersection.id)
        if index == 0:
            new_streets.append(street)
            continue
        if index == len(intersection.streets):
            new_streets.append(street)
            continue
        first_part = way(street.name, street.nodes[:index])
        second_part = way(street.name, street.nodes[index:])
        new_streets.append(first_part)
        new_streets.append(second_part)

for intersection in intersections:
    print(intersection.latitude, intersection.longitude)
    for street in intersection.streets:
        print(street.name)