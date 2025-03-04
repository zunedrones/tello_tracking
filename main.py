from tello_zune import TelloZune
import cv2
from tracking_base import tracking

tello = TelloZune()
tello.start_tello()

while True:
    frame = tello.get_frame()

    tello.calc_fps()
    tracking(tello, frame)

    cv2.imshow("Tello", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

tello.end_tello()
cv2.destroyAllWindows()

