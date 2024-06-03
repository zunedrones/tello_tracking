import cv2
import time
import socket
import threading
import numpy as np
import h264decoder

FONT = cv2.FONT_HERSHEY_SIMPLEX
COLOR = (0, 255, 0)
ORG = (30, 30)
FONTSCALE = 1
THICKNESS = 2
WIDTH = 544
HEIGHT = 306

class BatteryError(Exception):
    pass

def battery_error(tello_battery: int): # verificar
    #tello_battery = int(tello_battery)
    if tello_battery <= 20:
        raise BatteryError("Bateria menor que 20%, operação cancelada.")

class TelloZune():

    def __init__(self, local_ip='', local_port=8889, imperial=False, command_timeout=.3, tello_ip='192.168.10.1',
                 tello_port=8889):
        """
        Binds to the local IP/port and puts the Tello into command mode.

        :param local_ip (str): Local IP address to bind.
        :param local_port (int): Local port to bind.
        :param imperial (bool): If True, speed is MPH and distance is feet.
                             If False, speed is KPH and distance is meters.
        :param command_timeout (int|float): Number of seconds to wait for a response to a command.
        :param tello_ip (str): Tello IP.
        :param tello_port (int): Tello port.
        """
        self.num_frames = 0
        self.start_time = time.time()
        self.fps = 0
        self.last_rc_control_timestamp = time.time()  # Inicializa o timestamp do controle remoto
        self.TIME_BTW_RC_CONTROL_COMMANDS = 0.001  # in seconds
        self.abort_flag = False
        self.decoder = h264decoder.H264Decoder()
        self.command_timeout = command_timeout
        self.imperial = imperial
        self.response = None  
        self.frame = None  # numpy array BGR -- current camera output frame
        self.is_freeze = False  # freeze current camera output
        self.last_frame = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
        self.socket_video = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for receiving video stream
        self.tello_address = (tello_ip, tello_port)
        self.local_video_port = 11111  # port for receiving video stream
        self.last_height = 0
        self.socket.bind((local_ip, local_port))

        # thread for receiving cmd ack
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        # to receive video -- send cmd: command, streamon
        self.socket.sendto(b'command', self.tello_address)
        print('sent: command')
        self.socket.sendto(b'streamon', self.tello_address)
        print('sent: streamon')

        self.socket_video.bind((local_ip, self.local_video_port))

        # thread for receiving video
        self.receive_video_thread = threading.Thread(target=self._receive_video_thread)
        self.receive_video_thread.daemon = True
        self.receive_video_thread.start()

    def __del__(self):
        if hasattr(self, 'socket'):
            self.socket.close()
        if hasattr(self, 'socket_video'):
            self.socket_video.close()
    
    def read(self):
        """Return the last frame from camera."""
        if self.is_freeze:
            return self.last_frame
        else:
            return self.frame

    def video_freeze(self, is_freeze=True):
        """Pause video output -- set is_freeze to True"""
        self.is_freeze = is_freeze
        if is_freeze:
            self.last_frame = self.frame

    def _receive_thread(self):
        """Listen to responses from the Tello.

        Runs as a thread, sets self.response to whatever the Tello last returned.

        """
        while True:
            try:
                self.response, ip = self.socket.recvfrom(3000)
                # print(self.response)
            except socket.error as exc:
                print("Caught exception socket.error : %s" % exc)

    def _receive_video_thread(self):
        """
        Listens for video streaming (raw h264) from the Tello.

        Runs as a thread, sets self.frame to the most recent frame Tello captured.

        """
        packet_data = b''  # Initialize as bytes
        while True:
            try:
                res_string, ip = self.socket_video.recvfrom(2048)
                packet_data += res_string
                # end of frame
                if len(res_string) != 1460:
                    for frame in self._h264_decode(packet_data):
                        self.frame = frame
                    packet_data = b''  # Reset packet data
            except socket.error as exc:
                print("Caught exception socket.error : %s" % exc)
    
    def _h264_decode(self, packet_data):
        """
        Decode raw h264 format data from Tello
        
        :param packet_data: raw h264 data array
       
        :return: a list of decoded frame
        """
        res_frame_list = []
        frames = self.decoder.decode(packet_data)
        for framedata in frames:
            (frame, w, h, ls) = framedata
            if frame is not None:
                # print('frame size %i bytes, w %i, h %i, linesize %i' % (len(frame), w, h, ls))
                frame = np.frombuffer(frame, dtype=np.ubyte)
                frame = frame.reshape((h, ls // 3, 3))
                frame = frame[:, :w, :]
                res_frame_list.append(frame)
        return res_frame_list

    def send_command(self, command):
        """
        Send a command to the Tello and wait for a response.

        :param command: Command to send.
        :return (str): Response from Tello.
        """
        if command != 'battery?':
            print(">> send cmd: {}".format(command))
        self.abort_flag = False
        timer = threading.Timer(self.command_timeout, self.set_abort_flag)

        self.socket.sendto(command.encode('utf-8'), self.tello_address)

        timer.start()
        while self.response is None:
            if self.abort_flag:
                break
        timer.cancel()
        
        if self.response is None:
            response = 'none_response'
        else:
            response = self.response.decode('utf-8')

        self.response = None
        return response
    
    def set_abort_flag(self):
        """
        Sets self.abort_flag to True.

        Used by the timer in Tello.send_command() to indicate that a response
        timeout has occurred.
        """
        self.abort_flag = True

    def get_response(self):
        """
        Returns response of Tello.

        Returns:
            int: Response of Tello.
        """
        response = self.response
        return response

    def get_battery(self):
        """Returns percent battery life remaining.

        Returns:
            int: Percent battery life remaining.
        """
        battery = self.send_command('battery?')
        try:
            battery = int(battery)
        except:
            battery = 80
        return battery

    def get_flight_time(self):
        """Returns the number of seconds elapsed during flight.

        Returns:
            int: Seconds elapsed during flight.
        """
        flight_time = self.send_command('time?')
        try:
            flight_time = int(flight_time)
        except:
            pass
        return flight_time

    def takeoff(self):
        """
        Initiates take-off.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        return self.send_command('takeoff')

    def land(self):
        """Initiates landing.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.
        """
        return self.send_command('land')
    
    def send_rc_control(self, left_right_velocity: int, forward_backward_velocity: int, up_down_velocity: int,
                        yaw_velocity: int):
        """Send RC control via four channels. Command is sent every self.TIME_BTW_RC_CONTROL_COMMANDS seconds.
        Arguments:
            left_right_velocity: -100~100 (left/right)
            forward_backward_velocity: -100~100 (forward/backward)
            up_down_velocity: -100~100 (up/down)
            yaw_velocity: -100~100 (yaw)
        """
        def clamp100(x: int) -> int:
            return max(-100, min(100, x))

        if time.time() - self.last_rc_control_timestamp > self.TIME_BTW_RC_CONTROL_COMMANDS:
            self.last_rc_control_timestamp = time.time()
            cmd = 'rc {} {} {} {}'.format(
                clamp100(left_right_velocity),
                clamp100(forward_backward_velocity),
                clamp100(up_down_velocity),
                clamp100(yaw_velocity)
            )
            self.send_command_without_return(cmd)

    def send_command_without_return(self, command: str):
        """Send command to Tello without expecting a response.
        Internal method, you normally wouldn't call this yourself.
        """
        # Commands very consecutive makes the drone not respond to them. So wait at least self.TIME_BTW_COMMANDS seconds

        #self.LOGGER.info("Send command (no response expected): '{}'".format(command))
        self.socket.sendto(command.encode('utf-8'), self.tello_address)

    def start_tello(self):
        '''
        Inicializa o drone tello. Conecta, testa se é possível voar, habilita a transmissão por vídeo.
        '''
        user_input = input("Simular? (s/n): ").lower()
        self.video_decision = None
        if user_input == "s":
            self.simulate = True
            print("Simulando...")
            self.video_decision = input("Tello, webcam ou ambos? (t/w/b): ").lower()
            if self.video_decision in ['w', 'b']:
                self.webcam = cv2.VideoCapture(0)
                print("Abrindo vídeo da webcam")
        else:
            self.simulate = False
            print("Vamos voar...")

        if self.video_decision in ['t', 'b']:
            self.send_command("command")
            self.send_command("streamon")
            print("Conectei ao Tello")
            print("Abrindo vídeo do Tello")
            battery_error(self.get_battery())

        if not self.simulate:
            #self.takeoff() -> takeoff()
            self.send_command("takeoff")
            self.send_rc_control(0, 0, 0, 0)

    def end_tello(self):
        '''
        Finaliza o drone Tello.
        '''
        if not self.simulate:
            self.send_rc_control(0, 0, 0, 0)
            #self.land() -> verificar
            self.send_command("land")
        print("Finalizei")

    def start_webcam_video(self):
        '''
        Inicia a transmissão de vídeo da webcam.
        '''
        _, self.webcam_frame = self.webcam.read()
        self.webcam_frame = cv2.resize(self.webcam_frame, (WIDTH, HEIGHT))

    def start_video(self):
        '''
        Inicia a transmissão de vídeo do Tello.
        Pega cada frame da transmissão com tello_frame, converte a cor de RGB para BGR, muda o tamanho do frame para 544 x 306.
        Função de calcular frames já inclusa.
        '''
        if self.video_decision in ['t', 'b']:
            self.tello_frame = self.read()
            self.tello_frame = cv2.cvtColor(self.tello_frame, cv2.COLOR_RGB2BGR)
            self.tello_frame = cv2.resize(self.tello_frame, (WIDTH, HEIGHT))

            self.calc_fps(self.tello_frame)
            self.frame_detection = self.tello_frame
            cv2.putText(self.tello_frame, f"Battery: {self.get_battery()}", (350, 300), FONT, FONTSCALE, COLOR, THICKNESS) # texto deslocado para a esquerda

        if self.video_decision in ['w', 'b']:
            self.start_webcam_video()
            self.calc_fps(self.webcam_frame)
            self.frame_detection = self.webcam_frame

    def end_video(self):
        if self.video_decision in ['t', 'b']:
            self.send_command("streamoff")
        if self.video_decision in ['w', 'b']:
            self.webcam.release()
        cv2.destroyAllWindows()

    def calc_fps(self, frame):
        self.num_frames += 1
        self.elapsed_time = time.time() - self.start_time
        if self.elapsed_time >= 1:
            self.fps = int(self.num_frames / self.elapsed_time)
            self.num_frames = 0
            self.start_time = time.time() 
        cv2.putText(frame, f"FPS: {self.fps}", ORG, FONT, FONTSCALE, COLOR, THICKNESS)
