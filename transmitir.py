# transmitir.py
import numpy as np
import pyaudio
import time
import logging

logging.basicConfig(level=logging.DEBUG)

PREAMBLE_FREQ1 = 15000  # Frecuencia del primer tono del preámbulo (Hz)
PREAMBLE_FREQ2 = 16000  # Frecuencia del segundo tono del preámbulo (Hz)
FREQ_0 = 15000 # Frecuencia para '0' (Hz)
FREQ_1 = 16000 # Frecuencia para '1' (Hz)
BIT_DURATION = 0.1   # Duración de cada bit (segundos) - Ajustar
SAMPLE_RATE = 44100 # Tasa de muestreo (muestras por segundo)

def generar_tono(frecuencia, duracion, sample_rate=SAMPLE_RATE):
    """Genera una onda sinusoidal de la frecuencia y duración dadas."""
    t = np.linspace(0, duracion, int(sample_rate * duracion), endpoint=False)
    onda = 0.5 * np.sin(2 * np.pi * frecuencia * t)  # Amplitud 0.5 para evitar saturación
    return onda

def generar_senal(mensaje):
    """Función principal para la transmisión."""
    logging.info("Transmitiendo...")
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=SAMPLE_RATE, output=True)

    # 1. Preámbulo
    logging.debug("Enviando preámbulo...")
    stream.write(generar_tono(PREAMBLE_FREQ1, BIT_DURATION).astype(np.float32).tobytes())
    time.sleep(BIT_DURATION)  # Importante: Esperar después de cada tono
    stream.write(generar_tono(PREAMBLE_FREQ2, BIT_DURATION).astype(np.float32).tobytes())
    time.sleep(BIT_DURATION)

    # 2. Mensaje
    logging.debug("Enviando mensaje: %s", mensaje)
    for char in mensaje:
        binary_char = bin(ord(char))[2:].zfill(8)  # Convertir a binario (8 bits)
        #logging.debug("Enviando carácter: %s (binario: %s)", char, binary_char)
        for bit in binary_char:
            if bit == '1':
                stream.write(generar_tono(FREQ_1, BIT_DURATION).astype(np.float32).tobytes())
                time.sleep(BIT_DURATION)
            else:
                stream.write(generar_tono(FREQ_0, BIT_DURATION).astype(np.float32).tobytes())
                time.sleep(BIT_DURATION)

    stream.stop_stream()
    stream.close()
    p.terminate()
    logging.info("Transmisión completada.")

if __name__ == '__main__':
    generar_senal("Hola") #Prueba