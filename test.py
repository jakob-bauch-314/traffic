
import xml.etree.ElementTree as ET
import json

tree = ET.parse('map.osm')
root = tree.getroot()

class way():
    def __init__(self, name, nodes):
        self.name = name
        self.nodes = nodes

    @staticmethod
    def fromElement(element):
        return way(
            next((child.attrib["v"] for child in element if (child.tag == "tag" and child.attrib["k"] == "name")), None),
            [node.attrib["ref"] for node in element if node.tag == "nd"]
        )