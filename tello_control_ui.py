from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Toplevel, Scale
import threading
import datetime
import cv2
import os
import time
import platform

class TelloUI:
    """Wrapper class to enable the GUI."""

    def __init__(self, tello, output_path):
        """
        Initialize all the elements of the GUI, supported by Tkinter.

        :param tello: Class that interacts with the Tello drone.
        """
        self.tello = tello  # Video stream device
        self.output_path = output_path  # Path to save pictures created by clicking the takeSnapshot button
        self.frame = None  # Frame read from h264decoder and used for pose recognition
        self.thread = None  # Thread of the Tkinter main loop
        self.stop_event = None  

        # If the flag is TRUE, the auto-takeoff thread will stop waiting for the response from Tello
        self.quit_waiting_flag = False
        
        # Initialize the root window and image panel
        self.root = tk.Tk()
        self.panel = None

        # Create buttons
        self.btn_snapshot = tk.Button(self.root, text="Snapshot!", command=self.take_snapshot)
        self.btn_snapshot.pack(side="bottom", fill="both", expand="yes", padx=10, pady=5)

        self.btn_pause = tk.Button(self.root, text="Pause", relief="raised", command=self.pause_video)
        self.btn_pause.pack(side="bottom", fill="both", expand="yes", padx=10, pady=5)

        self.btn_landing = tk.Button(self.root, text="Open Command Panel", relief="raised", command=self.open_cmd_window)
        self.btn_landing.pack(side="bottom", fill="both", expand="yes", padx=10, pady=5)
        
        # Start a thread that constantly polls the video sensor for the most recently read frame
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.video_loop, args=())
        self.thread.start()

        # Set a callback to handle when the window is closed
        self.root.wm_title("TELLO Controller")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.on_close)

        # The sending_command will send a command to Tello every 5 seconds
        self.sending_command_thread = threading.Thread(target=self._sending_command)

    def video_loop(self):
        """
        The main loop thread of Tkinter.
        """
        try:
            # Start the thread that gets the GUI image and draws skeleton
            time.sleep(0.5)
            self.sending_command_thread.start()
            while not self.stop_event.is_set():
                system = platform.system()

                # Read the frame for GUI show
                self.frame = self.tello.read()
                if self.frame is None or self.frame.size == 0:
                    continue 

                # Transfer the format from frame to image
                image = Image.fromarray(self.frame)

                self._update_gui_image(image)

        except RuntimeError as e:
            print("[INFO] caught a RuntimeError")

    def _update_gui_image(self, image):
        """
        Main operation to initialize the image object and update the GUI panel.
        """
        image = ImageTk.PhotoImage(image)  
        # If the panel is None, we need to initialize it
        if self.panel is None:
            self.panel = tk.Label(image=image)
            self.panel.image = image
            self.panel.pack(side="left", padx=10, pady=10)
        # Otherwise, simply update the panel
        else:
            self.panel.configure(image=image)
            self.panel.image = image

    def _sending_command(self):
        """
        Start a while loop that sends 'command' to Tello every 5 seconds.
        """
        while True:
            self.tello.send_command('command')
            time.sleep(5)

    def _set_quit_waiting_flag(self):
        """
        Set the variable as TRUE, which will stop the computer from waiting for a response from Tello.
        """
        self.quit_waiting_flag = True

    def take_snapshot(self):
        """
        Save the current frame of the video as a jpg file and put it into the output path.
        """
        # Grab the current timestamp and use it to construct the filename
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))

        p = os.path.sep.join((self.output_path, filename))

        # Save the file
        cv2.imwrite(p, cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR))
        print(f"[INFO] saved {filename}")

    def pause_video(self):
        """
        Toggle the freeze/unfreeze of the video.
        """
        if self.btn_pause.config('relief')[-1] == 'sunken':
            self.btn_pause.config(relief="raised")
            self.tello.video_freeze(False)
        else:
            self.btn_pause.config(relief="sunken")
            self.tello.video_freeze(True)

    def on_close(self):
        """
        Set the stop event, clean up the camera, and allow the rest of the quit process to continue.
        """
        print("[INFO] closing...")
        self.stop_event.set()
        del self.tello
        self.root.quit()

