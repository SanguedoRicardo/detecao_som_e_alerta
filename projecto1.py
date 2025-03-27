import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
from datetime import datetime
import json
import os

# Configurações de som
RATE = 44100
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1

# Histórico de intensidades
HISTORICO = 100
intensidades = np.zeros(HISTORICO)

# Ficheiro para guardar eventos de som
FICHEIRO_EVENTOS = "eventos.json"

# Cria o ficheiro de eventos se ainda não existir
if not os.path.exists(FICHEIRO_EVENTOS):
    with open(FICHEIRO_EVENTOS, 'w') as f:
        json.dump([], f)

# Função para guardar eventos (quando o som ultrapassa o limiar)
def guardar_evento(intensidade):
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    evento = {
        "data": agora,
        "intensidade": int(intensidade)
    }
    with open(FICHEIRO_EVENTOS, 'r+') as f:
        dados = json.load(f)
        dados.append(evento)
        f.seek(0)
        json.dump(dados, f, indent=2)

# Criação do gráfico e do slider interativo
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)
linha, = ax.plot(intensidades, lw=2, color='green')
ax.set_ylim(0, 10000)
ax.set_title("Intensidade do Som (em tempo real)")
ax.set_xlabel("Tempo")
ax.set_ylabel("Intensidade")

# Slider para ajustar o limiar de deteção
ax_slider = plt.axes([0.15, 0.1, 0.75, 0.03])
slider_threshold = Slider(ax_slider, "Limiar", 0.0, 10000.0, valinit=3000.0)

# Inicialização do stream de áudio
pa = pyaudio.PyAudio()
stream = pa.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Função de atualização do gráfico (executada periodicamente)
def update(frame):
    global intensidades

    data = stream.read(CHUNK, exception_on_overflow=False)
    audio = np.frombuffer(data, dtype=np.int16).astype(np.float32)
    intensidade = np.abs(audio).mean()

    # Atualiza o histórico com a nova intensidade
    intensidades = np.roll(intensidades, -1)
    intensidades[-1] = intensidade
    linha.set_ydata(intensidades)

    # Verifica se ultrapassa o limiar definido no slider
    limiar = slider_threshold.val

    if intensidade > limiar:
        linha.set_color('red')  # Alerta visual
        print(f"🔴 Som detetado: {int(intensidade)}")
        guardar_evento(intensidade)  # Regista o evento
    else:
        linha.set_color('green')

    return linha,

# Inicia a animação do gráfico em tempo real
ani = FuncAnimation(fig, update, interval=50, blit=True)
plt.show()

# Fecha corretamente o stream de áudio ao terminar
stream.stop_stream()
stream.close()
pa.terminate()
