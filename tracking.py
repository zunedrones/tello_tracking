import numpy as np
from detect_yolo import baseDetect

WIDTH = 960
HEIGHT = 720
# center coordinates
CENTERX = WIDTH // 2
CENTERY = HEIGHT // 2
# previous error
prevErrorX = 0
prevErrorY = 0
# proportional coefficient (obtained through testing)
# determines how much the speed should change in response to the current error
KP = 0.2
# derivative coefficient (obtained through testing)
# responsible for controlling the rate of change of the error
KD = 0.2

def tracking(tello, frame) -> None:
    '''
    Function that controls the drone to follow a detected object in the image

    Parameters
        tello: TelloZune object
        frame: image captured by the drone's camera

    Returns
        None
    '''
    global prevErrorX, prevErrorY
    x1, y1, x2, y2, detections = baseDetect(frame)
    speedFB = 0
    # detectWidth = x2 - x1
    cxDetect = (x2 + x1) // 2
    cyDetect = (y2 + y1) // 2

    # PID - Speed Control
    area = (x2 - x1) * (y2 - y1)

    print(f"DETECTIONS: {detections}")
    # if the center of the detection is on the left, the horizontal error will be negative
    # if the object is on the right, the error will be positive
    if (detections > 0):
        errorX = cxDetect - CENTERX
        errorY = CENTERY - cyDetect
        if area < 27000: 
            speedFB = 25
        elif area > 120000:
            speedFB = -25
            print(f"AREA: {area}")
    else:
        errorX = 0
        errorY = 0

    # rotational speed around its own axis is calculated based on the horizontal error
    speedYaw = KP*errorX + KD*(errorX - prevErrorX)
    speedUD = KP*errorY + KD*(errorY - prevErrorY)

    # prevents the speed from exceeding the range -100 / 100
    speedYaw = int(np.clip(speedYaw,-100,100))
    speedUD = int(np.clip(speedUD,-100,100))
    
    print(f"FB: {speedFB}, UD: {speedUD}, YAW: {speedYaw}")
    if(detections != 0):
        tello.send_rc_control(0, speedFB, speedUD, speedYaw)
    else:
        tello.send_rc_control(0, 0, 0, 0)
    # the current error becomes the previous error
    prevErrorX = errorX
    prevErrorY = errorY
