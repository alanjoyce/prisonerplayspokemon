import cv2
import numpy as np

c = cv2.VideoCapture(0)

previousPieces = []

while(1):
	_,img = c.read()
	height, width, depth = img.shape
	
	#Get pieces of image
	pieces = []
	
	#Row 1
	pieces[0][0] = img[0:height/3, 0:width/3]
	pieces[0][1] = img[0:height/3, width/3:width*2/3]
	pieces[0][2] = img[0:height/3, width*2/3:width]
	
	#Row 2
	pieces[1][0] = img[height/3:height*2/3, 0:width/3]
	pieces[1][1] = img[height/3:height*2/3, width/3:width*2/3]
	pieces[1][2] = img[height/3:height*2/3, width*2/3:width]
	
	#Row 3
	pieces[2][0] = img[height*2/3:height, 0:width/3]
	pieces[2][1] = img[height*2/3:height, width/3:width*2/3]
	pieces[2][2] = img[height*2/3:height, width*2/3:width]
	
	#Initialize previousPieces if needed
	if(len(previousPieces) == 0) previousPieces = pieces
	
	#Check for movement between previousPieces and pieces
	mov = [[0,0,0],[0,0,0],[0,0,0]]
	
	
	#Update previousPieces
	previousPieces = pieces
	
	#Row 1
	cv2.rectangle(img, (0,0), (width/3,height/3), (mov[0][0],0,0), 5)
	cv2.rectangle(img, (width/3,0), (width*2/3,height/3), (mov[0][1],0,0), 5)
	cv2.rectangle(img, (width*2/3,0), (width,height/3), (mov[0][2],0,0), 5)
	
	#Row 2
	cv2.rectangle(img, (0,height/3), (width/3,height*2/3), (mov[1][0],0,0), 5)
	cv2.rectangle(img, (width/3,height/3), (width*2/3,height*2/3), (mov[1][1],0,0), 5)
	cv2.rectangle(img, (width*2/3,height/3), (width,height*2/3), (mov[1][2],0,0), 5)
	
	#Row 3
	cv2.rectangle(img, (0,height*2/3), (width/3,height), (mov[2][0],0,0), 5)
	cv2.rectangle(img, (width/3,height*2/3), (width*2/3,height), (mov[2][1],0,0), 5)
	cv2.rectangle(img, (width*2/3,height*2/3), (width,height), (mov[2][2],0,0), 5)
	
	cv2.imshow('e2', img)
	if cv2.waitKey(5) == 27:
		break

cv2.destroyAllWindows()