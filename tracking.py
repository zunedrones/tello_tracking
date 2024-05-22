import numpy as np

# largura e altura da tela
WIDTH = 544
HEIGHT = 306
#coordenadas do centro
CENTERX = WIDTH // 2
CENTERY = HEIGHT // 2
#coeficiente proporcional (obtido testando)
KP = 0.4
#coeficiente derivativo (obtido testando)
KD = 0.4
#erro anterior
prevErrorX = 0
prevErrorY = 0

def start_tracking(tello, values_detect):
    '''
    Faz o tracking do objeto detectado. Recebe como argumentos: tello, objeto tello
    que possui os métodos da biblioteca djitellopy, values_detect, um vetor que possui as coordenadas
    da detecção e o número de detecções [x1, y1, x2, y2, detections].
    A função retorna False se a função de pousar for chamada, e True se ainda não.
    '''
    global prevErrorX, prevErrorY
    _, x1, y1, x2, y2, detections = values_detect
    speedFB = 0
    
    cxDetect = (x2 + x1) // 2
    cyDetect = (y2 + y1) // 2

    #PID - Speed Control
    area = (x2 - x1) * (y2 - y1)
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
        print("0 DETECTIONS")
    
    #velocidade de rotação em torno do próprio eixo é calculada em relação ao erro horizontal
    speedYaw = KP*errorX + KD*(errorX - prevErrorX)
    speedUD = KP*errorY + KD*(errorY - prevErrorY)
    #não permite que a velocidade 'vaze' o intervalo -100 / 100
    speedYaw = int(np.clip(speedYaw,-100,100))
    speedUD = int(np.clip(speedUD,-100,100))
    
    print(f"FB: {speedFB}, UD: {speedUD}, YAW: {speedYaw}")
    if(detections != 0):
        tello.send_rc_control(0, speedFB, speedUD, speedYaw)
    else:
        tello.send_rc_control(0, 0, 0, 0)
    #o erro atual vira o erro anterior
    prevErrorX = errorX
    prevErrorY = errorY