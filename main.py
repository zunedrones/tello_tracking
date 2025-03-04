from djitellopy import Tello
import cv2
from detect_yolo import object_detect

tello = Tello()
tello.connect()
print(f"Battery: {tello.get_battery()}")
tello.streamon()

while True:
    frame = tello.get_frame_read().frame

    object_detect(frame)

    cv2.imshow("Tello", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

