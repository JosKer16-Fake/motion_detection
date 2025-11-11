# config.py

# Número máximo de câmaras a testar
NUM_CAMERAS = 4   # índices 0 a 3
 
# Resolução e FPS da captura
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30
 
# Divisão da imagem em zonas (2 linhas × 4 colunas = 8 zonas)
NUM_ROWS = 2
NUM_COLS = 4
 
# Parâmetros da deteção de movimento
PIXELS_THRESHOLD = 5000        # nº de pixels ativos para considerar movimento
BLUR_KERNEL = (21, 21)         # suavização da imagem
THRESHOLD_VALUE = 25           # sensibilidade da diferença de frames
DILATE_ITERATIONS = 2          # nº de dilatações para reforçar áreas de movimento
 
# Cooldown entre eventos (segundos)
COOLDOWN_TIME = 0.5            # tempo mínimo entre Note ON/OFF
 
# MIDI
MIDI_PORT_NAME = "loopMIDI"    # nome da porta MIDI virtual
BASE_NOTE = 60                 # nota inicial para a primeira zona
VELOCIDADE = 100               # intensidade da nota MIDI
CANAL = 0                      # canal MIDI

