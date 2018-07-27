#!/usr/bin/env python2

import json
import numpy as np
import matplotlib.pyplot as plt
import itertools
import math
import pickle

from scipy.spatial import Voronoi, voronoi_plot_2d, Delaunay
from os import mkdir as mkdir_os
from collections import defaultdict


schools_path           = "dataset/schools.geojson"              # Path to schools geojson
health_facilities_path = "dataset/health-facilities.geojson"    # Path to health facilities geojson

schools_coord = [] # schools coord 
health_coord  = [] # health coord

health_adjacent = defaultdict(set)

def plot_voronoi(vor):
    voronoi_plot_2d(vor)

def call_voronoi(points):
    print "Computing VORONOI..."
    vor = Voronoi(points)
    print "VORONOI has been computed on <" + str(len(points)) + "> points"
    return vor

def call_delaunay(points):
    print "Computing DELAUNAY..."
    delau = Delaunay(points)
    print "DELAUNAY has been computed on <" + str(len(points)) + "> points"
    return delau

def read_health():
    with open(health_facilities_path) as f:
        data = json.load(f)

    for feature in data["features"]:
        health_coord.append(feature['geometry']['coordinates'])

def read_schools():
    with open(schools_path) as f:
        data = json.load(f)

    for feature in data["features"]:
        schools_coord.append(feature['geometry']['coordinates'])

# TODO: Optimize
# Search for school region
def find_region_with_school(point, vor, list_school_by_region, idx):

    point_index = np.argmin(np.sum((np.subtract(health_coord, point))**2, axis=1))
    ridges = np.where(vor.ridge_points == point_index)[0]
    
    vertex_set = set(np.array(vor.ridge_vertices)[ridges, :].ravel())
    region = [x for x in vor.regions if set(x) == vertex_set][0]
  
    for i,reg in enumerate(vor.regions):
        if reg == region and i != 0: 
            list_school_by_region[i].append(idx)

# [region -> adjacent regions] mapping
def find_adjacent(delau):
    
    list_adjacent = defaultdict(set)
    for p in delau.vertices:
        for i,j in itertools.combinations(p, 2):
            list_adjacent[i].add(j)
            list_adjacent[j].add(i)

    return list_adjacent

def find_schools_for_health(h, health_adjacent, list_school_by_region, radius):

    health_coord_h = health_coord[h]
    list_adjacent = health_adjacent[h]
    
    list_schools_by_radius = []

    for adjacent in list_adjacent:
        list_school_adjacent = list_school_by_region[adjacent]
        for school_adjacent in list_school_adjacent:
            school_adjacent_coord = schools[school_adjacent]
            x = school_adjacent_coord[0] - health_coord_h[0]
            y = school_adjacent_coord[1] - health_coord_h[1]
            dist = math.sqrt( math.pow(x,2) + math.pow(y,2)) 
            if dist < radius:
                list_schools_by_radius.append(school_adjacent)

    return list_schools_by_radius

def write_to_file(filename, data):
    pickle.dump(data, open(filename, "wb"))

def main():
    
    try:
        mkdir_os("tmp")
    except OSError:
        pass 

    radius = 5
    input_health = 40

    # Reading JSON files
    read_health()
    read_schools()

    # Init 2D array with (nb health facilities) rows
    list_school_by_region = {f:[] for f in xrange(len(health_coord))}

    # Computing voronoi and delaunay
    vor = call_voronoi(health_coord) 
    delau = call_delaunay(health_coord)

    # Plotting Voronoi
    # TODO: Make it optional
    #plot_voronoi(vor)
    
    # Find adjacent regions for each region
    health_adjacent = find_adjacent(delau)

    # Find region for each school
    print "Finding all schools for each health facilities... (<" + str(len(schools_coord)) + "> schools found)"
    i = 0
    for sc in schools_coord:
        find_region_with_school(sc, vor, list_school_by_region, i)
        i = i + 1
    
    print "All schools has been tested."

    #TODO: Disabled for now
    #print "Finding all schools in less than <" +str(radius) +"> km from the health facilities <" + str(input_health) + ">."
    #health_schools_by_radius = find_schools_for_health(input_health, health_adjacent, list_school_by_region, radius)
    #print health_schools_by_radius
    #print "\n"

    print "\n\n"

    print "Plotting result"
    
    write_to_file("tmp/health_facilities_adjacent.txt", health_adjacent)
    write_to_file("tmp/health_facilities_list_schools.txt", list_school_by_region)

    #plt.show()

main()
