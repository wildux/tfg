from timeit import default_timer as timer
import numpy as np
import MORAS as vc
import cv2

algs = [vc._SIFT, vc._SURF, vc._ORB, vc._HARRIS, vc._MSER]
algsName = ["SIFT", "SURF","ORB", "HARRIS", "MSER"]
paths = ['images/graff/img1.png', 'images/boat/img1.png', 'images/ubc/img1.png', 'images/experiments/uni.jpg', 'images/experiments/jardi2.jpg', 'images/experiments/uni4.jpg']

for imgPath in paths:
	img = cv2.imread(imgPath, 0)
	img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
	print(imgPath)
	for i in range(len(algs)):
		psAlg = algs[i]
		name = algsName[i] + ":"
		times = np.zeros(10)
		numKp = 0
		for j in range(len(times)):
			start = timer()
			kpROI = vc.point_selection(img, psAlg)
			end = timer()
			times[j] = end - start
			numKp = len(kpROI)
		print(name, np.mean(times), "ms", "Keypoints:", numKp)
	print("\n")

