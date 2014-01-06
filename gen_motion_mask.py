import numpy as np
import cv2
import random
import math
import ParsePy
from streethunt import *
from util import *
from operator import itemgetter

def modify_affine(new, old, thr, recur):
    inlier = range(0,len(old))
    last_inlier = []
    dist_container = []
    count = 0
    M = None
    while  (len(inlier)!=len(last_inlier)):# and (count < recur):
        if len(inlier) < 0.8*len(old):
           #print len(inlier)
           thr = np.mean(dist_container) - np.std(dist_container)
           last_inlier = range(0,len(old))
           #print thr
        else:
           last_inlier = inlier
        inlier = []
        dist_container = []
        seeds = range(0,len(last_inlier))
        random.shuffle(seeds)
        seed = seeds[0:3]
        pst_new = np.array([new[last_inlier[j]] for j in seed])
        pst_old = np.array([old[last_inlier[j]] for j in seed])
        M = cv2.getAffineTransform(pst_new,pst_old)
        count = count + 1
        for k in range(0,len(last_inlier)):
            fone = np.hstack((old[last_inlier[k]],1))
            Tfone = np.transpose(fone)
            fcomp = np.dot(M,Tfone)
            dist = np.linalg.norm(old[last_inlier[k]]-fcomp[0:2])
            dist_container.append(dist)
            if dist < thr:
               inlier.append(last_inlier[k])
    return M

def generate_mask(cap, v_timelength):
    #mask_dict = {}
    n_frame = int(math.ceil(v_timelength/0.2))
    total_frame = cap.get(7) 
    # params for ShiTomasi corner detection
    feature_params = dict( maxCorners = 1000,
                           qualityLevel = 0.01,
                           minDistance = 7,
                           blockSize = 7 )
    # Parameters for lucas kanade optical flow
    lk_params = dict( winSize  = (15,15),
                      maxLevel = 2,
                      criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
    print n_frame 
    for i in range(1,n_frame):
        print i
        # Take first frame and find corners in it
        old_frame = get_specific_frame(cap,int(math.ceil(total_frame*(0.2*i)/v_timelength))-1)
        old_frame = cv2.flip(old_frame,-1)
        old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
        p0 = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)

        hsv = np.zeros_like(old_frame)
        hsv[...,1] = 255
        rows,cols,ch = old_frame.shape
        
        frame = get_specific_frame(cap,int(math.ceil(total_frame*(0.2*i)/v_timelength)))
        frame = cv2.flip(frame,-1)
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # calculate optical flow
        p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

        # Select good points
        good_new = p1[st==1]
        good_old = p0[st==1]
	    
        temp_new, temp_old = zip(*zip(good_new,good_old))
        new = np.array(temp_new, dtype = np.float32)
        old = np.array(temp_old, dtype = np.float32)
        M = modify_affine(new, old, 10, 100)
        dst = cv2.warpAffine(old_gray,M,(cols,rows))
        prvs = dst
        nextf = frame_gray
        flow = cv2.calcOpticalFlowFarneback(prvs,nextf, 0.5, 1, 30, 15, 50, 5, 1)

        mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
        hsv[...,0] = ang*180/np.pi/2
        hsv[...,2] = cv2.normalize(mag,None,0,255,cv2.NORM_MINMAX)
        rgb = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
        rgb_gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
        m,n = rgb_gray.shape
        mask = np.zeros_like(rgb[...,0])
        for a in range(0,m):
            for b in range(0,n):
                if rgb_gray[a][b] < 10:
                    mask[a][b] = 255

        cv2.imwrite('mask-2111/frame-'+str(0.2*i)+'.jpg',frame)
        cv2.imwrite('mask-2111/mask-'+str(0.2*i)+'.jpg',mask)
        cv2.imwrite('mask-2111/rgb-'+str(0.2*i)+'.jpg',rgb)
        #mask_dict[str(i*0.2)] = mask
        """# Now update the previous frame and previous points
        old_gray = frame_gray.copy()
        p0 = good_new.reshape(-1,1,2)
        prvs = nextf"""

    cap.release()

init_parse()
load_db()
cap = cv2.VideoCapture('streetview-data/IMG_2111.mov')
testcase_data = ParsePy.ParseQuery("Clip").get('Pb9erVwDty')
generate_mask(cap,testcase_data.length)
