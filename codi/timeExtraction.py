from timeit import default_timer as timer
import numpy as np
import MORAS as vc
import cv2

#EXECUCIÓ
imgs1 = ['images/experiments/uni_2.jpg', 'images/experiments/uni4_2.jpg', 'images/experiments/motos3.png', 'images/experiments/cars4.png', 'images/experiments/uni1.jpg', 'images/experiments/jardi_2.jpg']
imgs2 = ['images/experiments/uni.jpg', 'images/experiments/uni4.jpg', 'images/experiments/motos1.png', 'images/experiments/cars6.png', 'images/experiments/uni2.jpg', 'images/experiments/jardi2.jpg']
algs1 = [vc._HARRIS, vc._HARRIS, vc._SIFT, vc._ORB, vc._ORB]
algs2 = [vc._SIFT, vc._ORB, vc._SIFT, vc._ORB, vc._BRISK]
algsName = ["HARRIS + SIFT", "HARRIS + ORB", "SIFT", "ORB", "ORB + BRISK"]


for z in range(len(imgs1)):
	print(imgs1[z], imgs2[z])
	imgROI = cv2.imread(imgs1[z])
	imgROI = cv2.resize(imgROI, (0,0), fx=0.5, fy=0.5)
	imgROIGray = cv2.cvtColor(imgROI, cv2.COLOR_BGR2GRAY)

	imgRobot = cv2.imread(imgs2[z])
	imgRobot = cv2.resize(imgRobot, (0,0), fx=0.5, fy=0.5)
	imgRobotGray = cv2.cvtColor(imgRobot, cv2.COLOR_BGR2GRAY)

	for i in range(len(algs1)):
		psAlg = algs1[i]
		feAlg = algs2[i]
		name = algsName[i] + ":"
		
		times = np.zeros(5)
		numKp = 0
		good = 0
		for j in range(len(times)):
			start = timer()

			kpROI = vc.point_selection(imgROIGray, psAlg)				# Get Keypoints
			kp1, desROI = vc.feature_extraction(imgROIGray, kpROI, feAlg)	# Get features

			kpRobot = vc.point_selection(imgRobotGray, psAlg)					# Get points
			kp2, desRobot = vc.feature_extraction(imgRobotGray, kpRobot, feAlg)	# Get features

			#x, y, img3, good = vc.matching(imgROI, imgRobot, desROI, desRobot, kp1, kp2, feAlg, True)	# Find matching point
			matches = vc.matching2(imgROI, imgRobot, desROI, desRobot, kp1, kp2, feAlg)	# Find matching point
			end = timer()
			times[j] = end - start

		matchesMask = []
		if len(matches) >= 4:
			src_pts = np.float32([ kp1[m.queryIdx].pt for m in matches ]).reshape(-1,1,2)
			dst_pts = np.float32([ kp2[m.trainIdx].pt for m in matches ]).reshape(-1,1,2)
			M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
			matchesMask = mask.ravel().tolist()
		x, y, img3, good = vc.matching(imgROI, imgRobot, desROI, desRobot, kp1, kp2, feAlg, True)	# Find matching point
		cv2.imwrite("resultats/2.1/test"+algsName[i]+" "+str(z)+".png", img3)
		print(name, np.mean(times), "Good matches: "+str(len(matches)))
		print(np.sum(matchesMask))
		#print(name, np.mean(times), "Good matches: "+str(good))
	print("\n")

