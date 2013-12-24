import cv2
import numpy as np

from os import listdir
from os.path import isfile, join
from numpy import *
from scipy.cluster.vq import kmeans,vq

def buildVocabulary(path,k,grid_m,grid_n):
    files = [ f for f in listdir(path) if isfile(join(path,f)) ]
    dict_vocab = array([])
    for i in range(0,grid_m):
        for j in range(0,grid_n):
            for f in files:
                total_desc = array([])
                img = cv2.imread(path+f)
                desc = localFeature(img,grid_m,grid_n,i,j)
                if len(desc.shape) == 1:
                   desc = array([desc])
                if len(total_desc) == 0:
                   total_desc = desc
                else:
                   total_desc = np.append(total_desc,desc,axis = 0)
            vocab,dist = kmeans(total_desc,k) # k is the seed number
            if len(dict_vocab) == 0:
               dict_vocab = [vocab]
            else:
               dict_vocab = np.append(dict_vocab,[vocab],axis = 0)

def findWord(dict_vocab,path,grid_m,grid_n):
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
     return word_hist

def buildWordHist(desc,dict_part):
    index,temp = vq(desc,dict_part)
    k = dict_part.shape[0]
    hist,bucket = np.histogram(index,bins = range(k+1))
    return hist

def main():
    path = '/home/alicelee0606/helloflask/'
    d_path = path+'database/'
    t_path = path+'testcase/'
    k = 180
    grid_m = 1
    grid_n = 1
    dict_vocab = buildVocabulary(d_path,k,grid_m,grid_n)
    d_hist = findWord(dict_vocab,d_path,grid_m,grid_n)
    t_hist = findWord(dict_vocab,t_path,grid_m,grid_n)
