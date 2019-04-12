from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import math

x1 = 340
y1 = 240
def distance_to_camera(knownWidth, focalLength, perWidth):
	# compute and return the distance from the image to the camera
	return (knownWidth * focalLength) / perWidth
def find_marker(image):
	# convert the image to grayscale, blur it, and detect edges
	#frame = imutils.resize(image, width=600)
	blurred = cv2.GaussianBlur(image, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
	# mask = cv2.inRange(hsv, greenLower, greenUpper)
	mask = cv2.inRange(hsv, redLower, redUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
	cnts = cv2.findContours(mask.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	if (len(cnts)==0):
	    return 0 
	c = max(cnts, key = cv2.contourArea)

	# compute the bounding box of the of the paper region and return it
	return cv2.minAreaRect(c)
def angle_from_center(M, x1, y1):
	# compute and return the distance from the image to the camera
	try:
		x2 = int(M["m10"] / M["m00"])
		y2 = int(M["m01"] / M["m00"])
		angle = int(math.atan((y2-y1)/(x2-x1))*180/math.pi)
	except ZeroDivisionError:
		 return 0
	else:
		return angle 

		
	
#KNOWN_DISTANCE = 30
focalLength = 820


#the width of the object  in cm
KNOWN_WIDTH = 1

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())
# greenLower = (29, 86, 6)
# greenUpper = (64, 255, 255)
redLower =(0, 87, 131)
redUpper =(26,255,255)
pts = deque(maxlen=args["buffer"])
 
# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
	vs = VideoStream(src=0).start()
 
# otherwise, grab a reference to the video file
else:
	vs = cv2.VideoCapture(args["video"])
 
# allow the camera or video file to warm up
time.sleep(2.0)
# keep looping
while True:
	# grab the current frame
	frame = vs.read()
 
	# handle the frame from VideoCapture or VideoStream
	frame = frame[1] if args.get("video", False) else frame
	marker = find_marker(frame)
 
	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
	if frame is None:
		break
 
	# resize the frame, blur it, and convert it to the HSV
	# color space
	#frame = imutils.resize(frame, width=600)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
	
 
	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, redLower, redUpper)
	#mask2 = cv2.inRange(hsv,(165,145,100),(250,210,160))
	# mask3 = cv2.inRange(hsv,(105,180,40),(120,260,100))
	#mask4 = cv2.Add(mask2,mask3)  
	#mask = cv2.inRange(hsv, redLower, redUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
		# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	center = None
	# only proceed if at least one contour was found
	if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		inches = distance_to_camera(KNOWN_WIDTH, focalLength, marker[1][0])
		print(center)
		x2 = int(M["m10"] / M["m00"])
		y2 = int(M["m01"] / M["m00"])
		angle = angle_from_center(M, x1, y1)
		#cv2.line(mask,(x1,y1),(x2,y2),(0,255,0),4,cv2.LINE_AA)
		cv2.line(frame, (x1,y1), (x2,y2), (0, 0, 255), thickness=2, lineType=8)
		print(angle)
		font = cv2.FONT_HERSHEY_SIMPLEX
		cv2.putText(frame, str(inches), (int(x1),int(y1)),font, 1.0, (0, 255, 0),2)
		cv2.putText(frame, str(angle), ((int((int(x1) +int(x2))/2)),(int((int(y1) +int(y2))/2))),font, 1.0, (0, 0, 255),2)
		#print(M["m00"])
		# for z mask
		# 	area = cv2.contourArea(z)
		# 	#print(area)
		# 	focalLength = (area * KNOWN_DISTANCE) / KNOWN_WIDTH
		# 	CM = distance_to_camera(KNOWN_WIDTH, focalLength, area)
		# 	print(CM)
		# only proceed if the radius meets a minimum siarearea
		if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			#cv2.circle(frame, center, 5, (0, 0, 255), -1)
 
	# update the points queue
	# pts.appendleft(center)
	# # loop over the set of tracked points
	# for i in range(1, len(pts)):
	# 	# if either of the tracked points are None, ignore
	# 	# them
	# 	if pts[i - 1] is None or pts[i] is None:
	# 		continue
 
	# 	# otherwise, compute the thickness of the line and
	# 	# draw the connecting lines
	# 	thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
	# 	cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
 
	# show the frame to our screen
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
 
	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break
 
# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
	vs.stop()
 
# otherwise, release the camera
else:
	vs.release()
 
# close all windows
cv2.destroyAllWindows()
