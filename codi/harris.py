import cv2
import numpy as np
import MORAS as vc
from timeit import default_timer as timer
'''**********************
IMAGES
**********************'''

img = cv2.imread('images/all.ppm')	# Image
img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

imgRobot = cv2.imread('scene.jpg')	# Image captured by the robot
imgRobot = cv2.resize(imgRobot, (0,0), fx=0.3, fy=0.3)
imgRobotGray = cv2.cvtColor(imgRobot, cv2.COLOR_BGR2GRAY)

feAlg = vc._ORB	# Feature Extraction Algorithm

'''**********************
CV 
**********************'''
kp = []
G = imgGray.copy()

start = timer()
for i in range(5):
	if i != 0:
		G = cv2.pyrDown(G)
	scale = 2**(i)
	corners = cv2.goodFeaturesToTrack(G,1000,0.01,scale,useHarrisDetector=1, k=0.04)
	corners = np.int0(corners)
	for corner in corners:
		x,y = corner.ravel()
		k = cv2.KeyPoint(x*scale, y*scale, scale)
		kp.append(k)
end = timer()

clone = img.copy()
cv2.drawKeypoints(img,kp,clone,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
cv2.imshow("ROI", clone)
#kp, des = vc.feature_extraction(imgGray, kp, feAlg)	# Get features

print("Time: ",end-start)
#MATCHING
#x, y, img3 = vc.matching(img, imgRobot, des, desRobot, kp, kpR, feAlg)	# Find matching point
#cv2.imshow("Matching", img3)


#cv2.pyrDown()
#cv2.imwrite("RoiKp.png", clone)


#a = np.unravel_index(dst.argmax(),dst.shape)
#print(a)


#ORB
#orb = cv2.ORB_create(nfeatures = 50000, nlevels = 8, edgeThreshold = 8, patchSize = 8, fastThreshold = 5)
#kp, des = orb.compute(image, kp)

if cv2.waitKey(0) & 0xff == 27:
	cv2.destroyAllWindows()
