from tello_zune import TelloZune
import cv2
import detect_yolo as dy
import tracking
#cv2.namedWindow('webcam')
tello = TelloZune()
tello.start_tello()

while True:
    tello.start_video()
    dy.start_detection(tello.frame_detection)
    tracking.start_tracking(tello, dy.values_detect)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
tello.end_video()
tello.end_tello()

