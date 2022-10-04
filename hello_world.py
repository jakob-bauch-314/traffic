
import geopy
import xml.etree.ElementTree as ET

tree = ET.parse('map.osm')
root = tree.getroot()

streets = []

for element in root:
    if (element.tag == "way"):
        name = next((child.attrib["v"] for child in element if (child.tag == "tag" and child.attrib["k"] == "name")), None)
        if (name != None):
            if (not name in streets):
                streets.append(name)
        continue
    if (element.tag == "node"):
        pass

print(len(streets))
for element in streets:
    print (element)