from ultralytics import YOLO
import cv2

FONT = cv2.FONT_HERSHEY_SIMPLEX
FONTSCALE = 1
COLOR = (255, 0, 0)
THICKNESS = 2

model = YOLO("tello_4.pt")
classNames = ["movel", "takeoff"]
count = 0
x1, y1, x2, y2 = 0, 0, 0, 0
cls = 0
number_detect = 0

def baseDetect(frame):
    '''
    Faz a deteccao da base e takeoff, utilzando modelo pre-treinado do yolov8n.
    Recebe como argumento o frame atual do video.
    '''
    global count, x1, y1, x2, y2, cls, number_detect
    
    if count == 7:
        count = 0
    
        results = model(frame, conf=0.75, max_det=1, stream_buffer=True)
        for r in results:
            boxes = r.boxes
            if len(boxes) >= 1:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) 
                    cls = int(box.cls[0])
                    number_detect = len(boxes)
            else:
                x1, y1, x2, y2 = 0, 0, 0, 0
                number_detect = 0

    org = [x1, y1]
    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)
    cv2.putText(frame, classNames[cls], org, FONT, FONTSCALE, COLOR, THICKNESS)
    cv2.circle(frame, ((x2 + x1) // 2, (y2 + y1) // 2), 5, (0, 255, 0), cv2.FILLED)
    count += 1

    if number_detect >= 1:
        return [frame, x1, y1, x2, y2, number_detect]
    else:
        return [frame, 0, 0, 0, 0, number_detect]
