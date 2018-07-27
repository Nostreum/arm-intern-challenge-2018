#! /usr/bin/env python2

import pickle
import json
import pyqtree

import matplotlib
matplotlib.rcParams['backend.qt4'] = 'PyQt4'
matplotlib.use('Qt4Agg')

import matplotlib.pyplot as plt
import matplotlib.patches

hf_filename = "dataset/health-facilities.geojson"
hf_qtree_filename = "tmp/health-facilities.qtree"

# Precomputed bbox of health facilities
bbox = (-81.7090031701673, -0.6218765, 0.0, 12.5747941)

# Iterate through health-facilities
# and feed them to the quadtree
qtree = pyqtree.Index(bbox)
with open(hf_filename) as f:
    hfs_geojson = json.load(f)
    hfs = enumerate(hf["geometry"]["coordinates"] for hf in hfs_geojson["features"])
    for i, hf in hfs:
        hf_bbox = (hf[0], hf[1], hf[0], hf[1])
        qtree.insert(i, hf_bbox)

# Dump quad-tree
with open(hf_qtree_filename, "wb") as f:
    pickle.dump(qtree, f)

print "Health facilities quadtree generated in {}".format(hf_qtree_filename)
