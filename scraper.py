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

MID_LON = (MAX_LON + MIN_LON) / 2
MID_LAT = (MAX_LAT + MIN_LAT) / 2

ROAD_TYPES = ["secondary"]
TRAFFIC_LIGHT_IDS = ["35108427", "35108418", "187118378", "186969402", "186969348"]

def y_from_lat(lat):
    return (lat - MID_LAT) / VOLLKREIS * ERDUMFANG


def x_from_lon(lon):
    return (lon - MID_LON) / VOLLKREIS * ERDUMFANG * math.cos(MID_LAT / VOLLKREIS * 2 * math.pi)


def x_y_from_id(id):
    element = next((child for child in root if (child.tag == "node" and child.attrib["id"] == id)), None)
    return x_from_lon(float(element.attrib["lon"])), y_from_lat(float(element.attrib["lat"]))


def get_attribute(element, attribute):
    return next((child.attrib["v"] for child in element if (child.tag == "tag" and child.attrib["k"] == attribute)),
                None)


# download osm file --------------------------------------------------
"""
url = f"https://api.openstreetmap.org/api/0.6/map?bbox={MIN_LON},{MIN_LAT},{MAX_LON},{MAX_LAT}"
urllib.request.urlretrieve(url, "map.osm")
"""
# create map structure -------------------------------------------------:

tree = ET.parse('map.osm')
root = tree.getroot()

roads = [
    (
        [node.attrib["ref"] for node in way if node.tag == "nd"],
        [True] if get_attribute(way, "oneway") == "yes" or get_attribute(way, "junction") == "roundabout"
        else [True, False]
    )
    for way in root if way.tag == "way" and (get_attribute(way, "highway") in ROAD_TYPES)
]

# split roads apart - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

split_roads = []
for i, road in enumerate(roads):
    nodes, directions = road
    size = len(nodes)

    indices = [
        idx
        for idx, node in list(enumerate(nodes))[1:-1]
        if any([node in way[0] for j, way in enumerate(roads) if i != j])
    ]

    split_roads += [(nodes[i:j + 1], directions) for i, j in zip([0] + indices, indices + [size])]
roads = split_roads


# join roads - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

connection_ids = list(set(way[0][-1] for way in roads).union(set(way[0][0] for way in roads)))

for i, connection_id in enumerate(connection_ids):

    if connection_id in TRAFFIC_LIGHT_IDS:
        continue

    connected_roads = \
        [
            (i, True) for i, way in enumerate(roads) if way[0][-1] == connection_id
        ] + [
            (i, False) for i, way in enumerate(roads) if way[0][0] == connection_id
        ]

    if len(connected_roads) != 2:
        continue

    way_A = connected_roads[0]
    way_B = connected_roads[1]

    directions_A = sorted([(dir == way_A[1]) for dir in roads[way_A[0]][1]])
    directions_B = sorted([(dir == way_B[1]) for dir in roads[way_B[0]][1]])

    if directions_A != directions_B:
        continue

    A = roads[way_A[0]][0] \
        if way_A[1] \
        else list(reversed(roads[way_A[0]][0]))
    B = roads[way_B[0]][0] \
        if not way_B[1] \
        else list(reversed(roads[way_B[0]][0]))

    for idx in sorted((connected_roads[0][0], connected_roads[1][0]),
                      reverse=True):  # remove roads that are added together
        del roads[idx]

    roads.append((A + B[1:], directions_A))

# split roads into lanes

junction_ids = list(set(way[0][-1] for way in roads).union(set(way[0][0] for way in roads)))

roads = \
    [
        [(nodes if dir else list(reversed(nodes))) for dir in dirs]
        for nodes, dirs in roads
    ]

indexed_lanes = [
    (road_idx, lane) for road_idx, road in enumerate(roads) for lane in road
]

# streets - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

streets = []
for street_idx, (road_idx, lane) in enumerate(indexed_lanes):
    nodes = [x_y_from_id(id) for id in lane]
    start_junction = junction_ids.index(lane[0])
    out_idx = None
    end_junction = junction_ids.index(lane[-1])
    inc_idx = None

    streets.append(header.Street(nodes, start_junction, out_idx, end_junction, inc_idx))

# junctions, starts and ends - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

junctions = []
street_starts = []
street_ends = []
for junction_id in junction_ids:

    outs = [(street_idx, road_idx, lane)
            for street_idx, (road_idx, lane) in enumerate(indexed_lanes)
            if junction_ids[streets[street_idx].start_junction_idx] == junction_id]

    for out_idx, (street_idx, road_idx, lane) in enumerate(outs):
        streets[street_idx].out_idx = out_idx

    incs = [(street_idx, road_idx, lane)
            for street_idx, (road_idx, lane) in enumerate(indexed_lanes)
            if junction_ids[streets[street_idx].end_junction_idx] == junction_id]

    for inc_idx, (street_idx, road_idx, way) in enumerate(incs):
        streets[street_idx].inc_idx = inc_idx

    x, y = x_y_from_id(junction_id)

    street_starts +=\
        [header.StreetStart(out_street_idx)
         for out_idx, (out_street_idx, out_road_idx, out_lane) in enumerate(outs)
         if len(
            [None for (inc_street_idx, inc_road_idx, inc_lane) in incs if inc_road_idx != out_road_idx]
         ) == 0]

    street_ends +=\
        [header.StreetStart(inc_street_idx)
         for inc_idx, (inc_street_idx, inc_road_idx, inc_lane) in enumerate(incs)
         if len(
            [None for (out_street_idx, out_road_idx, out_lane) in outs if inc_road_idx != out_road_idx]
         ) == 0]

    connections = [
        [out_road_idx != inc_road_idx for (out_street_idx, out_road_idx, out_lane) in outs]
        for (inc_street_idx, inc_road_idx, inc_lane) in incs
    ]

    junctions.append(header.Junction(x, y, [end[0] for end in incs], [start[0] for start in outs], list(connections), []))

# traffic lights - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

traffic_lights = []
for traffic_light_idx, traffic_light_id in enumerate(TRAFFIC_LIGHT_IDS):
    junction_inx = junction_ids.index(traffic_light_id)
    junction = junctions[junction_inx]
    junction.traffic_lights.append(traffic_light_idx)

    traffic_lights.append(
        header.TrafficLight(junction_inx, len(junction.incs), len(junction.outs))
    )

# dump data - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

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