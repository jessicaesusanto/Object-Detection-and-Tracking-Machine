#!/usr/bin/python
'''
	Author: Igor Maculan - n3wtron@gmail.com
	A Simple mjpg stream http server
'''
import cv2
from PIL import Image
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import socket
import socketserver
from io import StringIO, BytesIO
import time
from threading import Thread
capture = None

JAVA_SERVER_HOST = "10.50.6.83"
JAVA_SERVER_PORT = 4445
PYTHON_SERVER_PORT = 4446


class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header(
                'Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            counter = 0
            while True:
                rc, img = capture.read()
                imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                jpg = Image.fromarray(imgRGB)
                tmpFile = BytesIO()
                jpg.save(tmpFile, 'JPEG')
                self.wfile.write("--jpgboundary".encode())
                self.send_header('Content-type', 'image/jpeg')
                self.send_header('Content-length',
                                 str(tmpFile.getbuffer().nbytes))
                self.end_headers()
                jpg.save(self.wfile, 'JPEG')
                counter = counter + 1
                print("This is frame" + str(counter))
            return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def onData(data):
        print("Python got data: " + data.decode("utf-8"))
		
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
    global capture
    capture = cv2.VideoCapture(0)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 500)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)
    servers = [ThreadedHTTPServer(('10.50.7.20', 8087), CamHandler), ThreadedUDPServer(("10.50.7.20", PYTHON_SERVER_PORT), ThreadedUDPRequestHandler)]
    for s in servers:
        Thread(target=s.serve_forever).start()
    count = 0
    while True:
        sendMessage("Hello" + str(count))
        count = count + 1

if __name__ == '__main__':
    main()
