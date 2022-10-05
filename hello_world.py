
import geopy
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

class way():
    def __init__(self, element):
        self.nodes = [node.attrib["ref"] for node in element if node.tag == "nd"]
        self.name = find(element, "name")

# start

tree = ET.parse('map.osm')
root = tree.getroot()

# sort file out
ways = [way(element) for element in root if element.tag == "way" and find(element, "highway") in accepted_road_types]

for currentWay in ways:
    for currentNode in currentWay.nodes:
        for otherWay in ways:
            for otherNode in otherWay.nodes:
                if otherNode == currentNode:
                    print(
                        f"{currentWay.name} intersects {otherWay.name} at {currentNode}"
                    )

print("done")