from timeit import default_timer as timer
import numpy as np
import MORAS as vc
import cv2

#IMATGES
imgROI = cv2.imread('object3.jpg')		# Global image
imgROI = cv2.resize(imgROI, (0,0), fx=0.3, fy=0.3)
imgROIGray = cv2.cvtColor(imgROI, cv2.COLOR_BGR2GRAY)

#EXECUCIÓ
algs = [vc._ORB, vc._BRISK, vc._SIFT, vc._SURF, vc._MSER]
algsName = ["ORB","BRISK","SIFT", "SURF", "MSER"]
for i in range(len(algs)):
	psAlg = algs[i]
	name = algsName[i] + ":"
	times = np.zeros(10)
	numKp = 0
	for j in range(len(times)):
		start = timer()
		kpROI = vc.point_selection(imgROIGray, psAlg, True)
		end = timer()
		times[j] = end - start
		numKp = len(kpROI)
	print(name, np.mean(times), "ms", "Keypoints:", numKp)

