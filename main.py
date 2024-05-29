import cv2
import detect_yolo as dy
import tracking
from tello_zune import TelloZune

def main():
    tello = TelloZune()

    tello.start_tello()

    while True:
        tello.start_video()

        dy.start_detection(tello.frame_detection)

        tracking.start_tracking(tello, dy.values_detect)

        if dy.values_detect:
            frame = dy.values_detect[0]  
            cv2.imshow("Detections", frame)
        else:
            print('Não há detecções')

        if cv2.waitKey(1) == ord('q'):
            break

    tello.end_video()
    tello.end_tello()

if __name__ == "__main__":
    main()
