import MORAS as vc
import cv2

'''**********************
IMAGES
**********************'''

img1 = cv2.imread('images/experiments/uni5_sel.jpg')
img2 = cv2.imread('images/experiments/uni5.jpg')
alg1 = vc._SIFT
alg2 = vc._SIFT

'''**********************
CV 
**********************'''
# GLOBAL IMAGE
img3 = vc.getResult(img1, img2, alg1, alg2)
cv2.imshow("Matching", img3)
cv2.imwrite("resultats/uniSel5.png", img3)


while(True):
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break
