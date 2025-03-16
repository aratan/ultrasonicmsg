import numpy as np
import sounddevice as sd
import scipy.fftpack as fft
import time

# Configuración
FREQ_ULTRASONICA = 20000  # 19 kHz
DURACION = 0.5  # Duración en segundos
FS = 44100  # Frecuencia de muestreo

def generar_ultrasonido(mensaje):
    """Convierte un mensaje en un tono ultrasónico modulando la frecuencia."""
    t = np.linspace(0, DURACION, int(FS * DURACION), endpoint=False)
    onda = np.sin(2 * np.pi * FREQ_ULTRASONICA * t)
    sd.play(onda, FS)
    time.sleep(DURACION)
    sd.stop()

def recibir_ultrasonido():
    """Graba el audio y detecta si hay una señal en la frecuencia objetivo."""
    grabacion = sd.rec(int(DURACION * FS), samplerate=FS, channels=1, dtype='float32')
    sd.wait()
    fft_resultado = np.abs(fft.fft(grabacion[:,0]))
    freqs = fft.fftfreq(len(fft_resultado), 1 / FS)

    # Detecta un pico en 19 kHz
    if np.max(fft_resultado[(freqs > 18900) & (freqs < 19100)]) > 0.1:
        print("🔊 Mensaje recibido en 19 kHz!")
    else:
        print("❌ No se detectó nada.")

# Prueba de transmisión y recepción
generar_ultrasonido("Hola")
recibir_ultrasonido()
