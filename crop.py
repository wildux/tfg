import argparse
import cv2
 
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
	cv2.waitKey(0)
	gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
	
	sift = cv2.xfeatures2d.SIFT_create()
	kp = sift.detect(gray,None)
	#(kps, descs) = sift.detectAndCompute(gray, None)
	cv2.drawKeypoints(gray,kp,roi,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	cv2.imshow("ROI", roi)
	cv2.waitKey(0)
	#print("# kps: {}, descriptors: {}".format(len(kps), descs.shape))

	#surf = cv2.xfeatures2d.SURF_create()
	#(kps, descs) = surf.detectAndCompute(gray, None)
	#print("# kps: {}, descriptors: {}".format(len(kps), descs.shape))
 

cv2.destroyAllWindows()
