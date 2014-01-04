import numpy as np
import cv2
import random

def modify_affine(new, old, thr, recur):
    inlier = range(0,len(old))
    last_inlier = []
    count = 0
    M = None
    while  (len(inlier)!=len(last_inlier)) and (count < recur):
        if len(inlier) < 0.3*len(old):
           last_inlier = range(0,len(old))
        else:
           last_inlier = inlier
        inlier = []
        seeds = range(0,len(last_inlier))
        random.shuffle(seeds)
        seed = seeds[0:4]
        pst_new = np.array([new[last_inlier[j]] for j in seed])
        pst_old = np.array([old[last_inlier[j]] for j in seed])
        M = cv2.getPerspectiveTransform(pst_new,pst_old)
        count = count + 1
        for k in range(0,len(last_inlier)):
            fone = np.hstack((old[last_inlier[k]],1))
            Tfone = np.transpose(fone)
            fcomp = np.dot(M,Tfone)
            dist = np.linalg.norm(old[last_inlier[k]]-fcomp[0:2])
            if dist < thr:
               inlier.append(last_inlier[k])
        print len(inlier)
	if len(inlier) < 0.5 * len(old):
            print "bang"
    return M

cap = cv2.VideoCapture('streetview-data/pkuRB_pFb2I.mp4')
T = 1

# params for ShiTomasi corner detection
feature_params = dict( maxCorners = 1000,
                       qualityLevel = 0.01,
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
p0 = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)

rows,cols,ch = old_frame.shape
# Create a mask image for drawing purposes
mask = np.zeros_like(old_frame)

for i in range(0,T):
    ret,frame = cap.read()
    #frame = cv2.flip(frame,0)
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
    dst = cv2.warpPerspective(old_gray,M,(cols,rows))
    cv2.imwrite('old_frame.jpg',old_gray)
    cv2.imwrite('frame.jpg',frame_gray)
    cv2.imwrite('persp_frame.jpg',dst)
    #k = cv2.waitKey(30) & 0xff
    #if k == 27:
    #    break

    # Now update the previous frame and previous points
    old_gray = frame_gray.copy()
    p0 = good_new.reshape(-1,1,2)

if cv2.waitKey(0) & 0xff == 27:
    cv2.destroyAllWindows()
cap.release()

