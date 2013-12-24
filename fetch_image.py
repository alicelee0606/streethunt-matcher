#!/usr/local/bin/python
#!/usr/bin/python

import os, sys
import urllib
import ParsePy

API_KEY = "AIzaSyBS-HaMAHhazScAOwdTOaclJEGBNptWFss"
# example:
# http://maps.googleapis.com/maps/api/streetview?size=640x640&location=25.033467,121.538572&heading=80&pitch=15&sensor=false&key=AIzaSyBS-HaMAHhazScAOwdTOaclJEGBNptWFss

def fetch_data(street_name, direction):
    print "Fetching data for " + street_name
    query = ParsePy.ParseQuery("Node")
    query = query.eq("streetName", street_name).eq("direction", direction) 
    nodes = query.fetch()
    for n in nodes:
        print "(" + str(n.lat) + ", " + str(n.lng) + ")"
        for i in range(8):
            url = imageurl(n.lat, n.lng, i * 45)
            save_image(url, "sv_%f_%f_%d.jpg" % (n.lat, n.lng, i))
    print "Output images are in images/%s/" % (sys.argv[3])

def imageurl(lat, lng, heading=0, pitch=0):
    return "http://maps.googleapis.com/maps/api/streetview?size=640x640&location=%f,%f&heading=%.1f&pitch=%.1f&sensor=false&key=AIzaSyBS-HaMAHhazScAOwdTOaclJEGBNptWFss" % (lat, lng, heading, pitch)

def save_image(url, filename):
    if not os.path.exists('./images'):
        os.mkdir('images')
    if not os.path.exists('./images/%s' % (sys.argv[3])):
        os.mkdir('./images/%s' % (sys.argv[3]))
    filename = "images/" + sys.argv[3] + "/" + filename
    urllib.urlretrieve(url, filename)

def init_parse():
    ParsePy.APPLICATION_ID = "0jrcxKZWUvcY7BXVmCj2hWmSYS2fDcJfWPbGW9p9"
    ParsePy.MASTER_KEY = "jSfjaSpwx85f5MZfAGXGJ2zMuB9fatDK8ObgdGiE"

if __name__ == "__main__":
    init_parse()
    if len(sys.argv) < 4:
        print "ERROR: No. Usage:(fetch_image.py STREET_NAME DIRECTION OUTPUT_DIR_NAME)"
    else:
        fetch_data(sys.argv[1], sys.argv[2])
