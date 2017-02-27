import MORAS as vc
import cv2

'''**********************
IMAGES
**********************'''

img1 = cv2.imread('images/menjador_sel.jpg')
img2 = cv2.imread('images/menjador2.jpg')
alg1 = vc._ORB
alg2 = vc._ORB

'''**********************
CV 
**********************'''
# GLOBAL IMAGE
img3 = vc.getResult(img1, img2, alg1, alg2)
cv2.imshow("Matching", img3)
cv2.imwrite("resultats/menjador.png", img3)


while(True):
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break
