import numpy as np
import MORAS as vc
import cv2

algs = [vc._SIFT, vc._ORB, vc._HARRIS]
algsName = ["SIFT", "ORB", "HARRIS"]
paths = ['images/graff/img1.png', 'images/graff/img3.png', 'images/experiments/uni1.jpg', 'images/experiments/uni2.jpg']

#path = 'images/experiments/uni1.jpg'

for j in range(len(paths)):
	image = cv2.imread(paths[j])
	image = cv2.resize(image, (0,0), fx=0.5, fy=0.5)
	img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	for i in range(len(algs)):
		psAlg = algs[i]
		kp = vc.point_selection(img, psAlg)
		#kp = vc.point_selection(img, vc._SIFT)
#for i in range(100):
	#cv2.drawKeypoints(img,[kp[i]],image,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
		cv2.drawKeypoints(img,kp,image,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
		cv2.imwrite("KP_"+algsName[i]+"_"+str(j)+".jpg", image)
	#cv2.imwrite("SIFT/KP_"+str(i)+"_UNI.jpg", image)
