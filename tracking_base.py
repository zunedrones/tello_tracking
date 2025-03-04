import numpy as np
from detect_yolo import object_detect

# Frame dimensions
WIDTH = 544
HEIGHT = 306
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2

# PD Controller coefficients (tuned experimentally)
KP = 0.2
KD = 0.2

# Previous errors
prev_error_x = 0
prev_error_y = 0

def tracking(tello, frame):
    """
    Tracks the detected object and keeps it centered on the screen.

    Parameters
    ----------
    tello : object
        Tello drone object that provides control methods.
    frame : numpy.ndarray
        Current video frame.

    The function adjusts the drone's movement based on the detected object's position 
    using a PD controller.
    """
    global prev_error_x, prev_error_y

    # Object detection
    x1, y1, x2, y2, detections = object_detect(frame)

    # Default values (if no detection)
    speed_fb, speed_ud, speed_yaw = 0, 0, 0

    if detections > 0:
        # Calculate object center and bounding box area
        cx_detect = (x1 + x2) // 2
        cy_detect = (y1 + y2) // 2
        area = (x2 - x1) * (y2 - y1)

        # Compute error values
        error_x = cx_detect - CENTER_X
        error_y = CENTER_Y - cy_detect

        # Forward/backward speed based on object area
        if area < 27000:
            speed_fb = 25
        elif area > 120000:
            speed_fb = -25

        # PD control for yaw and up/down movement
        speed_yaw = np.clip(KP * error_x + KD * (error_x - prev_error_x), -100, 100)
        speed_ud = np.clip(KP * error_y + KD * (error_y - prev_error_y), -100, 100)

        # Update previous errors
        prev_error_x, prev_error_y = error_x, error_y

    # Send control command only if necessary
    if (speed_fb, speed_ud, speed_yaw) != (0, 0, 0) or detections > 0:
        tello.send_rc_control(0, int(speed_fb), int(speed_ud), int(speed_yaw))

    # Print status
    print(f"Detections: {detections} | Area: {area if detections else 'N/A'}")
    print(f"FB: {speed_fb}, UD: {speed_ud}, YAW: {speed_yaw}")
