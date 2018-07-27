import pickle
import time
import json
import math
import matplotlib.pyplot as plt
import numpy as np
from random import randint

# Great circle distance - https://en.wikipedia.org/wiki/Great-circle_distance
def distance(point1, point2):
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


def get_all_candidates(hospital_index, radius, health, schools, list_schools, adjacent):
    # Current implementation : It is sufficient to have one element in cell to get neighbour cells
    visited = []
    queue   = [hospital_index]
    candidates = []
        
    while queue:
        current_index = queue.pop(0)
        if current_index in visited:
            continue
        visited.append(current_index)
    
        # Add all elements of this cell to the candidates
        for school in list_schools[current_index]:
            candidates.append(school)
        
        # If this cell still have a school < radius ==> Add its neighbors ot the queue
        for school in list_schools[current_index]:
            if distance(schools[school], health[current_index]) <= radius:
                for hospital in adjacent[current_index]:
                    queue.append(hospital)
                # break the current loop (schools traversal)
                break

    return candidates

    
start = time.time()

health  = []
schools = []

schools_path           = "dataset/schools.geojson"
health_facilities_path = "dataset/health-facilities.geojson"

with open(schools_path) as f:
    data = json.load(f)

for feature in data["features"]:
    schools.append(feature['geometry']['coordinates'])

with open(health_facilities_path) as f:
    data = json.load(f)

for feature in data["features"]:
    health.append(feature['geometry']['coordinates'])

with open("tmp/health_facilities_list_schools.txt", "rb") as f:
    list_schools = pickle.load(f)

with open("tmp/health_facilities_adjacent.txt", "rb") as f:
    adjacent = pickle.load(f)

end = time.time()

print "Read data in " + str(end-start) + " s"

# for i in range(1, 10):
#     index1 = randint(0, len(health))
#     index2 = randint(0, len(schools))
#     print "Distance between " + str(health[index1]) + " and " + str(schools[index2]) + " = " + str(distance(health[index1], schools[index2]))


all_radius   = []
all_mins     = []
all_averages = []
all_maxs     = []

for radius in np.linspace(0, 10, 100):
    print "Processing radius = " + str(radius)
    average = 0
    current_min =  100000000000
    current_max = -10000000000
    
    for index in range(0, len(health)):
        candidates = get_all_candidates(index, radius, health, schools, list_schools, adjacent) 
        average += len(candidates)
        current_min = min(current_min, len(candidates))
        current_max = max(current_max, len(candidates))
 
    all_radius.append(radius)
    all_mins.append(current_min)
    all_maxs.append(current_max)
    all_averages.append(100*(average/float(len(health))/float(len(schools))))

plt.subplot(3,1,1)
plt.plot(all_radius, all_averages)
plt.subplot(3,1,2)
plt.plot(all_radius, all_mins)
plt.subplot(3,1,3)
plt.plot(all_radius, all_maxs)
plt.show()
