import matplotlib.pyplot as plt
import numpy as np
import cv2
import cv
import time


def test_feature_detector(detector, imfname, num_slice):
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
        mask[i, 0:h, i*w/num_slice:(i+1)*w/num_slice] = 255
        kp.append(sift.detect(im, mask[i]))
        kp[i], descript = sift.compute(im, kp[i])
        des.append(descript)
#    kp_surf = surf.detect(im, None)
        img = cv2.drawKeypoints(im, kp[i], flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        cv2.imwrite('sift_keypoints%d.jpg' % (i), img)

    t2 = time.time()
    print detector, 'number of KeyPoint objects', len(kp), '(time', t2-t1, ')'

    return kp, des


def main():
    imfname = r'jean.jpg'

    form = ""
    detector = "FAST"

    num_slice = 4
    kpts,des = test_feature_detector(form + detector, imfname, num_slice)

if __name__ == '__main__':
    main()
