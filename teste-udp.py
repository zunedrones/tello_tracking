import socket
from ultralytics import YOLO
import cv2
import math


capture = cv2.VideoCapture ('udp:/0.0.0.0:11111',cv2.CAP_FFMPEG)
model = YOLO("tello_2.pt")
classNames = ["movel", "takeoff"]
tello_ip = '192.168.10.1'
tello_port = 8889
tello_address = (tello_ip, tello_port)
mypc_address = ('192.168.10.2', 3772)
socket = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
socket.bind (mypc_address)
socket.sendto ('command'.encode (' utf-8 '), tello_address)
socket.sendto ('streamon'.encode (' utf-8 '), tello_address)
print ("Start streaming")
capture = cv2.VideoCapture('udp://0.0.0.0:11111',cv2.CAP_FFMPEG)
if not capture.isOpened():
  	capture.open('udp://0.0.0.0:11111')

while True:
    ret, frame = capture.read()
    results = model(frame, stream=True, conf=0.7)
    #
    if(ret):
        cv2.imshow('frame', frame)
    if cv2.waitKey (1)&0xFF == ord ('q'):
        break
capture.release ()
cv2.destroyAllWindows ()
socket.sendto ('streamoff'.encode (' utf-8 '), tello_address)
"""
    results = model(frame, stream=True, conf=0.7)

    # coordinates
    for r in results:
        boxes = r.boxes

        for box in boxes:
            # bounding box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values

            # put box in cam
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

            # confidence
            confidence = math.ceil((box.conf[0]*100))/100
            print("Confidence --->",confidence)

            # class name
            cls = int(box.cls[0])
            print("Class name -->", classNames[cls])

            # object details
            org = [x1, y1]
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 1
            color = (255, 0, 0)
            thickness = 2

            cv2.putText(frame, classNames[cls], org, font, fontScale, color, thickness)"""
