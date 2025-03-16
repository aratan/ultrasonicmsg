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


Hardware Considerations
Ultrasonic Transmission :
Requires microphones/speakers with >20 kHz bandwidth (e.g., MEMS microphones, ultrasonic transducers).
Audible Mode :
Standard audio interfaces (16-bit, 44.1/48 kHz) suffice.
Mathematical Validation
Nyquist-Shannon Sampling Theorem
To avoid aliasing:
BW=255×Δf=5,100 Hz (compact spectral footprint)



Contributing
Bug Reports : Open an issue with FFT snapshots and hardware specs.
Enhancements : Propose DSP optimizations (e.g., Goertzel algorithm).
Hardware Tests : Share results with piezoelectric transducers.