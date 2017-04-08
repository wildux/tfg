from timeit import default_timer as timer
import numpy as np
import MORAS as vc
import cv2

#EXECUCIÓ
imgs1 = ['images/experiments/uni_2.jpg', 'images/experiments/uni4_2.jpg', 'images/experiments/motos3.png', 'images/experiments/cars4.png', 'images/experiments/uni1.jpg',
		'images/experiments/jardi_2.jpg', 'images/experiments/jardi_sel.jpg', 'images/experiments/uni_sel.jpg', 'images/experiments/jardi_sel.jpg', 'images/experiments/uni_sel.jpg']

imgs2 = ['images/experiments/uni.jpg', 'images/experiments/uni4.jpg', 'images/experiments/motos1.png', 'images/experiments/cars6.png', 'images/experiments/uni2.jpg',
		'images/experiments/jardi2.jpg', 'images/experiments/jardi_2.jpg', 'images/experiments/uni1.jpg', 'images/experiments/uni1.jpg', 'images/experiments/jardi_2.jpg']

algs1 = [vc._HARRIS, vc._SIFT, vc._ORB, vc._ORB]
algs2 = [vc._SIFT, vc._SIFT, vc._ORB, vc._BRISK]
algsName = ["HARRIS_SIFT", "SIFT", "ORB", "ORB_BRISK"]


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
		matches = []
		kpROI = []
		kpRobot = []
		for j in range(len(times)):
			start = timer()

			kpROI = vc.point_selection(imgROIGray, psAlg)				# Get Keypoints
			kp1, desROI = vc.feature_extraction(imgROIGray, kpROI, feAlg)	# Get features

			kpRobot = vc.point_selection(imgRobotGray, psAlg)					# Get points
			kp2, desRobot = vc.feature_extraction(imgRobotGray, kpRobot, feAlg)	# Get features

			matches = vc.matching(imgROI, imgRobot, desROI, desRobot, kp1, kp2, feAlg)	# Find matching point
			end = timer()
			times[j] = end - start
			
			if len(matches) >= 10:
				src_pts = np.float32([ kp1[m.queryIdx].pt for m in matches ]).reshape(-1,1,2)
				dst_pts = np.float32([ kp2[m.trainIdx].pt for m in matches ]).reshape(-1,1,2)
				M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
				matchesMask = mask.ravel().tolist()

				good_matches = []
				discarded_matches = []
				for m in range(len(matchesMask)):
					if matchesMask[m] == 1:
						good_matches.append(matches[m])
					else:
						discarded_matches.append(matches[m])
			else:
				good_matches = matches
				discarded_matches = []

		draw_params = dict(matchColor = (0,255,0), singlePointColor = None, flags = 2)
		img3 = cv2.drawMatches(imgROI,kp1,imgRobot,kp2,good_matches,None,**draw_params)
		img4 = cv2.drawMatches(imgROI,kp1,imgRobot,kp2,discarded_matches,None,**draw_params)
		cv2.imwrite("resultats/2.1/ransac_matches/"+algsName[i]+"/"+str(z)+".png", img3)
		cv2.imwrite("resultats/2.1/discarded_matches/"+algsName[i]+"/"+str(z)+".png", img4)

		x, y, img3 = vc.homography(imgROI, imgRobot, desROI, desRobot, kp1, kp2, matches)	# Find matching point
		cv2.imwrite("resultats/2.1/homography/"+algsName[i]+"/"+str(z)+".png", img3)
		img4 = cv2.circle(imgRobot,(int(x),int(y)), 5, (0,0,255), -1)
		cv2.imwrite("resultats/2.1/punts/"+algsName[i]+"/"+str(z)+".png", img4)

		#print(name, np.mean(times), "Ransac matches: "+str(len(good_matches)))
		print(name, np.mean(times), "Total matches: "+str(len(matches)), "Ransac matches: "+str(len(good_matches)))
		print(name, "Keypoints: "+str(len(kpROI)), str(len(kpRobot)))
	print("\n")

