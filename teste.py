import cv2
import time

foto = cv2.imread("foto.jpg")

cap = cv2.VideoCapture(0)
# cv2.imshow("foto", foto)

while True:
    time.sleep(3)
    ret, frame = cap.read()
    cv2.imshow("foto", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.waitKey(0)
cv2.destroyAllWindows()