# -*- coding: utf-8 -*-
import ParsePy
import numpy as np
import cv2
import sys, os, urllib, csv, json
import geopy
from math import floor
from util import *
from geopy import distance
from operator import itemgetter


"""
Data Model:
db_dict = {
    'file0.jpg':{
        'lat':23.7584929,
        'lnt':121.4858102,
        'descps':[DESCP0_LIST, DESCP1_LIST, DESCP2_LIST, DESCP3_LIST]
    },
    'file1.jpg':{
        ...
    }
    ...
}
"""

data_points = []
testcase_data = None
testcase_video = None
db_dict = None
dbname = "database"
dirname = "XinYiRd-East"
datafilename = "data.csv"
NEAR_DISTANCE_THRESHOLD = 30
API_KEY = "AIzaSyBS-HaMAHhazScAOwdTOaclJEGBNptWFss"

def fetch_data(nodes, street_name, direction):
    #print "Fetching data for " + street_name
    data = []
    #dirname = "%s_%s" % (street_name, direction)
    global dirname, db_files
    for n in nodes:
        print str(nodes.index(n) + 1) + "/" + str(len(nodes)) + "(" + str(n.lat) + ", " + str(n.lng) + ")"
        data.append([n.lat, n.lng])
        for i in range(8):
            url = imageurl(n.lat, n.lng, i * 45)
            save_image(url, "sv_%f_%f_%d.jpg" % (n.lat, n.lng, i), dirname)
    
    f = open(os.path.join(dbname, dirname, datafilename), 'w')
    w = csv.writer(f)
    w.writerows(data)
    f.close()

def save_image(url, filename, dirname):
    if not os.path.exists(dbname):
        os.mkdir(dbname)
    dirpath = os.path.join(dbname, dirname)
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)
    filepath = os.path.join(dbname, dirname, filename)
    if not os.path.isfile(filepath):
        urllib.urlretrieve(url, filepath)

def load_db(street_name=u"信義路", direction=u"東"):
    #dirname = street_name + "_" + direction
    global dirname
    dirpath = os.path.join(dbname, dirname)

    query = ParsePy.ParseQuery("Node")
    query = query.limit(10000).eq("streetName", street_name).eq("direction", direction) 
    nodes = query.fetch()
    print "There're %d nodes on the server." % (len(nodes))
    global files
    if not os.path.exists(dirpath):
        fetch_data(nodes, street_name, direction)
    else:
        files = [f for f in os.listdir(dirpath) if f[-3:] == "jpg"]
        f = open(os.path.join(dbname, dirname, datafilename), 'r')
        if not ((len(files) / 8 == len(nodes)) and (len(nodes) == sum(1 for row in csv.DictReader(f)) + 1)):
            fetch_data(nodes, street_name, direction)
        else:
            print "Your database is up-to-date."
    
    global data_points
    data_points = [geopy.Point(n.lat, n.lng) for n in nodes]

def build_db_descts():
    



def get_near_points(lat, lnt, threshold=NEAR_DISTANCE_THRESHOLD):
    p = geopy.Point(lat, lnt)
    near_points = [dp for dp in data_points if distance.distance(p, dp).m < threshold]
    
    #for np in near_points:
    #    for i in range(8):
    #        print "sv_%f_%f_%d.jpg" % (np.latitude, np.longitude, i)
    print "Found", len(near_points), "points"
    return near_points

def get_clip_data(video_name="IMG_2124.mov", id="HK6Kyn3LMr"):
    #default id is for IMG_2124.mov
    global testcase_data
    testcase_data = ParsePy.ParseQuery("Clip").get(id)
    video_path = os.path.join("testcase", video_name)
    if os.path.isfile(video_path):
        global testcase_video
        testcase_video = cv2.VideoCapture(video_path)
        if not testcase_video.isOpened():
            testcase_video = None
            print "ERROR: video file isn't opened"
    else:
        print "Plase place " + video_name + " under directory testcase/"

def compare_frame(frame, lat, lnt, n_slice=4):
    near_points = get_near_points(lat, lnt, NEAR_DISTANCE_THRESHOLD)
    file_set = []
    global dirname
    for np in near_points:
        for i in range(8):
            file_set.append(os.path.join(dbname, dirname, "sv_%f_%f_%d.jpg" % (np.latitude, np.longitude, i)))
    
    frame_desct = get_descriptor(frame, n_slice)[1]
    db_descts = []
    for f in file_set:
        print f
        db_descts.append(get_descriptor(cv2.imread(f), n_slice)[1])
    
    min_dists = [get_min_dist(d, frame_desct) for d in db_descts]
    indices, sorted_min_dists = zip(*sorted(enumerate(min_dists), key=itemgetter(1)))
    
    print "********************"
    print "Ranking:"
    for i in indices:
        print file_set[i], min_dists[i]


        

def match():
    #for i in range(len(testcase_data.dataPoints)):
    for i in range(1):
        lat = testcase_data.dataPoints[i]['location']['latitude']
        lnt = testcase_data.dataPoints[i]['location']['longitude']
        time = i * 0.2
        frame = n_frame * i * 0.2 / testcase_data.length
        print "[" + str(i * 0.2) + "] (" + str(lat) + ", " + str(lnt) + ") ===> " + str(frame)
        compare_frame(get_specific_frame(testcase_video, frame), lat, lnt)


if __name__ == '__main__':
    init_parse()
    load_db()
    get_clip_data()

    n_frame = floor(testcase_video.get(7))
    print "Total " + str(n_frame) + " frames"
    match()

            
