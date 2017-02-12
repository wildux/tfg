from timeit import default_timer as timer
import numpy as np
import MORAS as vc
import cv2
import scipy as sp

#EXECUCIÓ
imgs1 = ['images/light/img1.png','images/boat/img5.png','images/graff/img1.png']
imgs2 = ['images/light/img6.png','images/boat/img6.png','images/graff/img3.png']
algs1 = [vc._HARRIS, vc._SIFT, vc._ORB]
algs2 = [vc._SIFT, vc._SIFT, vc._ORB]
algsName = ["HARRIS + SIFT", "SIFT","ORB"]

def printMatches(img1, img2, k1, k2, sel_matches, name):
	h1, w1 = img1.shape[:2]
	h2, w2 = img2.shape[:2]
	view = sp.zeros((max(h1, h2), w1 + w2, 3), sp.uint8)
	view[:h1, :w1, :] = img1  
	view[:h2, w1:, :] = img2
	view[:, :, 1] = view[:, :, 0]  
	view[:, :, 2] = view[:, :, 0]
	cp = view.copy()

	num = 0
	for m in sel_matches:
		color = tuple([sp.random.randint(0, 255) for _ in range(3)])
		cv2.line(view, (int(k1[m.queryIdx].pt[0]), int(k1[m.queryIdx].pt[1])) , (int(k2[m.trainIdx].pt[0] + w1), int(k2[m.trainIdx].pt[1])), color)
		cv2.imwrite("resultats/"+name+"_"+str(num)+".png", view)
		view = cp.copy()
		num = num + 1

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

		kpROI = vc.point_selection(imgROIGray, psAlg, True)				# Get Keypoints
		kp1, desROI = vc.feature_extraction(imgROIGray, kpROI, feAlg)	# Get features

		kpRobot = vc.point_selection(imgRobotGray, psAlg, True)					# Get points
		kp2, desRobot = vc.feature_extraction(imgRobotGray, kpRobot, feAlg)	# Get features

		good = vc.matching2(imgROI, imgRobot, desROI, desRobot, kp1, kp2, feAlg)	# Find matching point

		printMatches(imgROI, imgRobot, kp1, kp2, good, algsName[i]+"_"+str(z))
	print("\n")
