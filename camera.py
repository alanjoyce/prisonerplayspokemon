import cv2
import numpy as np

c = cv2.VideoCapture(0)

while(1):
	_,img = c.read()
	height, width, depth = img.shape
	
	#Row 1
	cv2.rectangle(img, (0,0), (width/3,height/3), (255,0,0), 5)
	cv2.rectangle(img, (width/3,0), (width*2/3,height/3), (255,0,0), 5)
	cv2.rectangle(img, (width*2/3,0), (width,height/3), (255,0,0), 5)
	
	#Row 2
	cv2.rectangle(img, (0,height/3), (width/3,height*2/3), (255,0,0), 5)
	cv2.rectangle(img, (width/3,height/3), (width*2/3,height*2/3), (255,0,0), 5)
	cv2.rectangle(img, (width*2/3,height/3), (width,height*2/3), (255,0,0), 5)
	
	#Row 3
	cv2.rectangle(img, (0,height*2/3), (width/3,height), (255,0,0), 5)
	cv2.rectangle(img, (width/3,height*2/3), (width*2/3,height), (255,0,0), 5)
	cv2.rectangle(img, (width*2/3,height*2/3), (width,height), (255,0,0), 5)
	
	cv2.imshow('e2', img)
	if cv2.waitKey(5) == 27:
		break

cv2.destroyAllWindows()