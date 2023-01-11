
import urllib.request
import json
import xml.etree.ElementTree as ET
import math
import header

ERDUMFANG = 40000000
VOLLKREIS = 360

MIN_LON = 11.1552
MIN_LAT = 48.7153
MAX_LON = 11.2104
MAX_LAT = 48.7469

MID_LON = (MAX_LON + MIN_LON)/2
MID_LAT = (MAX_LAT + MIN_LAT)/2

ROAD_TYPES = [
    "motorway", "motorway_link",
    "trunk", "trunk_link",
    "primary", "primary_link",
    "secondary", "secondary_link",
    "tertiary", "tertiary_link",
    #"residential", "unclassified"
]

def y(lat):
    return (lat - MID_LAT) / VOLLKREIS * ERDUMFANG

def x(lon):
    return (lon - MID_LON) / VOLLKREIS * ERDUMFANG * math.cos(MID_LAT / VOLLKREIS * 2 * math.pi)

# download osm file --------------------------------------------------
"""
print("downloading osm file ...")
url = f"https://api.openstreetmap.org/api/0.6/map?bbox={MIN_LON},{MIN_LAT},{MAX_LON},{MAX_LAT}"
urllib.request.urlretrieve(url, "map.osm")
"""
# create map structure -------------------------------------------------:

tree = ET.parse('map.osm')
root = tree.getroot()

ways = [header.Way.from_element(way) for way in root if way.tag == "way" and header.get_attribute(way, "highway") in ROAD_TYPES]


print("joining ways")
#join ways together
for i, way_i in enumerate(ways):

    if way_i is None:
        continue

    end_end = []
    end_start = []
    start_end = []
    start_start = []

    for j, way_j in enumerate(ways):
        if i == j or way_j is None:
            continue
        if way_i.end() == way_j.end():
            end_end.append(j)
        if way_i.end() == way_j.start():
            end_start.append(j)
        if way_i.start() == way_j.end():
            start_end.append(j)
        if way_i.start() == way_j.start():
            start_start.append(j)

    found = False
    if len(end_end) == 1 and len(end_start) == 0:
        found = True
        way_i = way_i.slice(0, len(way_i.nodes)-1) - ways[end_end[0]]
        ways[end_end[0]] = None
    if len(end_start) == 1 and len(end_end) == 0:
        found = True
        way_i = way_i.slice(0, len(way_i.nodes)-1) + ways[end_start[0]]
        ways[end_start[0]] = None
    if len(start_end) == 1 and len(start_start) == 0:
        found = True
        way_i = ways[start_end[0]] + way_i.slice(1, len(way_i.nodes))
        ways[start_end[0]] = None
    if len(start_start) == 1 and len(start_end) == 0:
        found = True
        way_i = -ways[start_start[0]] + way_i.slice(1, len(way_i.nodes))
        ways[start_start[0]] = None

    if found:
        ways[i] = None
        ways.append(way_i)

ways = [way for way in ways if way is not None]

#split ways apart
print("splitting ways")

split_ways = []
for i, way_i in enumerate(ways):
    start = 0
    end = len(way_i.nodes) - 1


    for end, node in list(enumerate(way_i.nodes))[1:-1]:
        for j, way_j in enumerate(ways):
            if (i == j):
                continue
            if way_i.nodes[end] in way_j.nodes:  # Verbesserung? (gleich merken)
                pass
                split_ways.append(way_i.slice(start, end + 1))
                end = start

    split_ways.append(way_i.slice(start, len(way_i.nodes)))
ways = split_ways

crossing_ids = []
crossings = []
streets = []
road_ends = []
traffic_lights = []

print("creating json ...")
for way in ways:

    try:
        start = crossing_ids.index(way.start())
    except:
        start = len(crossing_ids)
        crossing_ids.append(way.start())
        node = next((child for child in root if (child.tag == "node" and child.attrib["id"] == way.start())), None)
        crossings.append(header.Crossing(x(float(node.attrib["lon"])), y(float(node.attrib["lat"]))))

    try:
        end = crossing_ids.index(way.end())
    except:
        end = len(crossing_ids)
        crossing_ids.append(way.end())
        node = next((child for child in root if (child.tag == "node" and child.attrib["id"] == way.end())), None)
        crossings.append(header.Crossing(x(float(node.attrib["lon"])), y(float(node.attrib["lat"]))))

    nodes = []
    for id in way.nodes:
        node = next((child for child in root if (child.tag == "node" and child.attrib["id"] == id)), None)
        nodes.append((x(float(node.attrib["lon"])), y(float(node.attrib["lat"]))))

    streets.append(header.Street(start, end, nodes))
    if not way.oneway:
        streets.append(header.Street(end, start, list(reversed(nodes))))

for i, crossing_ids in enumerate(crossing_ids):
    node = next((child for child in root if (child.tag == "node" and child.attrib["id"] == id)), None)
    print(header.get_attribute(node, "crossing"))

map = header.Map(crossings, streets, road_ends, traffic_lights,
    x(MIN_LON),
    y(MIN_LAT),
    x(MAX_LON),
    y(MAX_LAT)
)

with open('map.json', 'w') as f:
    json.dump(map.to_dict(), f)
