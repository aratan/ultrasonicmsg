import numpy as np
from scipy.io.wavfile import read
from scipy.fft import rfft, rfftfreq

FS = 32000
FREQ_BASE = 1000  # Misma frecuencia base que el emisor
FREQ_INCREMENTO = 50  # Mismo incremento
TOLERANCIA = 25  # Reducido por la mayor precisión
DURACION_BIT = 0.2
MUESTRAS_POR_CARACTER = int(FS * DURACION_BIT)
MUESTRAS_PAUSA = int(FS * 0.05)

# Leer el archivo WAV
fs_wav, data = read("senal.wav")
if fs_wav != FS:
    raise ValueError(f"Frecuencia de muestreo incorrecta: {fs_wav}Hz")

# Normalizar datos si es necesario
if data.dtype == np.int16:
    data = data.astype(np.float32) / np.iinfo(np.int16).max

mensaje_recibido = []
posicion = 0

while posicion < len(data):
    inicio = posicion
    fin = posicion + MUESTRAS_POR_CARACTER
    if fin > len(data):
        break
    
    bloque = data[inicio:fin]
    
    # Calcular FFT
    frecuencias = rfftfreq(len(bloque), d=1/FS)
    magnitudes = np.abs(rfft(bloque))
    
    # Encontrar frecuencia dominante
    indice_max = np.argmax(magnitudes)
    freq_detectada = frecuencias[indice_max]
    
    # Verificar rango y decodificar
    if FREQ_BASE - TOLERANCIA <= freq_detectada <= FREQ_BASE + 255*FREQ_INCREMENTO + TOLERANCIA:
        codigo_ascii = round((freq_detectada - FREQ_BASE) / FREQ_INCREMENTO)
        caracter = chr(codigo_ascii)
        mensaje_recibido.append(caracter)
    
    posicion += MUESTRAS_POR_CARACTER + MUESTRAS_PAUSA

print("Mensaje decodificado:", "".join(mensaje_recibido))