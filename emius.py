import numpy as np
from scipy.io.wavfile import write

FS = 32000
DURACION_BIT = 0.2
FREQ_BASE = 1000  # Frecuencia base ajustada
FREQ_INCREMENTO = 50  # Incremento reducido (max: 1000 + 255*50 = 13,750 Hz < 16 kHz)
AMPLITUD = 0.5

def generar_senal(mensaje):
    senal = []
    for caracter in mensaje:
        frecuencia = FREQ_BASE + (ord(caracter) * FREQ_INCREMENTO)
        tiempo = np.linspace(0, DURACION_BIT, int(FS * DURACION_BIT), False)
        onda = AMPLITUD * np.sin(2 * np.pi * frecuencia * tiempo)
        pausa = np.zeros(int(FS * 0.05))
        senal.extend(np.concatenate([onda, pausa]))
    return np.array(senal, dtype=np.float32)

mensaje = "Hola Victor"
senal = generar_senal(mensaje)
write("senal.wav", FS, senal)
print(f"senal.wav generado con el mensaje: {mensaje}")
print(f"senal.wav generado con el mensaje: {mensaje}")