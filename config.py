# config.py

# Número máximo de câmaras a testar
NUM_CAMERAS = 4   # índices 0 a 3

# Resolução e FPS da captura (pedido à câmara)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480   # continua a pedir altura total
FPS = 30

# Divisão da imagem em zonas (2 linhas × 4 colunas = 8 zonas)
NUM_ROWS = 2
NUM_COLS = 4

# Parâmetros da deteção de movimento
PIXELS_THRESHOLD = 1000
BLUR_KERNEL = (21, 21)
THRESHOLD_VALUE = 25
DILATE_ITERATIONS = 2

# Cooldown entre eventos (segundos)
COOLDOWN_TIME = 0.5

# MIDI
MIDI_PORT_NAME = "loopMIDI"
BASE_NOTE = 60
VELOCIDADE = 100
CANAL = 0

# Novo parâmetro para recorte vertical
CROP_VERTICAL = True   # se True, recorta para metade da altura (centro)

#Tempo de cooldown
COOLDOWN_TIME = 2.0
