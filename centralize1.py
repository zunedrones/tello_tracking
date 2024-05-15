import numpy as np

Width = 544
Height = 306
#coordenadas do centro
CenterX = Width // 2
CenterY = Height // 2
#erro anterior
prevErrorX = 0
prevErrorY = 0
#coeficiente proporcional (obtido testando)
#determina o quanto a velocidade deve mudar em resposta ao erro atual
Kp = 0.4
#coeficiente derivativo (obtido testando)
#responsável por controlar a taxa de variação do erro
Kd = 0.4

width_detect = 0
area_land = 0

def centralize(tello, values_detect, only_tracking = False):
    '''
    Centraliza o objeto detectado no centro da tela. Recebe como argumentos: tello, objeto tello
    que possui os métodos da biblioteca djitellopy, values_detect, um vetor que possui as coordenadas
    da detecção e o número de detecções [x1, y1, x2, y2, detections], only_tracking, se True
    apenas efetua o tracking do objeto sem pousar, e False detecta e pousa.
    A função retorna False se a função de pousar for chamada, e True se ainda não.
    '''
    global prevErrorX, prevErrorY, CenterX, CenterY, Kp, Kd, width_detect, area_land
    _, x1, y1, x2, y2, detections = values_detect
    speedFB = 0
    # detectWidth = x2 - x1
    cxDetect = (x2 + x1) // 2
    cyDetect = (y2 + y1) // 2

    #PID - Speed Control
    width_detect = x2 - x1
    area = (x2 - x1) * (y2 - y1)
    print(f"Area: {area}")
    print(f"DETECTIONS: {detections}")
    #se o centro da detecção encontrar-se na esquerda, o erro na horizontal será negativo
    #se o objeto estiver na direita, o erro será positivo
    if (detections > 0):
        errorX = cxDetect - CenterX
        errorY = CenterY - cyDetect
        if area < 27000: # calibrar
            speedFB = 25
            print(f"AREA: {area}")
        elif area > 120000 and only_tracking:
            speedFB = -25
            print(f"AREA: {area}")
            
        if area > 30000:
            area_land = area
    else:
        errorX = 0
        errorY = 0
        print("0 DETECTIONS")
        print(f"AREA: {area_land}")

        if tello.get_height() <= 23 and area_land > 30000 and not only_tracking:
            print("TENTEI POUSAR")
            tello.send_rc_control(0, 0, 0, 0)
            tello.move_forward(35)
            return False
    
    print(f"ALTURA: {tello.get_height()}")
    #velocidade de rotação em torno do próprio eixo é calculada em relação ao erro horizontal
    speedYaw = Kp*errorX + Kd*(errorX - prevErrorX)
    speedUD = Kp*errorY + Kd*(errorY - prevErrorY)
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

    return True


