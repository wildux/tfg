import cv2
import numpy as np
from matplotlib import pyplot as plt

_SIFT = 0
_SURF = 1
_ORB = 2
_BRISK = 3

_HARRIS = 5
_SHI_TOMASI = 6
_FAST = 7
_STAR = 8
_MSER = 9

_BRIEF = 5
_LATCH = 6
_FREAK = 7
_DAISY = 8

MIN_MATCH_COUNT = 10

#TODO: Make this local params
refPt = []			# List of reference points
cropping = False	# Cropping being performed
sel_rect_endpoint = []
img = None

def click_and_crop(event, x, y, flags, param):
	global refPt, cropping, sel_rect_endpoint, img	# grab references to the global var.
 
	if event == cv2.EVENT_LBUTTONDOWN:	# Initial coordinates. Cropping = true
		cropping = True
		refPt = [(x, y)]
 
	elif event == cv2.EVENT_LBUTTONUP:	# End coordinates. Cropping = false (done)
		cropping = False
		refPt.append((x, y))
 
		clone = img.copy()
		cv2.rectangle(clone, refPt[0], refPt[1], (0, 255, 255), 2)	# Draw a rectangle around the ROI
		cv2.imshow("image", clone)

	elif event == cv2.EVENT_MOUSEMOVE and cropping:	# Update position (moving rectangle)
		sel_rect_endpoint = [(x, y)]

def selectROI(image):
	global img, refPt, sel_rect_endpoint
	img = image ###
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

	return img

def imgPrep(image):
	img = cv2.resize(image, (0,0), fx=0.5, fy=0.5)
	#img = cv2.GaussianBlur(img,(3,3),0)
	imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	return img, imgGray

def point_selection(gray, alg):
	kp = []

	#SIFT
	if alg == _SIFT:
		sift = cv2.xfeatures2d.SIFT_create(sigma=1.4)
		kp = sift.detect(gray,None)

	#SURF
	if alg == _SURF:
		surf = cv2.xfeatures2d.SURF_create()
		kp = surf.detect(gray,None)

	#Harris
	elif alg == _HARRIS:		
		G = gray.copy()
		for i in range(5):
			if i != 0:
				G = cv2.pyrDown(G)
			scale = 2**(i)
			corners = cv2.goodFeaturesToTrack(image=G,maxCorners=1000,qualityLevel=0.01,minDistance=scale,useHarrisDetector=1, k=0.04)
			corners = np.int0(corners)
			for corner in corners:
				x,y = corner.ravel()
				k = cv2.KeyPoint(x*scale, y*scale, scale)
				kp.append(k)

	#FAST
	elif alg == _FAST:
		fast = cv2.FastFeatureDetector_create()
		kp = fast.detect(gray,None)

	#STAR
	elif alg == _STAR:
		star = cv2.xfeatures2d.StarDetector_create()
		kp = star.detect(gray,None)

	#GFTT (SHI TOMASI)
	elif alg == _SHI_TOMASI:
		corners = cv2.goodFeaturesToTrack(gray,100000,0.008,1)
		corners = np.int0(corners)
		for i in corners:
			x,y = i.ravel()
			k = cv2.KeyPoint(x, y, 10) #Size (?)
			kp.append(k)

	#ORB
	elif alg == _ORB:
		#if small:
		#	orb = cv2.ORB_create(nfeatures = 2500, nlevels = 8, edgeThreshold = 8, patchSize = 8, fastThreshold = 5)
		#else:
		#	orb = cv2.ORB_create(nfeatures = 50000, nlevels = 8, edgeThreshold = 8, patchSize = 8, fastThreshold = 5)
		orb = cv2.ORB_create(nfeatures = 2500, nlevels = 8, edgeThreshold = 8, patchSize = 8, fastThreshold = 5)
		kp = orb.detect(gray,None)

	#BRISK
	elif alg == _BRISK:
		brisk = cv2.BRISK_create(thresh = 8, octaves = 4)
		kp = brisk.detect(gray,None)

	#MSER
	elif alg == _MSER:
		mser = cv2.MSER_create()
		kp = mser.detect(gray,None)

	return kp

def feature_extraction(image, kp, alg):
	des = []

	#SIFT
	if alg == _SIFT:
		sift = cv2.xfeatures2d.SIFT_create(sigma=1.4)
		kp, des = sift.compute(image, kp)

	#SURF
	elif alg == _SURF:
		surf = cv2.xfeatures2d.SURF_create() #400
		kp, des = surf.compute(image, kp)

	#ORB
	elif alg == _ORB:
		#orb = cv2.ORB_create(nfeatures = 2500, nlevels = 8, edgeThreshold = 8, patchSize = 8, fastThreshold = 5)
		orb = cv2.ORB_create()
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

	#DAISY
	elif alg == _DAISY:
		daisy = cv2.xfeatures2d.DAISY_create()
		kp, des = daisy.compute(image, kp)

	return kp, des

def homography(img1, img2, des1, des2, kp1, kp2, good):
	x = -1; y = -1

	img2C = img2.copy()
	if len(good) >= MIN_MATCH_COUNT:
		src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
		dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
		M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
		matchesMask = mask.ravel().tolist()

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

		img2C = cv2.circle(img2C,(int(x),int(y)), 5, (0,0,255), -1)
	else:
		print("Not enough matches found", len(good),"of", MIN_MATCH_COUNT)
		matchesMask = None

	draw_params = dict(matchColor = (0,255,0), singlePointColor = None, matchesMask = matchesMask, flags = 2)
	img3 = cv2.drawMatches(img1,kp1,img2C,kp2,good,None,**draw_params)
	return x, y, img3


def matching(img1, img2, des1, des2, kp1, kp2, fe):
	if fe == _LATCH or fe == _ORB or fe == _BRISK:
		bf = cv2.BFMatcher(cv2.NORM_HAMMING)
		#bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
	else:
		bf = cv2.BFMatcher()
		#bf = cv2.BFMatcher(crossCheck=True)

	matches = bf.knnMatch(des1, des2, k=2)
	#matches = bf.match(des1,des2)
	#matches = sorted(matches, key = lambda x:x.distance)
	#num = int(len(matches)*0.6)
	#good = matches[:num]

	good = [] # Good matches; Lowe's ratio test
	for m,n in matches:
		if m.distance < 0.75*n.distance:
			good.append(m)
	return good


def getResult(img1, img2, alg1, alg2):
	img1, img1Gray = imgPrep(img1)
	img2, img2Gray = imgPrep(img2)

	kp1 = point_selection(img1Gray, alg1)
	kp2 = point_selection(img2Gray, alg1)

	kp1, des1 = feature_extraction(img1Gray, kp1, alg2)
	kp2, des2 = feature_extraction(img2Gray, kp2, alg2)

	good = matching(img1, img2, des1, des2, kp1, kp2, alg2)
	x, y, img3 = matching(img1, img2, des1, des2, kp1, kp2, good)
	return img3


def getAngle(aV, w, x):
	if x == -1:
		return 0
	else:
		return (aV*x / w) - (aV/2)

#gray2 = np.float32(gray)
		#dst = cv2.cornerHarris(gray2,2,3,0.04)
		#dst = cv2.dilate(dst,None)
		#roi[dst>0.01*dst.max()]=[0,0,255]
