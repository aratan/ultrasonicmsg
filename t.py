import numpy as np
import sounddevice as sd
import argparse

# Parámetros críticos (DEBEN SER IGUALES EN RECEPTOR)
FS = 44100               # Frecuencia de muestreo estándar
FREQ_BASE = 15000 # oculto 16000, normal 155
FREQ_INCREMENTO = 50     # Espaciado entre caracteres (Hz)
AMPLITUD = 0.8           # Amplitud ajustada (0.0 a 1.0)
DURACION_BIT = 0.0667    # Duración de cada carácter (segundos, REDUCIDO)
PREAMBLE = "*"         # Preámbulo para sincronización

def generar_senal(mensaje):
    senal = []
    mensaje_completo = PREAMBLE + mensaje + ".*"
    
    for caracter in mensaje_completo:
        # Calcular frecuencia para cada carácter
        frecuencia = FREQ_BASE + (ord(caracter) * FREQ_INCREMENTO)
        tiempo = np.linspace(0, DURACION_BIT, int(FS * DURACION_BIT), False)
        onda = AMPLITUD * np.sin(2 * np.pi * frecuencia * tiempo)
        
        # Añadir pausa entre caracteres (igual al 25% de DURACION_BIT)
        pausa = np.zeros(int(FS * 0.0167))  # Pauses más cortas
        senal.extend(np.concatenate([onda, pausa]))
        
        print(f"Generado: '{caracter}' → {frecuencia} Hz")
    
    return np.array(senal, dtype=np.float32)

def main():
    parser = argparse.ArgumentParser(description="Emisor de señales acústicas")
    parser.add_argument('-m', '--mensaje', type=str, required=True, help='Texto a transmitir')
    args = parser.parse_args()

    print(f"\n--- Transmitiendo: '{args.mensaje}' ---")
    senal = generar_senal(args.mensaje.upper())
    sd.play(senal, FS)
    sd.wait()

if __name__ == "__main__":
    main()