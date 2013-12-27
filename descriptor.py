#!/usr/local/bin/python
#!/usr/bin/python

import os, sys
import matplotlib.pyplot as plt
import numpy as np
import cv2
import time


def test_feature_detector(imfname, num_slice=1, save_output=False):
    descript = 'SIFT'
    image = cv2.imread(imfname)

    t1 = time.time()
    im = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#    forb = cv2.FeatureDetector_create(detector)
#    kpts = forb.detect(im)

    sift = cv2.SIFT(0, 3, 0.04, 10, 1.6)
#    surf = cv2.SURF()
    h,w = im.shape
    print 'h,w = ', h,w
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
        omfname = "%s_sift_keypoints%d.jpg" % (os.path.splitext(imfname)[0], i)
        if save_output:
            cv2.imwrite(omfname, img)

    t2 = time.time()
    print 'number of KeyPoint objects', len(kp), '(time', t2-t1, ')'
    print 'length of descriptor', len(des)
    for i in range(num_slice):
        print 'descriptor[%d]' % (i), des[i].shape

    return kp, des


def main():
    imfname = sys.argv[1]

    form = ""
    detector = "FAST"

    num_slice = 4
    if (len(sys.argv) >= 3):
       num_slice = int(sys.argv[2])
    save_output = True
    if (len(sys.argv) >= 4):
        save_output = (sys.argv[3] == '1')
    kpts,des = test_feature_detector(imfname, num_slice, save_output)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "ERROR: No input file. Usage: python descriptor.py INPUT_FILE_NAME [NUM_SLICE]"
    else:
        main()
