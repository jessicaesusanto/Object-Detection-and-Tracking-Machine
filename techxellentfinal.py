#!/usr/bin/python
'''
	Author: Techxellent5 - techxellent5@gmail.com
	A Simple mjpg stream http server
'''
from PIL import Image
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import socket
import socketserver
from io import BytesIO
from threading import Thread
import numpy as np
import imutils
import math
import cv2

# client and server ports and IP addresses
JAVA_SERVER_HOST = "10.54.77.2"
JAVA_SERVER_PORT = 4445
PYTHON_SERVER_PORT = 4446
PYTHON_SERVER_HOST = "10.54.77.85"
vs = None
globalX = 0
globalAngle = 0
globalRadius = 0
globalX2 = 0
globalY2 = 0
string =""


# lower and upper boundaries of object colours in HSV  
orangeLower =(0, 87, 131)
orangeUpper =(26,255,255)
# global x1 
x1 = 340
# global y1
y1 = 240
globalX1 = x1
globalY1 = y1
#known distance of object from camera
KNOWN_DISTANCE = 17.5
def distance_to_camera(knownWidth, focalLength, perWidth):
	# compute and return the distance from the image to the camera
	return (knownWidth * focalLength) / perWidth
def find_marker(image):
	# convert the image to grayscale, blur it, and detect edges
	blurred = cv2.GaussianBlur(image, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    #find the objects with in given HSV range, erode and dilate to remove disturbances
	mask = cv2.inRange(hsv, orangeLower, orangeUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
    #find and grab contours
	cnts = cv2.findContours(mask.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	if(len(cnts)==0):
		return 0
	c = max(cnts, key = cv2.contourArea)
	# compute the bounding box of object and return it
	return cv2.minAreaRect(c)
def angle_from_center(M, x1, y1):
    global x2, y2
	# compute and return the angle of the object from camera 
    try:
        x2 = int(M["m10"] / M["m00"])
        y2 = int(M["m01"] / M["m00"])
        angle = int(math.atan((y2-y1)/(x2-x1))*180/math.pi)
    except ZeroDivisionError:
        return 0
    else:
        return angle

#the width of the object  in inches
KNOWN_WIDTH = 13
image = cv2.imread("/home/nvidia/Desktop/17_5.jpg")
marker = find_marker(image)
#finding the focal length of camera
focalLength = (marker[1][0] * KNOWN_DISTANCE) / KNOWN_WIDTH

def calculate():
    global globalX, globalAngle, frame, globalX2, globalY2, globalRadius, frame2
    while True:
        rc, frame = vs.read() 
        # handle the frame from VideoCapture or VideoStream
        marker = find_marker(frame)       
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)            
        # construct a mask for the color "orange", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, orangeLower, orangeUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

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
            # globalX1 = x
            # globalY1 = y
            globalRadius = radius
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        
            inches = distance_to_camera(KNOWN_WIDTH, focalLength, marker[1][0])
            dist = round(inches,2)
            globalX = dist
            # print(dist)
            # x2 = int(M["m10"] / M["m00"])
            # globalX2 = x2
            # y2 = int(M["m01"] / M["m00"])
            # globalY2 = y2
            angle = angle_from_center(M, globalX1, globalY1)
            globalAngle = angle
            sendMessage(str(globalX)+" CM " + str(globalAngle) +" degree ") 
            cv2.line(frame, (globalX1,globalY1), (int(x),int(y)), (0, 0, 255), thickness=2, lineType=8)
            # print(angle)
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, str(angle), ((int((int(globalX1) +int(x2))/2)),(int((int(globalY1) +int(y2))/2))),font, 1.0, (0, 255, 0),2)
            cv2.putText(frame, str(dist), (int(globalX1),int(globalY1)),font, 1.0, (0, 255, 0),2)

            if radius > 10:
                # draw the circle and its  center in the frame
                cv2.circle(frame, (int(x), int(y)), int(radius),
                    (0, 255, 255), 2)
        frame2 =frame
        setResolution(string)
            
class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header(
                'Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            while True:
                frame3 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
                jpg = Image.fromarray(frame3)
                tmpFile = BytesIO()
                jpg.save(tmpFile, 'JPEG')
                self.wfile.write("--jpgboundary".encode())
                self.send_header('Content-type', 'image/jpeg')
                self.send_header('Content-length',
                                 str(tmpFile.getbuffer().nbytes))
                self.end_headers()
                jpg.save(self.wfile, 'JPEG')
            return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
#received data from server 
def onData(data):
        global string
        string = data.decode("utf-8")
        print(string)
        
# to set resolution upon request from client 
def setResolution(string):
    global globalX1, globalY1
    if (string == "a"):
        if (vs.get(cv2.CAP_PROP_FRAME_WIDTH) == 680):
            return
        else:
            vs.set(cv2.CAP_PROP_FRAME_WIDTH, 680)
            vs.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            globalX1 = 340
            globalY1 = 240
            print("High resolution")
    elif (string == "b"):
        if (vs.get(cv2.CAP_PROP_FRAME_WIDTH) == 340):
            return
        else:
            vs.set(cv2.CAP_PROP_FRAME_WIDTH, 340)
            vs.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            globalX1 = 170
            globalY1 = 120
            print("Low resolution")
    elif (string == "c"):
        if (vs.get(cv2.CAP_PROP_FPS) == 30):
            return
        else:
            vs.set(cv2.CAP_PROP_FPS, 30)
    elif (string == "d"):
        if (vs.get(cv2.CAP_PROP_FPS) == 15):
            return
        else:
            vs.set(cv2.CAP_PROP_FPS, 15)
		
	# to send data to client	
def sendMessage(message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((JAVA_SERVER_HOST, JAVA_SERVER_PORT))
        try:
            sock.sendall(message.encode('utf-8'))
        finally:
            sock.close()

class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]                              
        onData(data)

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


def main():
    global vs, string
    vs = cv2.VideoCapture(0)
    #setResolution(string)
    threadCalculate = Thread(target=calculate)
    httpserver = Thread(target=ThreadedHTTPServer((PYTHON_SERVER_HOST, 8087), CamHandler).serve_forever)
    udpserver = Thread(target=ThreadedUDPServer((PYTHON_SERVER_HOST, PYTHON_SERVER_PORT), ThreadedUDPRequestHandler).serve_forever)

    httpserver.start()
    udpserver.start()
    threadCalculate.start()
    threadCalculate.join()
    httpserver.join()
    udpserver.join()

if __name__ == '__main__':
    main()
