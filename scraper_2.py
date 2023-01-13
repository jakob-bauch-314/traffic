
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
"""
MIN_LON = 11.17910
MIN_LAT = 48.72822
MAX_LON = 11.18303
MAX_LAT = 48.72991
"""
MID_LON = (MAX_LON + MIN_LON)/2
MID_LAT = (MAX_LAT + MIN_LAT)/2

ROAD_TYPES = ["secondary"]

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
                split_ways.append(way_i.slice(start, end + 1))
                end = start

    split_ways.append(way_i.slice(start, len(way_i.nodes)))
ways = split_ways
"""
print("joining ways")
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
"""
print("finding junctions ...")

connections = []
streets = []
index = 0

for way in ways:

    try:
        start = [connection.id for connection in connections].index(way.start())
    except:
        start = index
        connections.append(header.Connection(way.start(), [], [], set()))
        index += 1

    try:
        end = [connection.id for connection in connections].index(way.end())
    except:
        end = index
        connections.append(header.Connection(way.end(), [], [], set()))
        index += 1

    nodes = []
    for id in way.nodes:
        node = next((child for child in root if (child.tag == "node" and child.attrib["id"] == id)), None)
        nodes.append((x(float(node.attrib["lon"])), y(float(node.attrib["lat"]))))

    street_1 = header.Street(nodes)
    streets.append(street_1)

    for incoming_way_index in range(0, len(connections[start].incoming_ways)):
        connections[start].connections.add((incoming_way_index, len(connections[start].outgoing_ways)))
    connections[start].outgoing_ways.append(street_1)

    for outgoing_way_index in range(0, len(connections[end].outgoing_ways)):
        connections[end].connections.add((len(connections[end].incoming_ways), outgoing_way_index))
    connections[end].incoming_ways.append(street_1)


    if not way.oneway:

        street_2 = header.Street(list(reversed(nodes)))
        streets.append(street_2)

        for outgoing_way_index, outgoing_way in enumerate(connections[start].outgoing_ways):
            if outgoing_way == street_1:
                continue
            connections[start].connections.add((len(connections[start].outgoing_ways), outgoing_way_index))
        connections[start].outgoing_ways.append(street_2)

        for incoming_way_index, incoming_way in enumerate(connections[end].incoming_ways):
            if incoming_way == street_1:
                continue
            connections[end].connections.add((incoming_way_index, len(connections[end].incoming_ways)))
        connections[end].incoming_ways.append(street_2)

for connection in connections:
    for incoming_way_index, incoming_way in enumerate(connection.incoming_ways):
        for outgoing_way_index, outgoing_way in enumerate(connection.outgoing_ways):
            connection.connections


junctions = []
for connection in connections:
    node = next((child for child in root if (child.tag == "node" and child.attrib["id"] == connection.id)), None)

    junctions.append(header.Junction(
        x(float(node.attrib["lon"])),
        y(float(node.attrib["lat"])),
        [streets.index(street) for street in connection.incoming_ways],
        [streets.index(street) for street in connection.outgoing_ways],
        list(connection.connections)
    ))

print(junctions)

with open('map.json', 'w') as f:
    json.dump(header.Map(junctions, streets, x(MIN_LON), y(MIN_LAT), x(MAX_LON), y(MAX_LAT)).to_dict(), f)

print("done")