#!/usr/bin/env python2

import json
import numpy as np
import matplotlib.pyplot as plt
import itertools
import math
import pickle
import time

from random import randint
from scipy.spatial import KDTree
from os import mkdir as mkdir_os
from collections import defaultdict

schools_path           = "../dataset/schools.geojson"              # Path to schools geojson
health_facilities_path = "../dataset/health-facilities.geojson"    # Path to health facilities geojson

schools_coord = [] # schools coord 
health_coord  = [] # health coord

healths = []
schools = []

def read_health():
    with open(health_facilities_path) as f:
        data = json.load(f)

    for feature in data["features"]:
        health_coord.append(feature['geometry']['coordinates'])
        healths.append(feature['properties']['name'])

def read_schools():
    with open(schools_path) as f:
        data = json.load(f)

    for feature in data["features"]:
        schools_coord.append(feature['geometry']['coordinates'])
        schools.append(feature['properties']['name'])

def transform_to_3d(point):
    lon = math.radians(point[0])
    lat = math.radians(point[1])
    R = 6371
    x = R * math.sin(lat) * math.sin(lon)
    y = R * math.cos(lat)
    z = R * math.sin(lat) * math.cos(lon)

    return [x, y, z]

# Great circle distance - https://en.wikipedia.org/wiki/Great-circle_distance
def geodesic_distance(point1, point2):
    lon1  = point1[0]
    lat1  = point1[1]
    lon2  = point2[0]
    lat2  = point2[1]
    earth = 6371 # Earth Radius

    dphi    = math.radians(lat2-lat1)
    dlambda = math.radians(lon2-lon1)

    a  = math.sin(dphi/2)    * math.sin(dphi/2)
    b  = math.sin(dlambda/2) * math.sin(dlambda/2)
    b *= (math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)))
    a += b

    return 2 * earth * math.asin(math.sqrt(a))


def euclidian_distance(point1, point2):
    return (point1[0] - point2[0]) **2 + (point1[1] - point2[1]) **2 + (point1[2] - point2[2])**2;

read_health()
read_schools()

all_points = []

for idx, h in enumerate(health_coord):
    all_points.append([h, 0, idx])

for idx, s in enumerate(schools_coord):
    all_points.append([s, 1, idx])


start      = time.time()
all_coords = [point[0] for point in all_points]
kd_tree    = KDTree(all_coords)
end        = time.time()

print "Built KDTree in  " + str(end-start) + " s"


def hf_compute(radius, hospital_index):
    h_coord    = [health_coord[hospital_index][1], health_coord[hospital_index][0]]
    school_res = [h_coord]
 
   # Binary Search
    max_radius = 100
    min_radius = 0
    iterations = 0
    while True:
        # Limit the number of iterations (In case no school near the border)
        iterations += 1
        if iterations >= 25:
            break
        found = False
        farthest_found = 0
        current_radius = (min_radius + max_radius) / 2.
        all_res =  kd_tree.query_ball_point(health_coord[hospital_index], current_radius)

        for res in all_res:
            dist = geodesic_distance(health_coord[hospital_index], all_points[res][0])
            farthest_found = max(farthest_found, dist)
            if  dist > radius:
                found      = True
                max_radius = current_radius
                break

        if found is True:
            continue

        min_radius = current_radius
        # Stop when we are at 0.1% of the radius
        if abs((farthest_found - radius) / radius) <= 0.01:
            print radius
            print farthest_found
            break

    for res in all_res:
        if all_points[res][1] == 1:
            idx = all_points[res][2]
            coord = [schools_coord[idx][1], schools_coord[idx][0]]
            school_res.append(coord)
    return school_res
