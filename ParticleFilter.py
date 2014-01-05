import numpy as np
import math
import cv2
import operator

'''
old_im = cv2.imread('old_image.jpg')
old_im_compensate = cv2.imread('affine_frame.jpg')
#old_gray = cv2.cvtColor(old_im, cv2.COLOR_BGR2GRAY)
new_im = cv2.imread('new_image.jpg')
#new_gray = cv2.cvtColor(new_im, cv2.COLOR_BGR2GRAY)
diff = np.absolute(new_im - old_im)
diff_compensate = np.absolute(new_im - old_im_compensate)
diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
diff_gray_compensate = cv2.cvtColor(diff_compensate, cv2.COLOR_BGR2GRAY)
#diff_gray = old_gray - new_gray
#cv2.namedWindow('diff_image', 0)
#cv2.imshow('diff_image', diff_gray)
#cv2.namedWindow('diff_image_compensate', 0)
#cv2.imshow('diff_image_compensate', diff_gray_compensate)
#cv2.waitKey(0)
'''

#threshold = 250
#length, width = diff_gray.shape

'''
im_thres=np.zeros((length, width))
im_thres_compensate=np.zeros((length, width))
for i, j in zip(*np.where(diff_gray>threshold)):
    im_thres[i,j] = 255
for i, j in zip(*np.where(diff_gray_compensate>threshold)):
    im_thres_compensate[i,j] = 255

cv2.namedWindow('im_thres', 0)
cv2.imshow('im_thres', im_thres)
cv2.namedWindow('im_thres_compensate', 0)
cv2.imshow('im_thres_compensate', im_thres_compensate)
cv2.waitKey(0)
'''

##########Particle Filter#########################

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
        while n<10000:
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

'''
St_prev = []
St = []
for i in range(4):
    diff_im = cv2.imread('diff%d.jpg' % i)
    if len(diff_im.shape)==3:
        diff_im = cv2.cvtColor(diff_im, cv2.COLOR_BGR2GRAY)
    St = ParticleFilter(St_prev, diff_im)
    St_prev = St
    St = []
'''
