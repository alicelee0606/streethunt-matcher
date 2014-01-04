import cv2
import ParsePy
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.vq import kmeans,vq
from numpy import *

def init_parse():
    ParsePy.APPLICATION_ID = "0jrcxKZWUvcY7BXVmCj2hWmSYS2fDcJfWPbGW9p9"
    ParsePy.MASTER_KEY = "jSfjaSpwx85f5MZfAGXGJ2zMuB9fatDK8ObgdGiE"

def imageurl(lat, lng, heading=0, pitch=0):
    return "http://maps.googleapis.com/maps/api/streetview?\
            size=640x640&location=%f,%f&heading=%.1f&pitch=%.1f&sensor=false&\
            key=AIzaSyBS-HaMAHhazScAOwdTOaclJEGBNptWFss" % (lat, lng, heading, pitch)

def get_specific_frame(v, frame):
    # CV_CAP_PROP_POS_FRAMES = 1
    v.set(1, frame)
    f =  v.read()[1]
    return f    

def get_descriptor(img, n_slice=1):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT(0, 3, 0.04, 10, 1.6)
    h, w = img.shape
    mask = np.zeros((n_slice, h, w), np.uint8)
    kp = []
    des = []

    for i in range(0, n_slice):
        mask[i, 0:(h / 2), i * w / n_slice:(i + 1) * w / n_slice] = 255
        kp.append(sift.detect(img, mask[i]))
        kp[i], d = sift.compute(img, kp[i])
        des.append(d)
    
    for i in range(0, n_slice):
        print '    #des:',len(des[i])
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
