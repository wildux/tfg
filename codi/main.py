import MORAS as vc
#from robot.neato import neatoA as neato
import time
from tkinter.filedialog import askopenfilename
import cv2
from tkinter import Tk

root = Tk()
root.withdraw()

'''**********************
VARIABLES
**********************'''
viewAngle = 90		# View Angle (camera)
psAlg = vc._ORB		# Point Selection Algorithm
feAlg = vc._BRISK	# Feature Extraction Algorithm
speed = 100 		# Speed in mm/s
distance = 500 		# Distance in mm

'''**********************
IMAGES
**********************'''
imgPath = askopenfilename()			# Ask for image path
imgScene = cv2.imread(imgPath)		# Global image
imgROI, _ = vc.imgPrep(imgScene)
imgROI = vc.selectROI(imgROI)								# Select ROI
imgROIGray = cv2.cvtColor(imgROI, cv2.COLOR_BGR2GRAY)

imgRobot = cv2.imread('scene.jpg')	# Image captured by the robot
imgRobot, imgRobotGray = vc.imgPrep(imgRobot)

'''**********************
CV 
**********************'''
# GLOBAL IMAGE
kpROI = vc.point_selection(imgROIGray, psAlg, True)				# Get Keypoints
kp1, desROI = vc.feature_extraction(imgROIGray, kpROI, feAlg)	# Get features

clone = imgROI.copy()
cv2.drawKeypoints(imgROI,kp1,clone,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
cv2.imshow("ROI", clone)
#cv2.imwrite("RoiKp.png", clone)

# IMAGE ROBOT
kpRobot = vc.point_selection(imgRobotGray, psAlg)					# Get points
kp2, desRobot = vc.feature_extraction(imgRobotGray, kpRobot, feAlg)	# Get features

clone = imgRobot.copy()
cv2.drawKeypoints(imgRobot,kp2,clone,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
cv2.imshow("Robot", clone)
#cv2.imwrite("RobotKp.png", clone)

#MATCHING
x, y, img3 = vc.matching(imgROI, imgRobot, desROI, desRobot, kp1, kp2, feAlg)	# Find matching point
cv2.imshow("Matching", img3)
#cv2.imwrite("homography2.png", img3)

#ANGLE
angle = vc.getAngle(viewAngle, imgRobot.shape[1], x)	# Get angle (to move robot)
print(angle)


'''
#MOVE ROBOT
# Connection
connected = neato.connect()
if not connected:
	print "Connection failed."
	exit(1)

print "Wait 3 seconds..."
time.sleep(3) #Wait 3 seconds

neato.turn_precise(-angle, speed, 0.3)					# Rotate robot
neato.advance_precise(distance, distance, speed, 0.3)	# Move robot

neato.close()
'''

while(True):
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break
