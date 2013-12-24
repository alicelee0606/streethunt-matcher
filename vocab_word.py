import cv2
import time
import numpy as np
import matplotlib.pyplot as plt

from os import listdir
from os.path import isfile, join
from numpy import *
from scipy.cluster.vq import kmeans,vq

def test_feature_detector(imfname, num_slice):
    descript = 'SIFT'
    image = cv2.imread(imfname)

    t1 = time.time()
    im = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#    forb = cv2.FeatureDetector_create(detector)
#    kpts = forb.detect(im)

    sift = cv2.SIFT(0, 3, 0.04, 10, 1.6)
#    surf = cv2.SURF()
    h,w = im.shape
#    print 'h,w = ', h,w
    mask = np.zeros((num_slice,h,w), np.uint8)
    kp = []
    des = []
    for i in range(num_slice):
        mask[i, 0:h/2, i*w/num_slice:(i+1)*w/num_slice] = 255
        kp.append(sift.detect(im, mask[i]))
        kp[i], descript = sift.compute(im, kp[i])
        des.append(descript)
#    kp_surf = surf.detect(im, None)
        img = cv2.drawKeypoints(im, kp[i], flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        cv2.imwrite('sift_keypoints%d.jpg' % (i), img)

    t2 = time.time()
#    print 'number of KeyPoint objects', len(kp), '(time', t2-t1, ')'
#    print 'length of descriptor', len(des)
#    for i in range(num_slice):
#        print 'descriptor[%d]' % (i), des[i].shape

    return kp, des

def buildVocabulary(path,k,grid_m,grid_n):
    files = [ f for f in listdir(path) if isfile(join(path,f)) ]
    total_desc = []
    dict_vocab = array([])
    for f in files:
        print f
        #img = cv2.imread(path+f)
        keypoints,file_desc = test_feature_detector(path+f, grid_n)
        for i in range(0,grid_m):
            for j in range(0,grid_n):
                desc = array(file_desc[j])
                if len(total_desc) < grid_n*i+j+1:
                   total_desc.append(desc)
                else:
                   temp = total_desc[grid_n*i+j]
                   total_desc[grid_n*i+j] = np.vstack((temp,desc))
    for i in range(0,grid_m):
        for j in range(0,grid_n):
            print j
            vocab,dist = kmeans(total_desc[grid_n*i+j],k) # k is the seed number
            print 'kmeans done'
            if len(dict_vocab) == 0:
               dict_vocab = [vocab]
            else:
               dict_vocab = np.append(dict_vocab,[vocab],axis = 0)
    return dict_vocab

"""def findWord(dict_vocab,path,grid_m,grid_n):
    files = [ f for f in listdir(path) if isfile(join(path,f)) ]
    word_hist = array([])
    for f in files:
        img = cv2.imread(path+f)
        line_hist = array([])
        for i in range(0,grid_m):
            for j in range(0,grid_n):
                desc = localFeature(img,grid_m,grid_n,i,j)
                hist = buildWordHist(desc,dict_vocab[grid_n*i+j])
                if len(line_hist) == 0:
                   line_hist = hist
                else
                   line_hist = np.hstack((line_hist,hist))
        if len(word_hist) == 0:
           word_hist = line_hist
        else:
           word_hist = np.vstack((word_hist,line_hist))
     return word_hist"""

def buildWordHist(desc,dict_part):
    index,temp = vq(desc,dict_part)
    k = dict_part.shape[0]
    hist,bucket = np.histogram(index,bins = range(k+1))
    return hist

def main():
    path = './images/'
    d_path = path+'database/'
    #t_path = path+'testcase/'
    k = 10
    grid_m = 1
    grid_n = 4
    dict_vocab = buildVocabulary(d_path,k,grid_m,grid_n)
    print dict_vocab
    #d_hist = findWord(dict_vocab,d_path,grid_m,grid_n)
    #t_hist = findWord(dict_vocab,t_path,grid_m,grid_n)

main()
