# recibir.py
import numpy as np
import pyaudio
import time
import logging
from scipy.fft import fft, fftfreq

logging.basicConfig(level=logging.DEBUG)

PREAMBLE_FREQ1 = 15000
PREAMBLE_FREQ2 = 16000
FREQ_0 = 15000
FREQ_1 = 16000
BIT_DURATION = 0.1  # Debe coincidir con el de transmitir.py
SAMPLE_RATE = 44100
THRESHOLD = 0.1  # Umbral para la detección de tonos (ajustar)
TIMEOUT = 5
CHUNK_SIZE = 2048 # Potencia de 2

def detectar_tono(datos, frecuencia, sample_rate=SAMPLE_RATE):
    """Detecta si una frecuencia específica está presente en los datos de audio."""
    yf = fft(datos)
    xf = fftfreq(len(datos), 1 / sample_rate)
    idx = (np.abs(xf - frecuencia)).argmin()
    amplitud = abs(yf[idx])
    logging.debug("Amplitud de la frecuencia %s Hz: %s", frecuencia, amplitud) #Log
    return amplitud > THRESHOLD

def iniciar_recepcion(timeout=TIMEOUT):
    """Función principal para la recepción."""
    logging.info("Iniciando recepción...")
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=SAMPLE_RATE, input=True, frames_per_buffer=CHUNK_SIZE)

    start_time = time.time()
    preamble_detected = False
    mensaje_recibido = ""

    # 1. Esperar Preámbulo
    while time.time() - start_time < timeout and not preamble_detected:
        try:
            datos = np.frombuffer(stream.read(CHUNK_SIZE), dtype=np.float32)
        except OSError as e:
            logging.error(f"Error de lectura: {e}")
            return ""
        if detectar_tono(datos, PREAMBLE_FREQ1, SAMPLE_RATE):
            logging.info("Detectado tono de preámbulo 1...")
            # Esperar el segundo tono del preámbulo dentro del mismo CHUNK o el siguiente.
            # Ajuste importante para evitar problemas de sincronización.
            datos_extra = np.array([], dtype=np.float32)
            #Leer CHUNKS adicionales hasta encontrar el segundo tono, o timeout.
            while time.time() - start_time < timeout:
                try:
                    data_extra = np.frombuffer(stream.read(CHUNK_SIZE), dtype=np.float32)
                except OSError as e:
                    logging.error(f"Error de lectura: {e}")
                    return ""
                datos_extra = np.concatenate((datos_extra, data_extra))
                if detectar_tono(datos_extra, PREAMBLE_FREQ2, SAMPLE_RATE):
                    logging.info("Preámbulo detectado!")
                    preamble_detected = True
                    break  # Sale del bucle interno (detección del segundo tono)
            if preamble_detected:
                break # Sale del bucle externo de espera.

    if not preamble_detected:
        logging.warning("Timeout: No se detectó el preámbulo.")
        stream.close()
        p.terminate()
        return ""

    # 2. Decodificar Mensaje
    binary_data = ""
    while time.time() - start_time < timeout:
        try:
           datos = np.frombuffer(stream.read(CHUNK_SIZE), dtype=np.float32)
        except OSError as e:
            logging.error(f"Error de lectura {e}")
            break

        if detectar_tono(datos, FREQ_1, SAMPLE_RATE):
            binary_data += "1"
            logging.debug("Bit recibido: 1")
        elif detectar_tono(datos, FREQ_0, SAMPLE_RATE):
            binary_data += "0"
            logging.debug("Bit recibido: 0")
        # else: # Comentado para que sea mas permisivo y capture aun en presencia de ruido.
           # logging.debug("No se detectó un tono claro.")

        if len(binary_data) == 8:
            try:
                char_code = int(binary_data, 2)
                char = chr(char_code)
                mensaje_recibido += char
                logging.debug("Carácter decodificado: %s", char)
            except ValueError:
                logging.error("Error al decodificar el carácter: %s", binary_data)
                break
            binary_data = ""

    stream.stop_stream()
    stream.close()
    p.terminate()
    logging.info("Mensaje recibido: %s", mensaje_recibido)
    return mensaje_recibido