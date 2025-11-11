
---

## 📄 README.md — Versão 1.1

```markdown
# 🎥 Motion Detection MIDI Controller — v1.1

Este projeto evoluiu para a versão **1.1**, trazendo melhorias de organização e personalização.  
Agora as configurações estão separadas num ficheiro `config.py`, permitindo ajustar facilmente parâmetros como número de câmaras, resolução, thresholds e notas MIDI.

---

## 🚀 Novidades da versão 1.1
- 📂 **Configurações externas** em `config.py`
  - Número de câmaras a testar
  - Resolução e FPS
  - Threshold de pixels para ativar movimento
  - Cooldown entre eventos
  - Notas MIDI base e canal
- 🎨 Suporte para **ícone personalizado** no executável gerado com PyInstaller
- 🧹 Código mais modular e limpo

---

## 🛠️ Tecnologias usadas
- **Python 3.11+**
- **OpenCV**
- **NumPy**
- **rtmidi**
- **PyInstaller** (para gerar executável com ícone)

---

## 📦 Instalação
1. Clonar o repositório:
   ```bash
   git clone https://github.com/seuuser/motion-detection-midi.git
   cd motion-detection-midi