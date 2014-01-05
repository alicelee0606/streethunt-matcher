# -*- coding: utf-8 -*-
import ParsePy
import numpy as np
import cv2
import sys, os, urllib, csv, json, time, shutil
import geopy
from math import floor
from util import *
from geopy import distance
from operator import itemgetter
import matplotlib.pyplot as plt

"""
Data Model:
db_dict = {
    'file0.jpg':{
        'lat':23.7584929,
        'lnt':121.4858102,:
        'descps':[DESCP0_LIST, DESCP1_LIST, DESCP2_LIST, DESCP3_LIST]
    'file1.jpg':{
        ...
    }
    ...
}
"""

data_points = []
testcase_data = None
testcase_video = None
db_dict = {}
dbname = "database"
dirname = "XinYiRd-East"
data_file_name = "data.json"
NEAR_DISTANCE_THRESHOLD = 25
API_KEY = "AIzaSyBS-HaMAHhazScAOwdTOaclJEGBNptWFss"
N_SLICE = 4

def fetch_data(nodes, street_name, direction):
    #print "Fetching data for " + street_name
    data = []
    #dirname = "%s_%s" % (street_name, direction)
    global dbname, dirname, db_dict
    for n in nodes:
        print str(nodes.index(n) + 1) + "/" + str(len(nodes)) + "(" + str(n.lat) + ", " + str(n.lng) + ")"
        data.append([n.lat, n.lng])
        for i in range(8):
            url = imageurl(n.lat, n.lng, i * 45)
            img_file_name = get_img_file_name(n.lat, n.lng, i)
            if not db_dict.has_key(img_file_name):
                db_dict[img_file_name] = {
                    'lat':n.lat,
                    'lnt':n.lng
                }
            save_image(url, dbname, dirname, "sv_%f_%f_%d.jpg" % (n.lat, n.lng, i))

    f = open(os.path.join(dbname, dirname, data_file_name), 'w')
    json.dump(db_dict, f, indent=2)
    f.close()

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
        data_file_path = os.path.join(dbname, dirname, data_file_name)
        if os.path.isfile(data_file_path):
            f = open(data_file_path, 'r')
            global db_dict
            db_dict = json.load(f)
            if db_dict is None:
                db_dict = {}

            if not ((len(files) / 8 == len(nodes)) and (len(db_dict) / 8 == len(nodes))):
                fetch_data(nodes, street_name, direction)
            else:
                print "Your database is up-to-date."
        else:
            print "data.json file does not exists."
            fetch_data(nodes, street_name, direction)
        
    global data_points
    data_points = [geopy.Point(n.lat, n.lng) for n in nodes]

def compute_db_descts():
    print "Start computing descriptors for images in database."
    
    has_updated = False
    global db_dict, dbname, dirname, data_file_name
    
    print "There are currently", len(db_dict), "image data in db_dict."

    start = time.time()

    n_files = len(db_dict)
    for i in range(n_files):
        f = db_dict.keys()[i]
        if not db_dict[f].has_key('descps'):
            print "[%04d/%04d] Computing descriptors for %s" % (i + 1, n_files, f)
            has_updated = True
            file_path = os.path.join(dbname, dirname, f)
            descps = [d.tolist() for d in get_descriptor(f_path=file_path, n_slice=N_SLICE)[1]]            
            
            db_dict[f]['descps'] = descps

    end = time.time()

    print "Computing finished. Elapsed time: %.5f sec." % ((end - start) / 1000)

    if has_updated:
        f = open(os.path.join(dbname, dirname, data_file_name), 'w')
        json.dump(db_dict, f, indent=4)
        f.close()

def get_nearby_points(lat, lnt, threshold=NEAR_DISTANCE_THRESHOLD):
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
    near_points = get_nearby_points(lat, lnt, NEAR_DISTANCE_THRESHOLD)
    file_set = []
    global dirname
    for np in near_points:
        for i in range(8):
            file_set.append("sv_%f_%f_%d.jpg" % (np.latitude, np.longitude, i))
    
    frame_descp = get_descriptor(img=frame, n_slice=N_SLICE)[1]
    db_descps = []
    for f in file_set:
        descp = None
        print f
        if db_dict[f].has_key('descps'):
            print "Descriptors are already computed!"
            descp = db_dict[f]['descps']
        else:
            file_path = os.path.join(dbname, dirname, f)
            descp = get_descriptor(f_path=file_path, n_slice=N_SLICE)[1]
            db_dict[f]['descps'] = descp
        db_descps.append(descp)
    
    min_dists = [get_min_dist(d, frame_descp) for d in db_descps]
    indices, sorted_min_dists = zip(*sorted(enumerate(min_dists), key=itemgetter(1)))
    
    print "********************"
    print "Ranking:"
    for i in indices:
        print file_set[i], min_dists[i]

    return file_set, indices, min_dists[indices[0]]

def match():
    min_dists = []
    changes = []
    cmp_lat = -1.0
    cmp_lnt = -1.0

    n_frame = testcase_video.get(7)


    output_dir_name = "output"
    if not os.path.exists(output_dir_name):
        os.mkdir(output_dir_name)

    for i in range(len(testcase_data.dataPoints)):
    #for i in range(1):
        #i = len(testcase_data.dataPoints) - 7
        lat = testcase_data.dataPoints[i]['location']['latitude']
        lnt = testcase_data.dataPoints[i]['location']['longitude']
        print "[" + str(i * 0.2) + "] (" + str(lat) + ", " + str(lnt) + ")"
        if lat != cmp_lat and lnt != cmp_lnt:
            #print "!"
            changes.append(i)
            cmp_lat = lat
            cmp_lnt = lnt
    print changes
    
    #for i in changes:
    for i in range(1):
        time = i * 0.2
        frame = n_frame * i * 0.2 / testcase_data.length
        print "[" + str(i * 0.2) + "] (" + str(lat) + ", " + str(lnt) + ") ===> " + str(frame)
        img_frame = get_specific_frame(testcase_video, frame)
        cv2.imwrite('%d.jpg' % (i + 1), img_frame)
        files, indices, min_dist = compare_frame(get_specific_frame(testcase_video, frame), lat, lnt)
        for j in range(len(files)):
            src_path = os.path.join(dbname, dirname, files[indices[j]])
            des_path = os.path.join(output_dir_name, "%d_%d.jpg" % (i + 1, j + 1)) 
            shutil.copy2(src_path, des_path)
        print "[%.1f] %.5f" % (time, min_dist)
        min_dists.append(min_dist)

    for i in range(len(changes)):
        print "[%.1f] %.5f" % (changes[i] * 0.2, min_dists[i])

    print "Saving db_dict before exit."

    plt.plot(min_dists)
    plt.show()


def main():
    init_parse()
    load_db()
    #compute_db_descts()
    get_clip_data()

    n_frame = floor(testcase_video.get(7))
    print "Total " + str(n_frame) + " frames"
    match()

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
       raise
    except e:
        print e
        #print "Saving db_dict before exit."
        #f = open(os.path.join(dbname, dirname, data_file_name), 'w')
        #json.dump(db_dict, f, indent=2)
        #f.close()
    
