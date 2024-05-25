import cv2
import time

FONT = cv2.FONT_HERSHEY_SIMPLEX
COLOR = (0, 255, 0)
ORG = (30, 30)
FONTSCALE = 1
THICKNESS = 2
WIDTH = 544
HEIGHT = 306

class BatteryError(Exception):
    pass

def battery_error(tello_battery: int):
    if tello_battery <= 20:
        raise BatteryError("Bateria menor que 20%, operação cancelada.")

class TelloZune():
    def __init__(self):
        super().__init__()
        self.num_frames = 0
        self.start_time = time.time()
        self.fps = 0

    def start_tello(self):
        '''
        Inicializa o drone tello. Conecta, testa se é possivel voar, habilita a transmissao por video.
        '''
        user_input = input("Simular? (s/n): ").lower()
        self.video_decision = None
        if user_input == "s":
            self.simulate = True
            print("simulando...")
            self.video_decision = input("Tello, webcam ou ambos? (t/w/b): ").lower()
            if self.video_decision == 'w' or self.video_decision == 'b':
                self.webcam = cv2.VideoCapture(0)
                print("abrindo video webcam")
        else:
            self.simulate = False
            print("vamos voar...")

        if self.video_decision == 't' or self.video_decision == 'b':
            self.connect()
            battery_error(self.get_battery())
            self.streamon()
            print("conectei ao Tello")
            print("abrindo video tello")

        if not self.simulate:
            self.takeoff()
            self.send_rc_control(0, 0, 0, 0)

    def send_rc_control(self, left_right_velocity: int, forward_backward_velocity: int, up_down_velocity: int,
                        yaw_velocity: int):
        """Send RC control via four channels. Command is sent every self.TIME_BTW_RC_CONTROL_COMMANDS seconds.
        Arguments:
            left_right_velocity: -100~100 (left/right)
            forward_backward_velocity: -100~100 (forward/backward)
            up_down_velocity: -100~100 (up/down)
            yaw_velocity: -100~100 (yaw)
        """
        """ def clamp100(x: int) -> int:
            return max(-100, min(100, x))

        if time.time() - self.last_rc_control_timestamp > self.TIME_BTW_RC_CONTROL_COMMANDS:
            self.last_rc_control_timestamp = time.time()
            cmd = 'rc {} {} {} {}'.format(
                clamp100(left_right_velocity),
                clamp100(forward_backward_velocity),
                clamp100(up_down_velocity),
                clamp100(yaw_velocity)
            )
            self.send_command_without_return(cmd) """

    def end_tello(self):
        '''
        Finaliza o drone tello.
        '''
        if not self.simulate:
            self.send_rc_control(0, 0, 0, 0)
            self.land()
        print("finalizei")

    def start_webcam_video(self):
        '''
        Inicia a transmissao de video da webcam.
        '''
        #cv2.namedWindow('Webcam')
        #cv2.startWindowThread(0)
        _, self.webcam_frame = self.webcam.read()
        self.webcam_frame = cv2.resize(self.webcam_frame, (WIDTH, HEIGHT))


    def start_video(self):
        '''
        Inicia a transmissao de video do tello. 
        Pega cada frame da transmissao com tello_frame, converte a cor de RGB para BGR, muda o tamanho do frame para 544 x 306.
        Funcao de calcular frames ja inclusa.
        '''
        if self.video_decision == 't' or self.video_decision == 'b':
            self.tello_frame = self.get_frame_read().frame
            self.tello_frame = cv2.cvtColor(self.tello_frame, cv2.COLOR_RGB2BGR)
            self.tello_frame = cv2.resize(self.tello_frame, (WIDTH, HEIGHT))

            self.calc_fps(self.tello_frame)
            self.frame_detection = self.tello_frame
            cv2.putText(self.tello_frame, f"Battery: {self.get_battery()}", (400, 300), FONT, FONTSCALE, COLOR, THICKNESS)
            #cv2.imshow("video", self.tello_frame)

        if self.video_decision == 'w' or self.video_decision == 'b':
            self.start_webcam_video()
            self.calc_fps(self.webcam_frame)
            self.frame_detection = self.webcam_frame
            #cv2.imshow('Webcam', self.webcam_frame)

    def end_video(self):
        if self.video_decision == 't' or self.video_decision == 'b':
            self.streamoff()
        if self.video_decision == 'w' or self.video_decision == 'b':
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
    