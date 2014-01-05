#!/usr/local/bin/python
#!/usr/bin/python
import cv2
import time
import numpy as np
import matplotlib.pyplot as plt
import sys, os

class Matcher:
    def __init__(self, path):
        self.__path = path
        #self.__load_video()

    def __load_video(self):
        print "Loading video file from:", self.__path
        video = cv2.VideoCapture(self.__path)
        if video.isOpened():
            success = True
            n_frame = 0
            while success:
                success, frame = video.read()
                if success:
                    n_frame = n_frame + 1
                    cv2.imwrite("%s_%05d.jpg" % (self.__path[:-4], n_frame), frame)
            print "Slice this video into %d images." % (n_frame)
        else:
            print "Cannot open this file."

