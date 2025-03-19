# Acoustic Data Transmission System (ADTS)  
**Secure Text Transmission via Audible/Ultrasonic Frequencies**  
![License](https://img.shields.io/badge/License-MIT-green)  

---

## Overview  
The **Acoustic Data Transmission System (ADTS)** enables covert text transmission using frequency-shift keying (FSK) modulation. The system supports both **audible** and **near-ultrasonic** frequency ranges (16-18 kHz) for stealthy communication. Key features:  
- **FSK Modulation**: Maps ASCII characters to unique frequencies.  
- **Real-time processing**: Uses FFT for frequency detection.  
- **Ultrasonic support**: Frequencies inaudible to most humans.  
- **Cross-platform**: Python implementation with minimal dependencies.  

---

## Technical Specifications  
### Core Parameters  
| Parameter             | Value                     | Description                              |
|-----------------------|---------------------------|------------------------------------------|
| Sampling Rate (`FS`)  | 44.1 kHz                  | Nyquist-compliant for ultrasonic ranges |
| Base Frequency (`f₀`) | 16,000 Hz                 | Lower bound of transmission band         |
| Frequency Increment   | 20 Hz/character           | `Δf = 20 Hz` (prevents spectral overlap) |
| Tolerance             | ±50 Hz                    | Robustness against hardware imprecision |
| Symbol Duration       | 200 ms                    | Balances speed and reliability           |

### Mathematical Model  
1. **Frequency Mapping**:  
   Each ASCII character `c` is encoded as:  
   \[
   f_c = f_0 + (\text{ASCII}(c) \times \Delta f)
   \]  
   Example:  
   - "A" (ASCII 65) → \(16000 + 65 \times 20 = 17,300 \text{ Hz}\).

2. **Signal Generation**:  
   Sinusoidal waveform for each character:  
   \[
   s(t) = A \cdot \sin(2\pi f_c t)
   \]  
   where \(A = 0.5\) (amplitude normalized to prevent clipping).

3. **FFT Analysis**:  
   Frequency detection via:  
   \[
   \text{FFT}\{s(t)\} \rightarrow \text{argmax}(|S(f)|)
   \]  
   with a Hanning window to minimize spectral leakage.

---

## Implementation Details  

### Directory Structure  

├── emitter.py # Frequency generator/transmitter
├── receiver.py # Signal capture and decoder
├── requirements.txt # Dependencies
└── examples/ # Test WAV files


### Dependencies  

- Python 3.8+  
- `numpy`, `scipy`, `sounddevice`  
Install via:  
```bash
pip install -r requirements.txt
```

# Hardware Considerations

## Ultrasonic Transmission :

Requires microphones/speakers with >20 kHz bandwidth (e.g., MEMS microphones, ultrasonic transducers).

## Audible Mode :
Standard audio interfaces (16-bit, 44.1/48 kHz) suffice.

## Mathematical Validation

![image](https://github.com/user-attachments/assets/1db00ae6-5912-4fa8-a444-39cf74cb62e6)

Nyquist-Shannon Sampling Theorem
To avoid aliasing:
BW=255×Δf=5,100 Hz (compact spectral footprint)

![image](https://github.com/user-attachments/assets/3ed6730e-1ab8-4fa7-b4ec-5e03ce8a77be)


## Main trasmitir y recibir 

Usan otro sistema de codificacion mucho mejor 
Sí, el código que te he proporcionado está configurado para usar dos frecuencias diferentes, lo que se conoce como Frequency-Shift Keying (FSK). Esto es, en esencia, usar dos "canales" de comunicación, aunque no son canales físicos separados, sino frecuencias distintas dentro del mismo medio (el aire, en este caso).

FREQ_0 = 1000 Hz: Esta frecuencia representa el bit '0'.

FREQ_1 = 2000 Hz: Esta frecuencia representa el bit '1'.

Por qué FSK (y, por tanto, dos frecuencias):

FSK es una técnica mucho más robusta que simplemente usar la presencia o ausencia de un tono (lo que sería equivalente a usar una sola frecuencia). Aquí están las ventajas clave de FSK:

Mayor Resistencia al Ruido: Si usaras una sola frecuencia (por ejemplo, 1000 Hz) para representar un '1' y silencio para representar un '0', cualquier ruido ambiental que contenga la frecuencia de 1000 Hz podría interpretarse erróneamente como un '1'. Con FSK, el receptor busca dos frecuencias específicas. Es mucho menos probable que el ruido ambiental contenga ambas frecuencias exactamente al mismo tiempo y con la amplitud suficiente para superar el umbral (THRESHOLD).

Detección Más Fiable: Con FSK, el receptor siempre está "escuchando" algo. No tiene que distinguir entre un tono y silencio absoluto, lo cual puede ser difícil en la práctica debido al ruido de fondo. El receptor simplemente tiene que decidir cuál de las dos frecuencias (FREQ_0 o FREQ_1) es más fuerte en un momento dado.

Sincronización Más Sencilla: La transición entre las dos frecuencias (de FREQ_0 a FREQ_1 o viceversa) ayuda a mantener la sincronización entre el transmisor y el receptor. Cada vez que hay un cambio de frecuencia, el receptor sabe que ha comenzado un nuevo bit.

Cómo Funciona en el Código:

transmitir.py:

La función generar_tono crea una onda sinusoidal de la frecuencia especificada.

En generar_senal, cuando se va a enviar un bit '1', se llama a generar_tono con FREQ_1.

Cuando se va a enviar un bit '0', se llama a generar_tono con FREQ_0.

recibir.py:

La función detectar_tono utiliza la Transformada Rápida de Fourier (FFT) para analizar el audio entrante y determinar la amplitud de las diferentes frecuencias.

En iniciar_recepcion, se llama a detectar_tono dos veces en cada ciclo del bucle de decodificación: una vez para comprobar la presencia de FREQ_1 y otra para comprobar la presencia de FREQ_0. El bit que se decodifica ('1' o '0') depende de cuál de las dos frecuencias tenga una amplitud mayor (por encima del THRESHOLD).
 

## Contributing
Bug Reports : Open an issue with FFT snapshots and hardware specs.
Enhancements : Propose DSP optimizations (e.g., Goertzel algorithm).
Hardware Tests : Share results with piezoelectric transducers.

Victor Arbiol
