import cv2
import numpy as np

c = cv2.VideoCapture(0)

prevPrevPieces = []
prevPieces = []
mov = []

while(1):
	img = c.read()[1]
	height, width, depth = img.shape
	gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
	
	#Get pieces of image
	pieces = [[0,0,0],[0,0,0],[0,0,0]]
	
	#Row 1
	pieces[0][0] = gray[0:height/3, 0:width/3]
	pieces[0][1] = gray[0:height/3, width/3:width*2/3]
	pieces[0][2] = gray[0:height/3, width*2/3:width]
	
	#Row 2
	pieces[1][0] = gray[height/3:height*2/3, 0:width/3]
	pieces[1][1] = gray[height/3:height*2/3, width/3:width*2/3]
	pieces[1][2] = gray[height/3:height*2/3, width*2/3:width]
	
	#Row 3
	pieces[2][0] = gray[height*2/3:height, 0:width/3]
	pieces[2][1] = gray[height*2/3:height, width/3:width*2/3]
	pieces[2][2] = gray[height*2/3:height, width*2/3:width]
	
	#Initialize prevPieces if needed
	if len(prevPieces) == 0:
		prevPieces = pieces
	if len(prevPrevPieces) == 0:
		prevPrevPieces = pieces
	if len(mov) == 0:
		mov = [[0,0,0],[0,0,0],[0,0,0]]
	
	#Check for movement between previousPieces and pieces
	for i in range(len(pieces)):
		for j in range(len(pieces[0])):
			d1 = cv2.absdiff(pieces[i][j], prevPieces[i][j])
			d2 = cv2.absdiff(prevPieces[i][j], prevPrevPieces[i][j])
			result = cv2.bitwise_and(d1, d2)
			result = cv2.threshold(result, 35, 255, cv2.THRESH_BINARY)[1]
			totalDiff = sum(sum(x) for x in result)
			if totalDiff > 1000:
				mov[i][j] = 255
			elif mov[i][j] > 0:
				mov[i][j] = max(mov[i][j] - 25, 0)
	
	#Update previousPieces
	prevPrevPieces = prevPieces
	prevPieces = pieces
	
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