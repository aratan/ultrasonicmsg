import numpy as np
from scipy.io.wavfile import write
import argparse

FS = 44100  # Frecuencia de muestreo compatible con ultrasonidos
DURACION_BIT = 0.2
FREQ_BASE = 16000 # Frecuencia base que podemos cambiar
FREQ_INCREMENTO = 50  # Espaciado entre caracteres
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

def main():
    parser = argparse.ArgumentParser(description="Genera una señal ultrasónica a partir de un mensaje.")
    parser.add_argument('-m', '--mensaje', type=str, required=True, help='El mensaje a codificar en la señal ultrasónica.')
    
    args = parser.parse_args()
    
    mensaje = args.mensaje
    senal = generar_senal(mensaje)
    write("senal_ultrasonica.wav", FS, senal)
    print(f"senal_ultrasonica.wav generado con el mensaje: {mensaje}")

if __name__ == "__main__":
    main()