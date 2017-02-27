import cv2
import numpy as np

img = cv2.imread('scene.jpg', 0)
img = cv2.resize(img, (0,0), fx=0.3, fy=0.3)

kernel = np.ones((3,3), np.uint8)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))

img_erosion = cv2.erode(img, kernel, iterations=1)
img_dilation = cv2.dilate(img, kernel, iterations=1)
img_open = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

cv2.imshow('Input', img)
#cv2.imshow('Erosion', img_erosion)
#cv2.imshow('Dilation', img_dilation)
cv2.imshow('Open', img_dilation)

cv2.waitKey(0)
