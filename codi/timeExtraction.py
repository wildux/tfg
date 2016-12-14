from timeit import default_timer as timer
import numpy as np
import MORAS as vc
import cv2

#IMATGES
imgROI = cv2.imread('1.ppm')		# Global image
#imgROI = cv2.resize(imgROI, (0,0), fx=0.3, fy=0.3)
imgROIGray = cv2.cvtColor(imgROI, cv2.COLOR_BGR2GRAY)

imgRobot = cv2.imread('all.ppm')	# Image captured by the robot
#imgRobot = cv2.resize(imgRobot, (0,0), fx=0.3, fy=0.3)
imgRobotGray = cv2.cvtColor(imgRobot, cv2.COLOR_BGR2GRAY)

#EXECUCIÓ
algs1 = [vc._ORB, vc._BRISK, vc._SIFT]
algs2 = [vc._ORB, vc._BRISK, vc._SIFT]
algsName = ["ORB", "BRISK","SIFT"]

for i in range(len(algs1)):
	psAlg = algs1[i]
	feAlg = algs2[i]
	name = algsName[i] + ":"
	#times = np.zeros(10)
	#numKp = 0
	#for j in range(len(times)):
	
	start = timer()

	kpROI = vc.point_selection(imgROIGray, psAlg, True)				# Get Keypoints
	kp1, desROI = vc.feature_extraction(imgROIGray, kpROI, feAlg)	# Get features

	kpRobot = vc.point_selection(imgRobotGray, psAlg, True)					# Get points
	kp2, desRobot = vc.feature_extraction(imgRobotGray, kpRobot, feAlg)	# Get features

	x, y, img3, good = vc.matching(imgROI, imgRobot, desROI, desRobot, kp1, kp2, feAlg, True)	# Find matching point
	end = timer()
	#times[j] = end - start
	#numKp = len(kpROI)
	cv2.imwrite("test"+algsName[i]+".png", img3)
	#print(name, np.mean(times), "ms", "Keypoints:", numKp)
	print(name, end-start, "Good matches: "+str(good))

