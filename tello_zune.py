import cv2
import time
from tello import Tello

FONT = cv2.FONT_HERSHEY_SIMPLEX
COLOR = (0, 255, 0)
ORG = (30, 30)
FONTSCALE = 1
THICKNESS = 2
WIDTH = 544
HEIGHT = 306

class BatteryError(Exception):
    pass

def battery_error(tello_battery): # verificar
    tello_battery = int(tello_battery)
    if tello_battery <= 20:
        raise BatteryError("Bateria menor que 20%, operação cancelada.")

class TelloZune(Tello):
    def __init__(self, local_ip='', local_port=8889, imperial=False, command_timeout=0.3, tello_ip='192.168.10.1', tello_port=8889):
        super().__init__(local_ip, local_port, imperial, command_timeout, tello_ip, tello_port)
        self.num_frames = 0
        self.start_time = time.time()
        self.fps = 0
        self.last_rc_control_timestamp = time.time()  # Inicializa o timestamp do controle remoto

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
            battery_error(self.get_battery())
            self.send_command("streamon")
            print("Conectei ao Tello")
            print("Abrindo vídeo do Tello")

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
