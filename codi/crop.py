import argparse
import cv2
import numpy as np
 
refPt = [] # List of reference points
cropping = False # Cropping being performed
sel_rect_endpoint = []
 
def click_and_crop(event, x, y, flags, param):
	global refPt, cropping, sel_rect_endpoint # grab references to the global var.
 
	
	# Starting (x, y) coordinates. Cropping = true
	if event == cv2.EVENT_LBUTTONDOWN:
		cropping = True
		refPt = [(x, y)]
 
	# Ending (x, y) coordinates. Cropping = false (done)
	elif event == cv2.EVENT_LBUTTONUP:
		cropping = False
		refPt.append((x, y))
 
		# Draw a rectangle around the RoI
		clone = image.copy()
		cv2.rectangle(clone, refPt[0], refPt[1], (0, 255, 255), 2)
		cv2.imshow("image", clone)

	elif event == cv2.EVENT_MOUSEMOVE and cropping:
		sel_rect_endpoint = [(x, y)]


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Image path")
args = vars(ap.parse_args())
 
# load the image, clone it, and setup the mouse callback function
image = cv2.imread(args["image"])
clone = image.copy()
cv2.namedWindow("image")
cv2.setMouseCallback("image", click_and_crop)
cv2.imshow('image', image) 

while True:
	# Display the image and wait for a keypress.
	if not cropping:
		#cv2.imshow('image', image)
		sel_rect_endpoint = []
	elif cropping and sel_rect_endpoint:	# Display rectangle (moving)
		rect_cpy = image.copy()
		cv2.rectangle(rect_cpy, refPt[0], sel_rect_endpoint[0], (0, 255, 0), 1)
		cv2.imshow('image', rect_cpy)
	key = cv2.waitKey(1) & 0xFF
 
	# Reset if the 'r' key is pressed.
	if key == ord("r"):
		image = clone.copy()
 
	# If the 'c' key is pressed, break.
	elif key == ord("c"):
		break
 
# if there are two reference points, then crop the region of interest from the image and display it
if len(refPt) == 2:
	roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
	cv2.imshow("ROI", roi)
	gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

	print('POINTS SELECTION:\n')
	print('1: DoG (SIFT)')
	print('2: Harris')
	print('3: FAST')
	print('4: STAR')
	print('5: GFTT')

	while True:
		key = cv2.waitKey(1) & 0xFF
	 
		#DoG
		if key == ord("1"):
			sift = cv2.xfeatures2d.SIFT_create()
			kp = sift.detect(gray,None)			
			cv2.drawKeypoints(gray,kp,roi,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
			cv2.imshow("ROI", roi)

		#Harris
		elif key == ord("2"):
			gray2 = np.float32(gray)
			dst = cv2.cornerHarris(gray2,2,3,0.04)
			dst = cv2.dilate(dst,None)			
			roi[dst>0.01*dst.max()]=[0,0,255]
			cv2.imshow("ROI", roi)

		#FAST
		elif key == ord("3"):
			fast = cv2.FastFeatureDetector_create()
			kp = fast.detect(gray,None)
			cv2.drawKeypoints(gray,kp,roi,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
			cv2.imshow("ROI", roi)

		#STAR
		elif key == ord("4"):
			star = cv2.xfeatures2d.StarDetector_create()
			kp = star.detect(gray,None)
			cv2.drawKeypoints(gray,kp,roi,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
			cv2.imshow("ROI", roi)

		#GFTT
		elif key == ord("5"):
			corners = cv2.goodFeaturesToTrack(gray,25,0.01,10)
			corners = np.int0(corners)
			for i in corners:
				x,y = i.ravel()
				cv2.circle(roi,(x,y),3,255,-1)
			print(corners[0])
			cv2.imshow("ROI", roi)


		elif key == ord("q"):
			break

	print('FEATURES EXTRACTION:\n')
	print('1: SIFT')
	print('2: SURF')
	print('3: ORB')
	print('4: BRIEF')
	
	while True:
		key = cv2.waitKey(1) & 0xFF
	 
		#SIFT
		if key == ord("1"):
			sift = cv2.xfeatures2d.SIFT_create()
			kp, des = sift.compute(img, kp)

		#SURF
		if key == ord("2"):
			surf = cv2.xfeatures2d.SURF_create(400)
			kp, des = surf.compute(img, kp)

		#ORB
		if key == ord("3"):
			orb = cv2.ORB_create()
			kp, des = orb.compute(img, kp)

		#BRIEF
		if key == ord("4"):
			brief = cv2.BriefDescriptorExtractor_create()
			kp, des = brief.compute(img, kp)

		#
		if key == ord("5"):
			brief = cv2.BriefDescriptorExtractor_create()
			kp, des = brief.compute(img, kp)
 
		elif key == ord("q"):
			print("hola")
			break
 

cv2.destroyAllWindows()
