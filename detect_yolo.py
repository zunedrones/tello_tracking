from ultralytics import YOLO
import cv2

FONT = cv2.FONT_HERSHEY_SIMPLEX
FONTSCALE = 1
COLOR = (255, 0, 0)
THICKNESS = 4

model = YOLO("tello_2.pt")
classNames = ["movel", "takeoff"]
#cv2.namedWindow('webcam')
count = 0
x1, y1, x2, y2 = 0, 0, 0, 0
cls = 0
number_detect = 0
values_detect = [0, 0, 0, 0, 0, 0]

def start_detection(frame):
    '''
    Faz a deteccao de um modelo pre-treinado do yolov8.
    Recebe como argumento o frame atual do video.
    '''
    global count, x1, y1, x2, y2, cls, number_detect, values_detect
    
    if count == 7:
        count = 0
    
        results = model(frame, conf=0.75, max_det=1)
        for r in results:
            boxes = r.boxes
            if len(boxes) >= 1:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) 
                    cls = int(box.cls[0])
                    number_detect = len(boxes)
                    org = [x1, y1]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)
                    cv2.putText(frame, classNames[cls], org, FONT, FONTSCALE, COLOR, THICKNESS)
                    cv2.circle(frame, ((x2 + x1) // 2, (y2 + y1) // 2), 5, (0, 255, 0), cv2.FILLED)
            else:
                x1, y1, x2, y2 = 0, 0, 0, 0
                number_detect = 0

    
    count += 1
    print(f"X1: {x1}, Y1: {y1}, X2: {x2}, Y2: {y2} Number: {number_detect}")

    if number_detect >= 1:
        values_detect = [frame, x1, y1, x2, y2, number_detect]
    else:
        values_detect = [frame, 0, 0, 0, 0, number_detect]