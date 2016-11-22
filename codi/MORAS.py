import cv2
import numpy as np
from matplotlib import pyplot as plt

_HARRIS = 5
_SHI_TOMASI = 6
_FAST = 7
_STAR = 8

_BRIEF = 5
_LATCH = 6
_FREAK = 7

_SIFT = 0
_SURF = 1
_ORB = 2
_BRISK = 3

MIN_MATCH_COUNT = 10

refPt = []			# List of reference points
cropping = False	# Cropping being performed
sel_rect_endpoint = []

img = None

def click_and_crop(event, x, y, flags, param):
	global refPt, cropping, sel_rect_endpoint, img # grab references to the global var.
 
	# Starting (x, y) coordinates. Cropping = true
	if event == cv2.EVENT_LBUTTONDOWN:
		cropping = True
		refPt = [(x, y)]
 
	# Ending (x, y) coordinates. Cropping = false (done)
	elif event == cv2.EVENT_LBUTTONUP:
		cropping = False
		refPt.append((x, y))
 
		# Draw a rectangle around the RoI
		clone = img.copy()
		cv2.rectangle(clone, refPt[0], refPt[1], (0, 255, 255), 2)
		cv2.imshow("image", clone)

	elif event == cv2.EVENT_MOUSEMOVE and cropping:
		sel_rect_endpoint = [(x, y)]

def selectROI(image):
	global img, refPt, sel_rect_endpoint
	img = image
	cv2.namedWindow("image")
	cv2.setMouseCallback("image", click_and_crop)
	cv2.imshow('image', img)

	while True:
		if not cropping:
			sel_rect_endpoint = []
		elif cropping and sel_rect_endpoint:	# Display rectangle (moving)
			clone = img.copy()
			cv2.rectangle(clone, refPt[0], sel_rect_endpoint[0], (0, 255, 0), 1)
			cv2.imshow('image', clone)
		
		if (cv2.waitKey(1) & 0xFF) == ord("c"):
			break

	cv2.destroyAllWindows()
	if len(refPt) == 2:
		img = img[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
		#cv2.imshow("ROI",img)
	return img

def point_selection(roi, alg):
	gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
	kp = []

	#SIFT
	if alg == _SIFT:
		sift = cv2.xfeatures2d.SIFT_create()
		kp = sift.detect(gray,None)
		#cv2.drawKeypoints(gray,kp,roi,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

	#SURF
	if alg == _SURF:
		surf = cv2.xfeatures2d.SURF_create()
		kp = surf.detect(gray,None)

	#Harris
	elif alg == _HARRIS:
		gray2 = np.float32(gray)
		dst = cv2.cornerHarris(gray2,2,3,0.04)
		dst = cv2.dilate(dst,None)
		roi[dst>0.01*dst.max()]=[0,0,255]

	#FAST
	elif alg == _FAST:
		fast = cv2.FastFeatureDetector_create()
		kp = fast.detect(gray,None)
		#cv2.drawKeypoints(gray,kp,roi,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

	#STAR
	elif alg == _STAR:
		star = cv2.xfeatures2d.StarDetector_create()
		kp = star.detect(gray,None)
		#cv2.drawKeypoints(gray,kp,roi,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

	#GFTT (SHI TOMASI)
	elif alg == _SHI_TOMASI:
		corners = cv2.goodFeaturesToTrack(gray,5000,0.01,10)
		corners = np.int0(corners)
		for i in corners:
			x,y = i.ravel()
			#cv2.circle(roi,(x,y),3,255,-1)
			k = cv2.KeyPoint(x, y, 10)
			kp.append(k)
			#cv2.drawKeypoints(gray,kp,roi,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
		#print(corners[0])
	
	#ORB
	elif alg == _ORB:
		orb = cv2.ORB_create(nfeatures = 50000, nlevels = 8, edgeThreshold = 8, patchSize = 8, fastThreshold = 5)
		kp = orb.detect(gray,None)

	#BRISK
	elif alg == _BRISK:
		brisk = cv2.BRISK_create(thresh = 8, octaves = 4)
		kp = brisk.detect(gray,None)

	clone = roi.copy()
	cv2.drawKeypoints(gray,kp,clone,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

	#cv2.imshow("ROI", clone)
	return kp, clone

def feature_extraction(image, kp, alg):
	des = []
	
	#SIFT
	if alg == _SIFT:
		sift = cv2.xfeatures2d.SIFT_create()
		kp, des = sift.compute(image, kp)

	#SURF
	elif alg == _SURF:
		surf = cv2.xfeatures2d.SURF_create() #400
		kp, des = surf.compute(image, kp)

	#ORB
	elif alg == _ORB:
		orb = cv2.ORB_create(nfeatures = 50000, nlevels = 8, edgeThreshold = 8, patchSize = 8, fastThreshold = 5)
		kp, des = orb.compute(image, kp)

	#BRIEF
	elif alg == _BRIEF:
		brief = cv2.BriefDescriptorExtractor_create()
		kp, des = brief.compute(image, kp)

	#LATCH
	elif alg == _LATCH:
		latch = cv2.xfeatures2d.LATCH_create()
		kp, des = latch.compute(image, kp)

	#BRISK
	elif alg == _BRISK:
		brisk = cv2.BRISK_create(thresh = 8, octaves = 4)
		kp, des = brisk.compute(image, kp)

	#FREAK
	elif alg == _FREAK:
		freak = cv2.xfeatures2d.FREAK_create()
		kp, des = freak.compute(image, kp)

	return kp, des

def matching(img1, img2, des1, des2, kp1, kp2, fe ,rs=True):
	if fe == _LATCH or fe == _ORB or fe == _BRISK:
		bf = cv2.BFMatcher(cv2.NORM_HAMMING)
	else:
		bf = cv2.BFMatcher()

	matches = bf.knnMatch(des1, des2, k=2)
	x = -1
	y = -1

	# store all the good matches as per Lowe's ratio test.
	
	good = []
	for m,n in matches:
		if m.distance < 0.8*n.distance:
			good.append(m)

	if len(good) >= MIN_MATCH_COUNT:
		src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
		dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

		M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0) #If Ransac
		matchesMask = mask.ravel().tolist()

		img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
		h,w = img1.shape
		pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
		dst = cv2.perspectiveTransform(pts,M)

		img2 = cv2.polylines(img2,[np.int32(dst)],True,255,3, cv2.LINE_AA)

		#RETURN POINT
		x1, y1 = np.int32(dst)[0].ravel()
		x2, y2 = np.int32(dst)[1].ravel()
		x3, y3 = np.int32(dst)[2].ravel()
		x4, y4 = np.int32(dst)[3].ravel()
		x = (x1+x2+x3+x4)/4
		y = (y1+y2+y3+y4)/4

	else:
		print("Not enough matches are found", len(good),"of",MIN_MATCH_COUNT)
		matchesMask = None


	draw_params = dict(matchColor = (0,255,0), # draw matches in green color
					   singlePointColor = None,
					   matchesMask = matchesMask, # draw only inliers
					   flags = 2)

	img3 = cv2.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)
	plt.imshow(img3, 'gray'),plt.show()

	return x, y

def getPoint(sl):
	x = 0
	y = 0
	return x,y

def getAngle(aV, w, x):
	if x == -1:
		return 0
	else:
		return (aV*x / w) - (aV/2)

def moveRobot(o):
	st = "ok"
	return st
