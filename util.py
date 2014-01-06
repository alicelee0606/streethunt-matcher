import cv2
import ParsePy
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.vq import kmeans,vq
from numpy import *
import os

def init_parse():
    ParsePy.APPLICATION_ID = "0jrcxKZWUvcY7BXVmCj2hWmSYS2fDcJfWPbGW9p9"
    ParsePy.MASTER_KEY = "jSfjaSpwx85f5MZfAGXGJ2zMuB9fatDK8ObgdGiE"

def imageurl(lat, lng, heading=0, pitch=0):
    return "http://maps.googleapis.com/maps/api/streetview?\
            size=640x640&location=%f,%f&heading=%.1f&pitch=%.1f&sensor=false&\
            key=AIzaSyBS-HaMAHhazScAOwdTOaclJEGBNptWFss" % (lat, lng, heading, pitch)

def get_specific_frame(v, frame):
    # CV_CAP_PROP_POS_FRAMES = 1
    max_frame = v.get(7)
    if (frame > max_frame):
        frame = max_frame
    v.set(1, frame)
    f =  v.read()[1]
    return f    

def get_descriptor(f_path=None, img=None, n_slice=1):
    if f_path is None and img is None:
        print "ERROR: No input specified."
        return
    if img is None:
        img = cv2.imread(f_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT(0, 3, 0.04, 10, 1.6)
    h, w = img.shape
    mask = np.zeros((n_slice, h, w), np.uint8)
    kp = []
    des = []

    for i in range(0, n_slice):
        mask[i, 0:h/2, i * w / n_slice:(i + 1) * w / n_slice] = 255
        kp.append(sift.detect(img, mask[i]))
        d = np.array([])
        #print '[',i,'] ', len(kp[i])
        if len(kp[i]) > 0:
            #print "compute", i
            kp[i], d = sift.compute(img, kp[i])
        
        des.append(d)
        #print des[i]
    
    for i in range(0, n_slice):
        print '     des#',i,':',len(des[i])
    return kp, des

def get_min_dist(ds1, ds2):
    matcher = cv2.DescriptorMatcher_create("BruteForce")
    min_dist = -1
    for i in range(0, len(ds1)):
        for j in range(0, len(ds2)):
            matches = matcher.match(ds1[i], ds2[j])
            d = min([m.distance for m in matches])
            if min_dist < 0 or d < min_dist:
                min_dist = d
    return min_dist

def get_img_file_name(lat, lnt, direction):
    return  "sv_%f_%f_%d.jpg" % (lat, lnt, direction)

def save_image(url, dbname, dirname, filename):
    if not os.path.exists(dbname):
        os.mkdir(dbname)
    dirpath = os.path.join(dbname, dirname)
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)
    filepath = os.path.join(dbname, dirname, filename)
    if not os.path.isfile(filepath):
        urllib.urlretrieve(url, filepath)

if __name__ == '__main__':
    get_descriptor(f_path="database/XinYiRd-East/sv_25.033365_121.537655_3.jpg", n_slice=4)
