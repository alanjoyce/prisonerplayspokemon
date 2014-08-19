import cv2
import numpy as np
import os
import time
import datetime
import random
import thread
import autopy

c = cv2.VideoCapture(1)

prevPrevPieces = []
prevPieces = []
mov = []

buttonCoords = {(0,0):"e", (0,1):"u", (0,2):"d", (1,0):"l", (1,1):"r", (1,2):"a", (2,0):"b", (2,1):"s", (2,2):"n"}
buttons = buttonCoords.values()
buttonLabels = {"u":"U", "d":"D", "l":"L", "r":"R", "a":"A", "b":"B", "s":"START", "e":"SEL", "n":"RAND"}

lastPress = time.time()
lastButton = "u"
toPress = {}

lastRandomize = lastPress

def randomizeCoords():
	global buttonCoords
	
	keys = buttonCoords.keys()
	values = buttonCoords.values()
	
	random.shuffle(keys)
	random.shuffle(values)
	
	for i in range(len(keys)):
		buttonCoords[keys[i]] = values[i]

def systemKeystroke(char):
	autopy.key.toggle(char, True)
	time.sleep(0.2)
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
		
		#If the pressed button is random, shuffle the buttons
		if maxKey == "n":
			randomizeCoords()
			lastButton = ""
		
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
	
	timeNow = datetime.datetime.now()
	isNight = False
	if timeNow.hour >= 20 or timeNow.hour < 6:
		isNight = True
	
	#Define the sections
	sections = [[0,0,0],[0,0,0],[0,0,0]]

	sections[0][0] = (0, 0, 15, 50)
	sections[0][1] = (15, 0, 30, 50)
	sections[0][2] = (30, 0, 100, 33)

	sections[1][0] = (30, 33, 55, 60)
	sections[1][1] = (55, 33, 75, 60)
	sections[1][2] = (75, 33, 100, 70)
	
	sections[2][0] = (30, 60, 55, 100)
	sections[2][1] = (55, 60, 75, 100)
	sections[2][2] = (75, 70, 100, 100)
	
	#Get pieces of image for each section
	pieces = [[0,0,0],[0,0,0],[0,0,0]]
	for i in range(len(sections)):
		for j in range(len(sections[i])):
			#Convert section coordinates from percentage to pixels
			x1, y1, x2, y2 = sections[i][j]
			sections[i][j] = (width*x1/100, height*y1/100, width*x2/100, height*y2/100)
			
			#Create the image piece based on the section
			x1, y1, x2, y2 = sections[i][j]
			pieces[i][j] = gray[y1:y2, x1:x2]
	
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
			
			#Define motion threshold and total section difference requirement
			thresh = 110
			diffReq = 1000
			
			#At night, go nuts with the threshold and diffReq
			if isNight:
				thresh = 40
				diffReq = 400
			
			result = cv2.threshold(result, thresh, 255, cv2.THRESH_BINARY)[1]
			
			totalDiff = sum(sum(x) for x in result)
			if totalDiff > 1000:
				mov[i][j] = 255
			else:
				mov[i][j] = 0
	ix = ix + 1
	if ix > len(pieces) - 1:
		ix = 0
	
	#Draw each square
	for i in range(len(sections)):
		for j in range(len(sections[i])):
			thisButton = buttonCoords[(i,j)]
			if mov[i][j]:
				pressButton(thisButton)
			x1, y1, x2, y2 = sections[i][j]
			cv2.rectangle(img, (x1, y1), (x2-2, y2-2), (mov[i][j],0,0), 3)
			m = 0
			if lastButton == thisButton:
				m = 255
			cv2.putText(img, buttonLabels[thisButton], (x1+20, y2-25), cv2.FONT_HERSHEY_PLAIN, 3, (255,m,0), 5)
	
	#Label the hour, per request
	cv2.putText(img, str(timeNow.month) + "/" + str(timeNow.day) + " " + str(timeNow.hour) + ":" + str(timeNow.minute), (width*59/100,height*5/100), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,255), 3)
	
	#Explain night mode
	if isNight:
		cv2.putText(img, "NIGHT MODE: LOW THRESHOLD", (width*59/100,height*10/100), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,255), 3)
	
	pressButton("")
	
	#Randomize every 60 minutes during the day and every 10 minutes at night.
	randInterval = 60*60
	if isNight:
		randInterval = 60*10
	
	#Randomize every hour
	if time.time() > lastRandomize + randInterval:
		randomizeCoords()
		lastRandomize = time.time()
	
	#Update previousPieces
	prevPrevPieces = prevPieces
	prevPieces = pieces
	
	cv2.imshow('e2', img)
	if cv2.waitKey(5) == 27:
		break

cv2.destroyAllWindows()