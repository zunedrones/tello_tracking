from tello_zune import TelloZune
import cv2
import detect_yolo as dy
import tracking

tello = TelloZune()
tello.start_tello()

while True:
    tello.start_video()
    dy.start_detection(tello.frame_detection)
    tracking.start_tracking(tello, dy.values_detect)
    
    # Mostrar o frame com as bounding boxes
    cv2.imshow("Detections", dy.values_detect[0])
    
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
tello.end_video()
tello.end_tello()
