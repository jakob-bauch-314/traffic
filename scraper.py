
import urllib.request
import json
import xml.etree.ElementTree as ET
import math
import header

ERDUMFANG = 40000000
VOLLKREIS = 360

MIN_LON = 11.1641
MIN_LAT = 48.7228
MAX_LON = 11.1981
MAX_LAT = 48.7446

MID_LON = (MAX_LON + MIN_LON)/2
MID_LAT = (MAX_LAT + MIN_LAT)/2

ROAD_TYPES = ["secondary"]

def y_from_lat(lat):
    return (lat - MID_LAT) / VOLLKREIS * ERDUMFANG

def x_from_lon(lon):
    return (lon - MID_LON) / VOLLKREIS * ERDUMFANG * math.cos(MID_LAT / VOLLKREIS * 2 * math.pi)

def x_y_from_id(id):
    element = next((child for child in root if (child.tag == "node" and child.attrib["id"] == id)), None)
    return x_from_lon(float(element.attrib["lon"])), y_from_lat(float(element.attrib["lat"]))

def get_attribute(element, attribute):
    return next((child.attrib["v"] for child in element if (child.tag == "tag" and child.attrib["k"] == attribute)), None)

# download osm file --------------------------------------------------
"""
print("downloading osm file ...")
url = f"https://api.openstreetmap.org/api/0.6/map?bbox={MIN_LON},{MIN_LAT},{MAX_LON},{MAX_LAT}"
urllib.request.urlretrieve(url, "map.osm")
"""
# create map structure -------------------------------------------------:

tree = ET.parse('map.osm')
root = tree.getroot()

ways = [
    (
        [node.attrib["ref"] for node in way if node.tag == "nd"],
        [True] if get_attribute(way, "oneway") == "yes" or get_attribute(way, "junction") == "roundabout"
        else [True, False]
    )
    for way in root if way.tag == "way" and (get_attribute(way, "highway") in ROAD_TYPES)
]

# split ways apart

split_ways = []
for i, way in enumerate(ways):
    nodes, directions = way
    size = len(nodes)

    indices = [
        idx
        for idx, node in list(enumerate(nodes))[1:-1]
        if any([node in way[0] for j, way in enumerate(ways) if i != j])
    ]

    split_ways += [(nodes[i:j+1], directions) for i, j in zip([0] + indices, indices + [size])]

ways = split_ways


joined_ways = []
connection_ids = list(set(way[0][-1] for way in ways).union(set(way[0][0] for way in ways)))

# find traffic light ids
traffic_light_ids = []
for junction_id in connection_ids:

    traffic_signal = False

    """
    lights = 0
    starts = [way for way in ways if way[0][0] == junction_id]
    for start in starts:
        node = next((child for child in root if (child.tag == "node" and child.attrib["id"] == start[0][1])), None)
        if get_attribute(node, "highway") == "traffic_signals" and get_attribute(node, "traffic_signals:direction") == "backward":
            lights += 1

    ends = [way for way in ways if way[0][-1] == junction_id]
    for end in ends:
        node = next((child for child in root if (child.tag == "node" and child.attrib["id"] == end[0][-2])), None)
        if get_attribute(node, "highway") == "traffic_signals" and get_attribute(node, "traffic_signals:direction") == "forward":
            lights += 1

    if lights > 1:
        traffic_signal = True
    
    """
    node = next((child for child in root if (child.tag == "node" and child.attrib["id"] == junction_id)), None)
    if get_attribute(node, "highway") == "traffic_signals" and get_attribute(node, "traffic_signals:direction") is None:
        traffic_signal = True
    if traffic_signal:
        traffic_light_ids.append(junction_id)

print(traffic_light_ids)

# join ways
for i, connection_id in enumerate(connection_ids):

    if connection_id in traffic_light_ids:
        continue

    connected_ways =\
        [
            (i, True) for i, way in enumerate(ways) if way[0][-1] == connection_id
        ] + [
            (i, False) for i, way in enumerate(ways) if way[0][0] == connection_id
        ]

    if len(connected_ways) != 2:
        continue

    way_A = connected_ways[0]
    way_B = connected_ways[1]

    directions_A = sorted([(dir == way_A[1]) for dir in ways[way_A[0]][1]])
    directions_B = sorted([(dir == way_B[1]) for dir in ways[way_B[0]][1]])

    if directions_A != directions_B:
        continue

    A = ways[way_A[0]][0]\
        if way_A[1]\
        else list(reversed(ways[way_A[0]][0]))
    B = ways[way_B[0]][0]\
        if not way_B[1]\
        else list(reversed(ways[way_B[0]][0]))

    for idx in sorted((connected_ways[0][0], connected_ways[1][0]), reverse=True):     # remove ways that are added together
        del ways[idx]

    ways.append((A + B[1:], directions_A))

# slice ways

junction_ids = list(set(way[0][-1] for way in ways).union(set(way[0][0] for way in ways)))

ways = \
    [
        [(way[0] if dir else list(reversed(way[0]))) for dir in way[1]]
        for way in ways
    ]

ways = [
    (i, lane) for i, way in enumerate(ways) for lane in way
]

# streets
streets = [header.Street([x_y_from_id(id) for id in way[1]]) for way in ways]

# junctions, starts and ends
junctions = []
street_starts = []
street_ends = []
for junction_id in junction_ids:

    starts = [(i, way) for i, way in enumerate(ways) if way[1][0] == junction_id]
    ends = [(i, way) for i, way in enumerate(ways) if way[1][-1] == junction_id]

    x, y = x_y_from_id(junction_id)

    street_starts += [header.StreetStart(i) for i, street in starts if len([end for end in ends if end[1][0] != street[0]]) == 0]
    street_ends += [header.StreetEnd(i) for i, street in ends if len([start for start in starts if start[1][0] != street[0]]) == 0]

    connections = [[start[1][0] != end[1][0] for j, end in enumerate(starts)] for i, start in enumerate(ends)]
    junctions.append(header.Junction(x, y, [end[0] for end in ends], [start[0] for start in starts], list(connections)))

# traffic lights
traffic_lights = []
for traffic_light_id in traffic_light_ids:
    junction_inx = junction_ids.index(traffic_light_id)
    junction = junctions[junction_inx]
    traffic_lights.append(header.TrafficLight(junction_inx, len(junction.incoming_streets), len(junction.outgoing_streets)))

# dump data
with open('map.json', 'w') as f:
    json.dump(header.Map(
        junctions,
        streets,
        street_starts,
        street_ends,
        traffic_lights,
        x_from_lon(MIN_LON),
        y_from_lat(MIN_LAT),
        x_from_lon(MAX_LON),
        y_from_lat(MAX_LAT)
    ).to_dict(), f)

import simulation