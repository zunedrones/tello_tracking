from tello_zune import TelloZune
import cv2
import detect_yolo as dy
import tracking

tello = TelloZune()

tello.start_tello()

while True:
    # Start video stream
    tello.start_video()

    # Detect objects with YOLO
    dy.start_detection(tello.frame_detection)

    # Track detected objects
    tracking.start_tracking(tello, dy.values_detect)

    # Display the frame with bounding boxes
    if dy.values_detect:
        frame = dy.values_detect[0]  # Assuming the first element in values_detect is the frame
        cv2.imshow("Detections", frame)
        print('frame adquirido, mostrar imagem')
        print('imshow bem sucedido')
    else:
        print('Não há detecções')

    # Exit loop on 'q' press
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

# Stop video stream and disconnect drone
tello.end_video()
tello.end_tello()