import MORAS as vc
import cv2
import numpy as np

'''**********************
IMAGES
**********************'''

img1 = cv2.imread('images/experiments/uni_sel.jpg')
img1, imgROIGray = vc.imgPrep(img1)
img2 = cv2.imread('images/experiments/uni1.jpg')
img2, imgRobotGray = vc.imgPrep(img2)

psAlg = vc._SIFT
feAlg = vc._SIFT

MIN_MATCH_COUNT = 10

'''**********************
CV 
**********************'''
kpROI = vc.point_selection(imgROIGray, psAlg)				# Get Keypoints
kp1, des1 = vc.feature_extraction(imgROIGray, kpROI, feAlg)	# Get features

kpRobot = vc.point_selection(imgRobotGray, psAlg)					# Get points
kp2, des2 = vc.feature_extraction(imgRobotGray, kpRobot, feAlg)	# Get features

good = vc.matching(imgROIGray, imgRobotGray, des1, des2, kp1, kp2, feAlg) #Get matches


#good = sorted(good, key = lambda x:x.distance)
x = -1; y = -1
img2C = img2.copy()

if len(good) >= MIN_MATCH_COUNT:
	src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
	dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
	M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
	matchesMask = mask.ravel().tolist()

	good_matches = []
	for i in range(len(matchesMask)):
		if matchesMask[i] == 1:
			good_matches.append(good[i])

	#if len(good) >= 4:
	#src_pts = np.float32([ kp1[m.queryIdx].pt for m in good_matches ]).reshape(-1,1,2)
	#dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good_matches ]).reshape(-1,1,2)
	#M, mask = cv2.findHomography(src_pts, dst_pts, cv2.LMEDS)
	#matchesMask = mask.ravel().tolist()

	h,w,_ = img1.shape
	pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
	dst = cv2.perspectiveTransform(pts,M)
	img2C = cv2.polylines(img2C,[np.int32(dst)],True,255,3, cv2.LINE_AA)

	#RETURN POINT
	x1, y1 = np.int32(dst)[0].ravel()
	x2, y2 = np.int32(dst)[1].ravel()
	x3, y3 = np.int32(dst)[2].ravel()
	x4, y4 = np.int32(dst)[3].ravel()
	x = (x1+x2+x3+x4)/4
	y = (y1+y2+y3+y4)/4

	#draw_params = dict(matchColor = (0,255,0), singlePointColor = None, matchesMask = matchesMask, flags = 2)
	#img3 = cv2.drawMatches(img1,kp1,img2C,kp2,good_matches,None,**draw_params)
	#draw_params = dict(matchColor = (0,255,0), singlePointColor = None, flags = 2)
	#img3 = cv2.drawMatches(img1,kp1,img2,kp2,good_matches,None,**draw_params)
	img3 = cv2.circle(img2,(int(x),int(y)), 5, (0,0,255), -1)
	cv2.imshow("Matching", img3)
	print(len(good_matches))
	
	#print(good_matches[0])
	

	#else:
	#	print("Not enough matches found", len(good),"of", MIN_MATCH_COUNT)
else:
	print("Not enough matches found", len(good),"of", MIN_MATCH_COUNT)


while(True):
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break
