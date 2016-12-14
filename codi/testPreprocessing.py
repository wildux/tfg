import cv2
import matplotlib.pyplot as plt
import numpy as np

img = cv2.imread('object3.jpg', 0)

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(2,2))
imgGaussian = cv2.GaussianBlur(img,(5,5),0)
imgMedian = cv2.medianBlur(img,5)
imgBilateral = cv2.bilateralFilter(img,5,20,20)
imgContrast =cv2.equalizeHist(img)
imgClahe = clahe.apply(img)
ret,imgBin = cv2.threshold(imgClahe,90,255,cv2.THRESH_BINARY)

'''
img = imgClahe
dft = cv2.dft(np.float32(img),flags = cv2.DFT_COMPLEX_OUTPUT)
dft_shift = np.fft.fftshift(dft)
magnitude_spectrum = 20*np.log(cv2.magnitude(dft_shift[:,:,0],dft_shift[:,:,1]))

rows, cols = img.shape
crow,ccol = rows/2 , cols/2

# create a mask first, center square is 1, remaining all zeros
mask = np.zeros((rows,cols,2),np.uint8)
mask[crow-30:crow+30, ccol-30:ccol+30] = 1

# apply mask and inverse DFT
fshift = dft_shift*mask
f_ishift = np.fft.ifftshift(fshift)
img_back = cv2.idft(f_ishift)
img_back = cv2.magnitude(img_back[:,:,0],img_back[:,:,1])
'''

titles = ["Gaussian", "Mediana", "Bilateral", "Equalització", "Clahe", "Binarització"]
images = [imgGaussian, imgMedian, imgBilateral, imgContrast, imgClahe, imgBin]

fig = plt.figure()
for i in range(6):
	fig.add_subplot(2,3,i+1),plt.imshow(images[i],'gray')
	plt.title(titles[i])
	plt.xticks([]),plt.yticks([])
plt.show()

fig.savefig("pre-processat.png")
