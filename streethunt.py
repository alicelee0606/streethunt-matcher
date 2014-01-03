# -*- coding: utf-8 -*-

import ParsePy
import numpy as np
import cv2
import sys, os
import urllib
import csv

db = None
dbname = "database"
datafilename = "data.csv"
API_KEY = "AIzaSyBS-HaMAHhazScAOwdTOaclJEGBNptWFss"

def fetch_data(street_name=u"信義路", direction=u"東"):
    print "Fetching data for " + street_name
    query = ParsePy.ParseQuery("Node")
    query = query.limit(10000).eq("streetName", street_name).eq("direction", direction) 
    nodes = query.fetch()
    db = []
    dirname = "%s_%s" % (street_name, direction)
    for n in nodes:
        print str(nodes.index(n) + 1) + "/" + str(len(nodes)) + "(" + str(n.lat) + ", " + str(n.lng) + ")"
        db.append([n.lat, n.lng])
        for i in range(8):
            url = imageurl(n.lat, n.lng, i * 45)
            save_image(url, "sv_%f_%f_%d.jpg" % (n.lat, n.lng, i), dirname)
    
    f = open(os.path.join(dbname, dirname, datafilename), 'w')
    w = csv.writer(f)
    w.writerows(db)
    f.close()

def imageurl(lat, lng, heading=0, pitch=0):
    return "http://maps.googleapis.com/maps/api/streetview?size=640x640&location=%f,%f&heading=%.1f&pitch=%.1f&sensor=false&key=AIzaSyBS-HaMAHhazScAOwdTOaclJEGBNptWFss" % (lat, lng, heading, pitch)

def save_image(url, filename, dirname):
    if not os.path.exists(dbname):
        os.mkdir(dbname)
    dirpath = os.path.join(dbname, dirname)
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)
    filepath = os.path.join(dbname, dirname, filename)
    if not os.path.isfile(filepath):
        urllib.urlretrieve(url, filepath)

def init_parse():
    ParsePy.APPLICATION_ID = "0jrcxKZWUvcY7BXVmCj2hWmSYS2fDcJfWPbGW9p9"
    ParsePy.MASTER_KEY = "jSfjaSpwx85f5MZfAGXGJ2zMuB9fatDK8ObgdGiE"

def load_db(street_name=u"信義路", direction=u"東"):
    dirname = street_name + "_" + direction
    dirpath = os.path.join(dbname, dirname)

    query = ParsePy.ParseQuery("Node")
    query = query.limit(10000).eq("streetName", street_name).eq("direction", direction) 
    nodes = query.fetch()
    print "There're %d nodes on the server." % (len(nodes))

    if not os.path.exists(dirpath):
        fetch_data(street_name, direction)
    else:
        files = [f for f in os.listdir(dirpath) if f[-3:] == "jpg"]
        f = open(os.path.join(dbname, dirname, datafilename), 'r')
        if not ((len(files) / 8 == len(nodes)) and (len(nodes) == sum(1 for row in csv.DictReader(f)) + 1)):
            fetch_data(street_name, direction)
        else:
            print "Your database is up-to-date."


def get_nearest_pictures(lat, lnt):
    print "Nothing here yet ha"

def camera_capture():
    cap = cv2.VideoCapture(0)
    while(True):
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.flip(gray, 1)
        cv2.imshow('frame', gray)
        if cv2.waitKey(1) & 0xEF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    init_parse()
    load_db()
