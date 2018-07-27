#!/usr/bin/env python2

from flask import Flask, render_template, request, redirect, Response, jsonify, make_response
import kd_tree_test as kd
import urllib2
import json

app = Flask(__name__, template_folder='.')

@app.route('/')
def output():
    return render_template("index.html")

@app.route('/hf_compute', methods=['GET'])
def worker():
    radius = int(request.args.get("radius"))
    hospital = int(request.args.get("hospital"))
    school_res = kd.hf_compute(radius, hospital)
    data = str(school_res)
    return data

@app.route('/completion')
def completion():
    #contents = kd.getAllCities()
    text = request.args.get("text")
    contents = urllib2.urlopen("http://photon.komoot.de/api/?q="+text+"&osm_tag=place:city")
    contents = json.load(contents)

    res = []
    for feature in contents['features']:
        #print "feat : " + str(feature)
        #print "geo : " + str(feature['geometry'])
        #print "prop : " + str(feature['properties'])
        #print feature['properties']['city'] 
        if feature['properties'].get('name'):
            #print feature['properties']['city']
            coord = [feature['geometry']['coordinates'][1], feature['geometry']['coordinates'][0]];
            res.append([feature['properties']['name'], coord])
    
    return make_response(json.dumps(res))

if __name__ == '__main__':
    app.run()

