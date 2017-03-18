import numpy as np
import MORAS as vc
import cv2

algs = [vc._SIFT, vc._SURF, vc._ORB, vc._HARRIS, vc._MSER]
algsName = ["SIFT", "SURF","ORB", "HARRIS", "MSER"]
paths = ['images/graff/img1.png', 'images/boat/img1.png', 'images/ubc/img1.png', 'images/experiments/uni.jpg', 'images/experiments/jardi2.jpg', 'images/experiments/uni4.jpg']

for imgPath in paths:
	image = cv2.imread(imgPath)
	img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
	for i in range(len(algs)):
		psAlg = algs[i]
		kp = vc.point_selection(img, psAlg, True)
		cv2.drawKeypoints(img,kp,image,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
		cv2.imwrite("KP_"+algsName[i]+"_"+imgPath, img3)
