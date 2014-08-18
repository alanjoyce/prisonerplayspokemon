import cv2
import numpy as np
import os
import time
import datetime
import random
from time import sleep
import thread
import autopy

c = cv2.VideoCapture(1)

prevPrevPieces = []
prevPieces = []
mov = []

buttons = ["u","d","l","r","a","b","s","e"]

lastPress = time.time()
lastButton = "u"
toPress = {}

nightRandom = "u"
nightRandomCount = 0

def systemKeystroke(char):
	autopy.key.toggle(char, True)
	sleep(0.2)
	autopy.key.toggle(char, False)
	#cmd = "osascript -e 'tell application \"System Events\" to keystroke \"" + char + "" + char + "" + char + "\"'"
	#cmd = "osascript -e 'tell application \"System Events\" to key down \"" + char + "\"'"
	#os.system(cmd)
	#cmd = "osascript -e 'tell application \"System Events\" to delay 0.5'"
	#os.system(cmd)
	#cmd = "osascript -e 'tell application \"System Events\" to key up \"" + char + "\"'"
	#os.system(cmd)

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
				maxValue = value
		
		if maxKey == "":
			maxKey = lastButton
		
		try:
			thread.start_new_thread(systemKeystroke, (maxKey, ))
			#systemKeystroke(maxKey)
		except:
			print "Error starting thread"
		
		lastPress = time.time()
		lastButton = maxKey
		toPress = {}
	elif char != "":
		toPress[char] = toPress.get(char, 0) + 1

ix = 0
while True:
	img = c.read()[1]
	height, width, depth = img.shape
	gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
	
	hour = datetime.datetime.now().hour
	minute = datetime.datetime.now().minute
	isNight = False
	if hour > 20 or hour < 6:
		isNight = True
	
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
			
			thresh = 90
			#Use a harsher threshold for the tree
			if i < 2 and j > 0:
				if i == 1 and j == 2:
					thresh = 120
				else:
					thresh = 130
			
			#At night, go nuts with the threshold
			if isNight:
				thresh = 40
			
			result = cv2.threshold(result, thresh, 255, cv2.THRESH_BINARY)[1]
			
			totalDiff = sum(sum(x) for x in result)
			if totalDiff > 500:
				mov[i][j] = 255
			else:
				mov[i][j] = 0
	ix = ix + 1
	if ix > len(pieces) - 1:
		ix = 0
	
	#If it's night, press random buttons
	if isNight:
		#Every so often, pick a new random
		if nightRandomCount > 10:
			nightRandom = random.choice(buttons)
			nightRandomCount = 0
		else:
			nightRandomCount = nightRandomCount + 1
		toPress[nightRandom] = 3
		cv2.putText(img, "NIGHT MODE: WEIGHTED RANDOM", (width*59/100,height/16), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,255), 3)
	
	#Label the hour, per request
	cv2.putText(img, str(hour) + ":" + str(minute), (width*9/12,height*37/38), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,255), 3)
	
	m = 0
	#Row 1
	if mov[0][0]:
		pressButton("")
	cv2.rectangle(img, (0,0), (width/3,height/3), (mov[0][0],0,0), 5)
	if lastButton == "":
		m = 255
	cv2.putText(img, "", (width/6, height/6), cv2.FONT_HERSHEY_PLAIN, 3, (255,m,0), 5)
	m = 0
	
	if mov[0][1]:
		pressButton("l")
	cv2.rectangle(img, (width/3,0), (width*2/3,height/3), (mov[0][1],0,0), 5)
	if lastButton == "l":
		m = 255
	cv2.putText(img, "L", (width/2, height/6), cv2.FONT_HERSHEY_PLAIN, 3, (255,m,0), 5)
	m = 0
	
	if mov[0][2]:
		pressButton("u")
	cv2.rectangle(img, (width*2/3,0), (width,height/3), (mov[0][2],0,0), 5)
	if lastButton == "u":
		m = 255
	cv2.putText(img, "U", (width*5/6, height/6), cv2.FONT_HERSHEY_PLAIN, 3, (255,m,0), 5)
	m = 0
	
	#Row 2
	if mov[1][0]:
		pressButton("e")
	cv2.rectangle(img, (0,height/3), (width/3,height*2/3), (mov[1][0],0,0), 5)
	if lastButton == "e":
		m = 255
	cv2.putText(img, "SEL", (width/6, height*7/12), cv2.FONT_HERSHEY_PLAIN, 3, (255,m,0), 5)
	m = 0
	
	if mov[1][1]:
		pressButton("d")
	cv2.rectangle(img, (width/3,height/3), (width*2/3,height*2/3), (mov[1][1],0,0), 5)
	if lastButton == "d":
		m = 255
	cv2.putText(img, "D", (width/2, height/2), cv2.FONT_HERSHEY_PLAIN, 3, (255,m,0), 5)
	m = 0
	
	if mov[1][2]:
		pressButton("s")
	cv2.rectangle(img, (width*2/3,height/3), (width,height*2/3), (mov[1][2],0,0), 5)
	if lastButton == "s":
		m = 255
	cv2.putText(img, "ST", (width*5/6, height/2), cv2.FONT_HERSHEY_PLAIN, 3, (255,m,0), 5)
	m = 0
	
	#Row 3
	if mov[2][0]:
		pressButton("a")
	cv2.rectangle(img, (0,height*2/3), (width/3,height), (mov[2][0],0,0), 5)
	if lastButton == "a":
		m = 255
	cv2.putText(img, "A", (width/6, height*5/6), cv2.FONT_HERSHEY_PLAIN, 3, (255,m,0), 5)
	m = 0
	
	if mov[2][1]:
		pressButton("b")
	cv2.rectangle(img, (width/3,height*2/3), (width*2/3,height), (mov[2][1],0,0), 5)
	if lastButton == "b":
		m = 255
	cv2.putText(img, "B", (width/2, height*5/6), cv2.FONT_HERSHEY_PLAIN, 3, (255,m,0), 5)
	m = 0
	
	if mov[2][2]:
		pressButton("r")
	cv2.rectangle(img, (width*2/3,height*2/3), (width,height), (mov[2][2],0,0), 5)
	if lastButton == "r":
		m = 255
	cv2.putText(img, "R", (width*5/6, height*5/6), cv2.FONT_HERSHEY_PLAIN, 3, (255,m,0), 5)
	m = 0
	
	pressButton("")
	
	#Update previousPieces
	prevPrevPieces = prevPieces
	prevPieces = pieces
	
	cv2.imshow('e2', img)
	if cv2.waitKey(5) == 27:
		break

cv2.destroyAllWindows()