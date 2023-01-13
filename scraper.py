
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


# join ways

joined_ways = []
connections_but_not_junctions = []
connection_ids = list(set(way[0][-1] for way in ways).union(set(way[0][0] for way in ways)))

for i, connection_id in enumerate(connection_ids):
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

    connections_but_not_junctions.append(i)

    for idx in sorted((connected_ways[0][0], connected_ways[1][0]), reverse=True):     # remove ways that are added together
        del ways[idx]

    ways.append((A + B[1:], directions_A))

junction_ids = [id for i, id in enumerate(connection_ids) if i not in connections_but_not_junctions]

junction_ids = list(set(way[0][-1] for way in ways).union(set(way[0][0] for way in ways)))

# find junctions

ways = \
    [
        [(way[0] if dir else list(reversed(way[0]))) for dir in way[1]]
        for way in ways
    ]

ways = [
    (i, lane) for i, way in enumerate(ways) for lane in way
]

streets = [header.Street([x_y_from_id(id) for id in way[1]]) for way in ways]

junctions = []
street_starts = []
street_ends = []
traffic_lights = []
for junction_id in junction_ids:

    starts = [(i, way) for i, way in enumerate(ways) if way[1][0] == junction_id]
    ends = [(i, way) for i, way in enumerate(ways) if way[1][-1] == junction_id]

    connections = set()

    for i, start in enumerate(starts):
        for j, end in enumerate(ends):
            if start[1] != end[1]:
                connections.add((i, j))

    x, y = x_y_from_id(junction_id)

    for (i, street) in starts:
        if len([end for end in ends if end[1][0] != street[0]]) == 0:
            street_starts.append(header.StreetStart(i))

    for (i, street) in ends:
        if len([start for start in starts if start[1][0] != street[0]]) == 0:
            street_ends.append(header.StreetStart(i))

    junctions.append(header.Junction(x, y, [end[0] for end in ends], [start[0] for start in starts], list(connections)))

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

print("done")

import simulation