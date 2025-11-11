# 🎥 Motion Detection MIDI Controller

Este projeto permite transformar movimento captado por uma câmara em sinais **MIDI**, que podem ser usados para controlar instrumentos virtuais ou software musical.  
A imagem da câmara é dividida em **8 zonas** e cada zona ativa uma nota MIDI quando é detetado movimento.

---

## 🚀 Funcionalidades
- Deteção de movimento em tempo real com **OpenCV**
- Divisão da imagem em **8 zonas (2 linhas × 4 colunas)**
- Envio de mensagens **MIDI Note On/Off** através de `rtmidi`
- Feedback visual: zonas ficam a vermelho quando ativas
- Feedback textual: consola mostra nota, zona e intensidade

---

## 🛠️ Tecnologias usadas
- **Python 3.11+**
- **OpenCV** para captura e processamento de vídeo
- **NumPy** para cálculos de pixels
- **rtmidi** para comunicação MIDI

---

## 📦 Instalação
1. Clonar o repositório:
   ```bash
   git clone https://github.com/seuuser/motion-detection-midi.git
   cd motion-detection-midi
