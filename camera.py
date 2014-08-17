import cv2
import numpy as np
import os
import time
from time import sleep
import thread

c = cv2.VideoCapture(0)

prevPrevPieces = []
prevPieces = []
mov = []

lastPress = time.time()
lastButton = "u"
toPress = {}

def systemKeystroke(char):
	cmd = "osascript -e 'tell application \"System Events\" to keystroke \"" + char + "" + char + "" + char + "" + char + "" + char + "" + char + "" + char + "" + char + "" + char + "" + char + "" + char + "" + char + "\"'"
	#cmd = "osascript -e 'tell application \"System Events\" to key down \"" + char + "\"'"
	#os.system(cmd)
	#cmd = "osascript -e 'tell application \"System Events\" to delay 0.5'"
	#os.system(cmd)
	#cmd = "osascript -e 'tell application \"System Events\" to key up \"" + char + "\"'"
	os.system(cmd)

def pressButton(char):
	global lastPress
	global lastButton
	global toPress
	
	#Rate limit to 1 button per half-second
	#Pick the button with the most motion
	#If no motion, use the last pressed button
	if time.time() - lastPress >= 0.5:
		maxValue = 0
		maxKey = ""
		for key, value in toPress.iteritems():
			if value > maxValue:
				maxKey = key
		
		if maxKey == "":
			maxKey = lastButton
		
		try:
			#thread.start_new_thread(systemKeystroke, (maxKey, ))
			systemKeystroke(maxKey)
		except:
			print "Error starting thread"
		
		lastPress = time.time()
		lastButton = maxKey
		toPress = {}
	elif char != "":
		toPress[char] = toPress.get(char, 0) + 1

ix = 0
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
	#Use ix to only process 1/3 of the grid each iteration to save time
	for i in [ix]:
		for j in range(len(pieces[0])):
			d1 = cv2.absdiff(pieces[i][j], prevPieces[i][j])
			d2 = cv2.absdiff(prevPieces[i][j], prevPrevPieces[i][j])
			result = cv2.bitwise_and(d1, d2)
			result = cv2.threshold(result, 35, 255, cv2.THRESH_BINARY)[1]
			totalDiff = sum(sum(x) for x in result)
			if totalDiff > 1000:
				mov[i][j] = 255
			else:
				mov[i][j] = 0
	ix = ix + 1
	if ix > len(pieces) - 1:
		ix = 0
	
	m = 0
	#Row 1
	if mov[0][0]:
		pressButton("a")
	cv2.rectangle(img, (0,0), (width/3,height/3), (mov[0][0],0,0), 5)
	if lastButton == "a":
		m = 255
	cv2.putText(img, "A", (width/6, height/6), cv2.FONT_HERSHEY_PLAIN, 3, (255,m,0), 5)
	m = 0
	
	if mov[0][1]:
		pressButton("u")
	cv2.rectangle(img, (width/3,0), (width*2/3,height/3), (mov[0][1],0,0), 5)
	if lastButton == "u":
		m = 255
	cv2.putText(img, "U", (width/2, height/6), cv2.FONT_HERSHEY_PLAIN, 3, (255,m,0), 5)
	m = 0
	
	if mov[0][2]:
		pressButton("b")
	cv2.rectangle(img, (width*2/3,0), (width,height/3), (mov[0][2],0,0), 5)
	if lastButton == "b":
		m = 255
	cv2.putText(img, "B", (width*5/6, height/6), cv2.FONT_HERSHEY_PLAIN, 3, (255,m,0), 5)
	m = 0
	
	#Row 2
	if mov[1][0]:
		pressButton("l")
	cv2.rectangle(img, (0,height/3), (width/3,height*2/3), (mov[1][0],0,0), 5)
	if lastButton == "l":
		m = 255
	cv2.putText(img, "L", (width/6, height/2), cv2.FONT_HERSHEY_PLAIN, 3, (255,m,0), 5)
	m = 0
	
	cv2.rectangle(img, (width/3,height/3), (width*2/3,height*2/3), (mov[1][1],0,0), 5)
	cv2.putText(img, "", (width/2, height/2), cv2.FONT_HERSHEY_PLAIN, 3, (255,m,0), 5)
	
	if mov[1][2]:
		pressButton("r")
	cv2.rectangle(img, (width*2/3,height/3), (width,height*2/3), (mov[1][2],0,0), 5)
	if lastButton == "r":
		m = 255
	cv2.putText(img, "R", (width*5/6, height/2), cv2.FONT_HERSHEY_PLAIN, 3, (255,m,0), 5)
	m = 0
	
	#Row 3
	if mov[2][0]:
		pressButton("e")
	cv2.rectangle(img, (0,height*2/3), (width/3,height), (mov[2][0],0,0), 5)
	if lastButton == "e":
		m = 255
	cv2.putText(img, "SEL", (width/6, height*5/6), cv2.FONT_HERSHEY_PLAIN, 3, (255,m,0), 5)
	m = 0
	
	if mov[2][1]:
		pressButton("d")
	cv2.rectangle(img, (width/3,height*2/3), (width*2/3,height), (mov[2][1],0,0), 5)
	if lastButton == "d":
		m = 255
	cv2.putText(img, "D", (width/2, height*5/6), cv2.FONT_HERSHEY_PLAIN, 3, (255,m,0), 5)
	m = 0
	
	if mov[2][2]:
		pressButton("s")
	cv2.rectangle(img, (width*2/3,height*2/3), (width,height), (mov[2][2],0,0), 5)
	if lastButton == "s":
		m = 255
	cv2.putText(img, "ST", (width*5/6, height*5/6), cv2.FONT_HERSHEY_PLAIN, 3, (255,m,0), 5)
	m = 0
	
	pressButton("")
	
	#Update previousPieces
	prevPrevPieces = prevPieces
	prevPieces = pieces
	
	cv2.imshow('e2', img)
	if cv2.waitKey(5) == 27:
		break

cv2.destroyAllWindows()