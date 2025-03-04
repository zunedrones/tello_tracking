from ultralytics import YOLO
import cv2

FONT = cv2.FONT_HERSHEY_SIMPLEX
FONTSCALE = 1
COLOR = (255, 0, 0)
THICKNESS = 2

# Load model
model = YOLO("tello_4.pt")
classNames = ["movel", "takeoff"]

count = 0
x1, y1, x2, y2 = 0, 0, 0, 0
cls = 0
number_detect = 0

def object_detect(frame):
    """
    Detects objects in the given frame using a YOLO model.

    Parameters
    ----------
    frame : numpy.ndarray
        The image frame in which objects will be detected.

    Returns
    -------
    list
        A list containing:
        - x1 (int): Top-left x-coordinate of the bounding box.
        - y1 (int): Top-left y-coordinate of the bounding box.
        - x2 (int): Bottom-right x-coordinate of the bounding box.
        - y2 (int): Bottom-right y-coordinate of the bounding box.
        - number_detect (int): The number of detected objects.
    """

    global count, x1, y1, x2, y2, cls, number_detect
    
    if count == 10:
        count = 0
    
        results = model(frame, conf=0.87, max_det=1, stream_buffer=True)
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

    return [x1, y1, x2, y2, number_detect]
