import cv2
import numpy as np
import rtmidi
import time
import config   # importa as configurações

# Funções MIDI com feedback na consola
def enviar_note_on(nota=60, velocidade=config.VELOCIDADE, canal=config.CANAL,
                   zona=0, motion_level=0, intensidade=0):
    midiout = rtmidi.MidiOut()
    ports = midiout.get_ports()
    for i, port in enumerate(ports):
        if config.MIDI_PORT_NAME in port:
            midiout.open_port(i)
            break
    else:
        print("Porta MIDI não encontrada.")
        return
    midiout.send_message([0x90 + canal, nota, velocidade])
    midiout.close_port()
    agora = time.strftime("%H:%M:%S")
    print(f"[{agora}] ZONA {zona} → NOTE ON | Nota: {nota} | Pixels: {motion_level:.0f} | Intensidade: {intensidade:.2f}%")

def enviar_note_off(nota=60, canal=config.CANAL, zona=0, motion_level=0, intensidade=0):
    midiout = rtmidi.MidiOut()
    ports = midiout.get_ports()
    for i, port in enumerate(ports):
        if config.MIDI_PORT_NAME in port:
            midiout.open_port(i)
            break
    else:
        print("Porta MIDI não encontrada.")
        return
    midiout.send_message([0x80 + canal, nota, 0])
    midiout.close_port()
    agora = time.strftime("%H:%M:%S")
    print(f"[{agora}] ZONA {zona} → NOTE OFF | Nota: {nota} | Pixels: {motion_level:.0f} | Intensidade: {intensidade:.2f}%")

# Inicializar captura
cap = None
for i in range(config.NUM_CAMERAS):
    temp = cv2.VideoCapture(i)
    if temp.isOpened():
        print(f"Câmara encontrada no índice {i}")
        cap = temp
        break
    else:
        temp.release()

if cap is None:
    print("Erro: nenhuma câmara disponível.")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, config.FPS)

first_frame = None

# Definir zonas
zones = []
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
zone_w = width // config.NUM_COLS
zone_h = height // config.NUM_ROWS

for row in range(config.NUM_ROWS):
    for col in range(config.NUM_COLS):
        x = col * zone_w
        y = row * zone_h
        zones.append((x, y, zone_w, zone_h))

zona_ativa = [False] * len(zones)

cv2.namedWindow("Detecção de Movimento - Zonas", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Detecção de Movimento - Zonas", 1200, 450)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, config.BLUR_KERNEL, 0)

    if first_frame is None:
        first_frame = gray
        continue

    frame_delta = cv2.absdiff(first_frame, gray)
    thresh = cv2.threshold(frame_delta, config.THRESHOLD_VALUE, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=config.DILATE_ITERATIONS)

    for i, (x, y, w, h) in enumerate(zones):
        zone_crop = thresh[y:y+h, x:x+w]
        motion_level = np.sum(zone_crop) / 255   # nº de pixels ativos
        intensidade = (motion_level / (w * h)) * 100  # % da zona ocupada

        if motion_level > config.PIXELS_THRESHOLD and not zona_ativa[i]:
            enviar_note_on(nota=config.BASE_NOTE + i, zona=i+1,
                           motion_level=motion_level, intensidade=intensidade)
            zona_ativa[i] = True

        elif motion_level <= config.PIXELS_THRESHOLD and zona_ativa[i]:
            enviar_note_off(nota=config.BASE_NOTE + i, zona=i+1,
                            motion_level=motion_level, intensidade=intensidade)
            zona_ativa[i] = False

        color = (0, 0, 255) if zona_ativa[i] else (0, 255, 0)
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, f"Zona {i+1}", (x+10, y+30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    frame_resized = cv2.resize(frame, (1200, 450))
    cv2.imshow("Detecção de Movimento - Zonas", frame_resized)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
