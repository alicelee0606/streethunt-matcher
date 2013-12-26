import cv2
import time
import numpy as np
import matplotlib.pyplot as plt

from os import listdir
from os.path import isfile, join
from numpy import *
from scipy.cluster.vq import kmeans,vq
from descriptor import test_feature_detector

def buildVocabulary(path,k,grid_m,grid_n):
    files = [ f for f in listdir(path) if isfile(join(path,f)) ]
    total_desc = []
    dict_vocab = []
    for fidx in range(0,30):
        f = files[fidx]
    #for f in files:
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
            t1 = time.time()
            vocab,dist = kmeans(total_desc[grid_n*i+j],k) # k is the seed number
            t2 = time.time()
            print 'Kmeans in grid[',j,'] takes',t2-t1
            dict_vocab.append(vocab)
    return dict_vocab

def findWord(dict_vocab,path,grid_m,grid_n):
    files = [ f for f in listdir(path) if isfile(join(path,f)) ]
    word_hist = array([])
    for fidx in range(0,30):
        f = files[fidx]
    #for f in files:
        keypoints,file_desc = test_feature_detector(path+f, grid_n)
        line_hist = array([])
        for i in range(0,grid_m):
            for j in range(0,grid_n):
                desc = array(file_desc[j])
                hist = buildWordHist(desc,dict_vocab[grid_n*i+j])
                if len(line_hist) == 0:
                   line_hist = hist
                else:
                   line_hist = np.hstack((line_hist,hist))
        if len(word_hist) == 0:
           word_hist = line_hist
        else:
           word_hist = np.vstack((word_hist,line_hist))
    return word_hist

def buildWordHist(desc,dict_part):
    r = 2
    index,temp = vq(desc,dict_part)
    k = dict_part.shape[0]
    hist,bucket = np.histogram(index,bins = range(k+1))
    norm_hist = hist/double(sum(absolute(hist**r))**(1/r))
    return norm_hist

def main():
    path = './images/'
    d_path = path+'ZhongXiaoEstRd/'
    #t_path = path+'testcase/'
    k = 30
    grid_m = 1
    grid_n = 4
    dict_vocab = buildVocabulary(d_path,k,grid_m,grid_n)
    print dict_vocab
    d_hist = findWord(dict_vocab,d_path,grid_m,grid_n)
    print d_hist
    #t_hist = findWord(dict_vocab,t_path,grid_m,grid_n)

main()
