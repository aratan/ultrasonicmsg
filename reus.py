import numpy as np
from scipy.io.wavfile import read
from scipy.fft import rfft, rfftfreq

FS = 44100
FREQ_BASE = 16000 # Frecuencia base que podemos cambiar
FREQ_INCREMENTO = 50
TOLERANCIA = 100  # Tolerancia ampliada
DURACION_BIT = 0.2
MUESTRAS_POR_CARACTER = int(FS * DURACION_BIT)
MUESTRAS_PAUSA = int(FS * 0.05)

# Leer el archivo WAV
fs_wav, data = read("senal_ultrasonica.wav")
if fs_wav != FS:
    raise ValueError(f"Frecuencia de muestreo incorrecta: {fs_wav}Hz")

# Normalizar datos
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
    
    # Aplicar ventana de Hanning para reducir fugas
    ventana = np.hanning(len(bloque))
    bloque_ventana = bloque * ventana
    
    # Calcular FFT
    frecuencias = rfftfreq(len(bloque_ventana), d=1/FS)
    magnitudes = np.abs(rfft(bloque_ventana))
    
    # Encontrar frecuencia dominante
    indice_max = np.argmax(magnitudes)
    freq_detectada = frecuencias[indice_max]
    
    # Verificar rango y decodificar
    if (FREQ_BASE - TOLERANCIA <= freq_detectada <= 
        FREQ_BASE + 255*FREQ_INCREMENTO + TOLERANCIA):
        
        codigo_ascii = round((freq_detectada - FREQ_BASE) / FREQ_INCREMENTO)
        caracter = chr(codigo_ascii)
        mensaje_recibido.append(caracter)
        print(f"Detectado: {freq_detectada} Hz → {caracter}")  # Depuración
    
    posicion += MUESTRAS_POR_CARACTER + MUESTRAS_PAUSA

print("Mensaje decodificado:", "".join(mensaje_recibido))