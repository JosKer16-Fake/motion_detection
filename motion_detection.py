import cv2
import numpy as np
import rtmidi
import time
import threading
import config  # importa as configurações


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


def enviar_note_off(nota=60, canal=config.CANAL, zona=0,
                    motion_level=0, intensidade=0):
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


# Função para cooldown por zona (executada em thread)
def cooldown_note_off(nota, canal, zona, motion_level, intensidade, delay, idx, locks):
    agora = time.strftime("%H:%M:%S")
    print(f"[{agora}] ZONA {zona} → cooldown thread iniciada (idx={idx}, delay={delay}s)")
    time.sleep(delay)
    enviar_note_off(nota=nota, canal=canal, zona=zona,
                    motion_level=motion_level, intensidade=intensidade)
    # Liberta a flag com proteção
    with locks[idx]:
        zona_em_cooldown[idx] = False
        agora = time.strftime("%H:%M:%S")
        print(f"[{agora}] ZONA {zona} → cooldown terminado (idx={idx})")


# Inicializar captura da câmara
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

# Definir zonas de deteção (com base na imagem recortada)
zones = []
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) // 2  # metade da altura

zone_w = width // config.NUM_COLS
zone_h = height // config.NUM_ROWS

for row in range(config.NUM_ROWS):
    for col in range(config.NUM_COLS):
        x = col * zone_w
        y = row * zone_h
        zones.append((x, y, zone_w, zone_h))

zona_ativa = [False] * len(zones)
zona_em_cooldown = [False] * len(zones)  # flag de cooldown por zona

# Locks por zona para proteção de leitura/escrita nas flags
zona_locks = [threading.Lock() for _ in range(len(zones))]

cv2.namedWindow("Detecção de Movimento - Zonas", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Detecção de Movimento - Zonas", 1200, 225)  # metade da altura


# Loop principal
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Recortar apenas o centro vertical da imagem, deslocado 8% para baixo
    h, w = frame.shape[:2]
    recorte_altura = h // 2
    offset = int(h * 0.01)  # deslocamento de 8% da altura total

    inicio = (h - recorte_altura) // 2 + offset
    fim = inicio + recorte_altura

    # Garantir que não ultrapassa os limites da imagem
    if fim > h:
        fim = h
        inicio = h - recorte_altura

    frame = frame[inicio:fim, :]  # mantém toda a largura

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
        motion_level = np.sum(zone_crop) / 255
        intensidade = (motion_level / (w * h)) * 100

        # Leitura das flags com lock para evitar races
        with zona_locks[i]:
            ativa = zona_ativa[i]
            em_cool = zona_em_cooldown[i]

        # Condição para disparar NOTE ON: não ativa e não em cooldown
        if motion_level > config.PIXELS_THRESHOLD and not ativa and not em_cool:
            nota = config.BASE_NOTE + i
            with zona_locks[i]:
                if not zona_ativa[i] and not zona_em_cooldown[i]:
                    zona_ativa[i] = True
                    zona_em_cooldown[i] = True
                    agora = time.strftime("%H:%M:%S")
                    print(f"[{agora}] ZONA {i+1} → disparo permitido, iniciando NOTE ON e cooldown")
                    enviar_note_on(nota=nota, zona=i+1,
                                   motion_level=motion_level, intensidade=intensidade)
                    # Lança thread para cooldown
                    t = threading.Thread(target=cooldown_note_off,
                                         args=(nota, config.CANAL, i+1,
                                               motion_level, intensidade, config.COOLDOWN_TIME, i, zona_locks))
                    t.daemon = True
                    t.start()
        elif motion_level <= config.PIXELS_THRESHOLD:
            with zona_locks[i]:
                if zona_ativa[i]:
                    zona_ativa[i] = False
                    agora = time.strftime("%H:%M:%S")
                    print(f"[{agora}] ZONA {i+1} → ficou inativa (motion abaixo do threshold)")

        color = (0, 0, 255) if zona_ativa[i] else (0, 255, 0)
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, f"Zona {i+1}", (x+10, y+30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    frame_resized = cv2.resize(frame, (1200, 225))
    cv2.imshow("Detecção de Movimento - Zonas", frame_resized)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        # Reset manual das zonas e do frame de comparação
        first_frame = None
        zona_ativa = [False] * len(zones)
        zona_em_cooldown = [False] * len(zones)
        print(">>> Reset efetuado: zonas e frame de comparação reiniciados <<<")

cap.release()
cv2.destroyAllWindows()
