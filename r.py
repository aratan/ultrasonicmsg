import numpy as np
import sounddevice as sd
from scipy.fft import rfft, rfftfreq

# Parámetros críticos (DEBEN SER IGUALES QUE EMISOR)
FS = 44100
FREQ_BASE = 155
FREQ_INCREMENTO = 50
TOLERANCIA = 200         # Tolerancia en Hz para detección
UMBRAL_AMPLITUD = 0.8    # Umbral para detectar señal válida

# Variables de estado
ultimo_caracter = None   # Para evitar repeticiones
mensaje_recibido = []

def encontrar_dispositivo():
    """Muestra dispositivos disponibles y permite seleccionar uno"""
    print("\n--- Dispositivos de audio disponibles ---")
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:  # Solo dispositivos de entrada
            print(f"[{i}] {dev['name']} (Entrada)")
    
    # Permitir selección manual o usar índice 3 por defecto
    device_index = input("\nSelecciona el índice del micrófono a usar [default=3]: ")
    if device_index.strip() == "":
        device_index = 3  # Índice predeterminado
    else:
        device_index = int(device_index)
    
    try:
        sd.check_input_settings(device=device_index, samplerate=FS)
        print(f"\nUsando dispositivo: {devices[device_index]['name']} (índice {device_index})")
        return device_index
    except Exception as e:
        print(f"Error con el dispositivo seleccionado: {e}")
        exit()

def callback(indata, frames, time, status):
    global ultimo_caracter, mensaje_recibido
    
    if status:
        print(status)
    
    data = indata[:, 0]  # Convertir a mono
    bloque = data[:int(FS * 0.2)]  # Bloque de 0.2 segundos
    
    # Aplicar ventana de Hanning
    ventana = np.hanning(len(bloque))
    bloque_ventana = bloque * ventana
    
    # Calcular FFT
    frecuencias = rfftfreq(len(bloque_ventana), d=1/FS)
    magnitudes = np.abs(rfft(bloque_ventana))
    max_mag = np.max(magnitudes)
    
    # Ignorar ruido
    if max_mag < UMBRAL_AMPLITUD:
        return
    
    # Encontrar frecuencia dominante
    freq_detectada = frecuencias[np.argmax(magnitudes)]
    
    # Verificar rango válido
    if not (FREQ_BASE - TOLERANCIA <= freq_detectada <= FREQ_BASE + 255*FREQ_INCREMENTO + TOLERANCIA):
        return
    
    # Decodificar carácter
    codigo_ascii = round((freq_detectada - FREQ_BASE) / FREQ_INCREMENTO)
    caracter = chr(codigo_ascii)
    
    # Filtrar repeticiones temporales
    if caracter == ultimo_caracter:
        return  # Ignorar si es igual al último carácter detectado
    
    # Actualizar estado
    ultimo_caracter = caracter
    mensaje_recibido.append(caracter)
    print(f"Recibido: {caracter} → {freq_detectada:.0f} Hz")

def main():
    device_index = encontrar_dispositivo()
    
    print("\nEscuchando señales ultrasónicas...")
    with sd.InputStream(
        callback=callback,
        channels=1,
        samplerate=FS,
        device=device_index,
        blocksize=1024
    ):
        input("Presiona Enter para detener la recepción...\n")
    
    print("\n--- Transmisión finalizada ---")
    print(f"Mensaje decodificado: {''.join(mensaje_recibido)}")

if __name__ == "__main__":
    main()