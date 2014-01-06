import numpy as np
import cv2
import random
import math
import operator

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

def ParticleFilter(St_prev, diff_im):

    St = []
    n = 0
    k = 0
    m = 6 
    alpha = 0
    length, width = diff_im.shape
    particle_filter = np.zeros((length,width))

    if not St_prev:
        print 'St_prev is empty.'
        threshold = 253
    	for i,j in zip(*np.where(diff_im>threshold)):
            wt = 1/math.sqrt(m)*sum(sum(diff_im[max(i-m/2,0):min(i+m/2,length), max(j-m/2,0):min(j+m/2,width)]))
            alpha=alpha+wt
            St.append((i,j,wt))
            n=n+1
            #if wt>0:
    		    #particle_filter[i,j]=255
    else:
        print 'The size of St_prev is ', len(St_prev)
        St_prev_sorted = sorted(St_prev, key=operator.itemgetter(2))
        while n<40000:
            i,j = (St_prev_sorted[n][0], St_prev_sorted[n][1])
            wt = 1/math.sqrt(m)*sum(sum(diff_im[max(i-m/2,0):min(i+m/2,length), max(j-m/2,0):min(j+m/2,width)]))
            alpha = alpha+wt
            St.append((i,j,wt))
            n=n+1
    for idx in range(n):
        St[idx] = (St[idx][0],St[idx][1],St[idx][2]/alpha)
        if St[idx][2]>0:
            #print St[idx][2]
            particle_filter[St[idx][0],St[idx][1]]=255 

    print '(alpha, n) = ', alpha, n
    cv2.namedWindow('Particle_Filter',0)
    cv2.imshow('Particle_Filter', particle_filter)
    cv2.namedWindow('diff_gray_compensate',0)
    cv2.imshow('diff_gray_compensate', diff_im)
    cv2.waitKey(2000)

    return St


cap = cv2.VideoCapture('streetview-data/pkuRB_pFb2I.mp4')
#cap = cv2.VideoCapture('streetview-data/IMG_2109.mov')
T = 10
Q = 1
# params for ShiTomasi corner detection
feature_params = dict( maxCorners = 1000,
                       qualityLevel = 0.1,
                       minDistance = 7,
                       blockSize = 7 )

# Parameters for lucas kanade optical flow
lk_params = dict( winSize  = (15,15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

# Take first frame and find corners in it
ret, old_frame = cap.read() # should change this to a certain frame index
#old_frame = cv2.flip(old_frame,0)
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
old_gray = (old_gray/Q)*Q
p0 = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)

rows,cols,ch = old_frame.shape
# Create a mask image for drawing purposes
mask = np.zeros_like(old_frame)
St_prev = []
St = []

for i in range(0,T):
    ret,frame = cap.read()
    #frame = cv2.flip(frame,0)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_gray = (frame_gray/Q)*Q
    # calculate optical flow
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

    # Select good points
    good_new = p1[st==1]
    good_old = p0[st==1]
    
    #for gg in good_new:
    #    a,b = gg.ravel()
    #    cv2.circle(frame,(a,b),5,255,-1)
    #cv2.imwrite('our-image/cframe'+str(i)+'.jpg',frame)

    temp_new, temp_old = zip(*zip(good_new,good_old))
    new = np.array(temp_new, dtype = np.float32)
    old = np.array(temp_old, dtype = np.float32)
    M = modify_affine(new, old, 10, 100)
    old_compensate = cv2.warpAffine(old_gray,M,(cols,rows))
    #diff = np.absolute(frame_gray-old_gray)
    diff = np.absolute(frame_gray-old_compensate)
    
    if len(diff.shape)==3:
        diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    St = ParticleFilter(St_prev, diff)
    St_prev = St
    St = []
    
    #cv2.imwrite('our-image/frame'+str(i)+'.jpg',frame_gray)
    #cv2.imwrite('our-image/diff'+str(i)+'.jpg',diff)
    #cv2.imwrite('our-image/diff_compensate'+str(i)+'.jpg',diff_compensate)   
 
    # Now update the previous frame and previous points
    old_gray = frame_gray.copy()
    p0 = good_new.reshape(-1,1,2)

if cv2.waitKey(0) & 0xff == 27:
    cv2.destroyAllWindows()
cap.release()

