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
feAlg = vc._SURF	# Feature Extraction Algorithm
speed = 100 		# Speed in mm/s
distance = 500 		# Distance in mm

'''**********************
IMAGES
**********************'''
#imgPath = askopenfilename()			# Ask for image path
#imgScene = cv2.imread(imgPath)		# Global image
imgROI = cv2.imread('object4.jpg')		# Global image
imgROI = cv2.medianBlur(imgROI,1)
imgROI = cv2.resize(imgROI, (0,0), fx=0.3, fy=0.3)


imgRobot = cv2.imread('scene.jpg')	# Image captured by the robot
imgRobot = cv2.medianBlur(imgRobot,1)
imgRobot = cv2.resize(imgRobot, (0,0), fx=0.3, fy=0.3)


'''**********************
CV 
**********************'''
# Global image
#imgROI = vc.selectROI(imgScene)								# Select ROI
kpROI, imgKpROI = vc.point_selection(imgROI, psAlg)					# Get Keypoints
kp1, desROI = vc.feature_extraction(imgROI, kpROI, feAlg)	# Get features
cv2.imshow("ROI", imgKpROI)

'''
TODO: Loop --> Get picture (robot), features, match, move until the robot is placed in front of the object or there is no match
If there is no match (initially), rotate the robot (scan area 360º)
'''

# Image captured by the robot
kpRobot, imgKpRobot = vc.point_selection(imgRobot, psAlg)			# Get points
kp2, desRobot = vc.feature_extraction(imgRobot, kpRobot, feAlg)	# Get features
cv2.imshow("Robot", imgKpRobot)

x, y = vc.matching(imgROI, imgRobot, desROI, desRobot, kp1, kp2, feAlg)	# Find matching point
angle = vc.getAngle(viewAngle, imgRobot.shape[1], x)	# Get angle (to move robot)
print(angle)


'''
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
