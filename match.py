#!/usr/local/bin/python
#!/usr/bin/python

import cv2
import time
import numpy as np
import matplotlib.pyplot as plt

import sys
from os import listdir
from os.path import isfile, join
from numpy import *
from scipy.cluster.vq import kmeans,vq
from descriptor import test_feature_detector
from operator import itemgetter

def main():
    db_path = sys.argv[1] 
    t_file = sys.argv[2]

    n_slice = 4
    db_files = [db_path + f for f in listdir(db_path) if isfile(db_path + f)]
    
    db_descriptors = [get_descriptor(f, n_slice)[1] for f in db_files]
    kp_t, d_t = get_descriptor(t_file, n_slice)

    min_dists = [get_min_dist(d_d, d_t) for d_d in db_descriptors]
    indices, sorted_min_dists = zip(*sorted(enumerate(min_dists), key=itemgetter(1)))

    print "********************"
    print "Ranking:"
    for i in indices:
        print db_files[i], min_dists[i]

def get_descriptor(imfname, n_slice=1):
    print 'Compute descriptor for', imfname
    img = cv2.imread(imfname)
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
        print '    #des:',len(des[i]),'for',imfname,'[',i,']'
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

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "ERROR! Usage: python match.py DATABASE_DIR TARGET_FILE"
    else:
        main()
