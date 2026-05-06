# PixelTone: Image-to-Sound Sonification Tool

PixelTone is a specialized software engine designed to translate **visual data (pixels)** into **acoustic signals (sound waves)**. By mapping 2D image geometry to spectral audio properties, the tool allows users to effectively **"hear"** the visual composition of any digital image.

---

## The Challenge: Visual Noise vs. Auditory Clarity
A standard grayscale image contains **256 levels of brightness** ($n=256$). Directly converting every minute color variation into audio frequencies creates **"white noise"**—a chaotic signal that makes it nearly impossible for the human ear to distinguish shapes, borders, or patterns.

## The Solution: Data Simplification via K-Means Clustering
To ensure a clear and structured audio output, PixelTone leverages **Machine Learning (K-Means Clustering)** to preprocess the image. Instead of sonifying raw, noisy data, the system categorizes pixel intensities into $k$ **dominant clusters** (e.g., $k=4$):

1. **Silence** – (Black / Background)
2. **Quiet** – (Dark Gray / Shadows)
3. **Loud** – (Light Gray / Main Features)
4. **Peak Intensity** – (White / Highlights)

### Technical Benefits:
* **Noise Reduction:** Removes visual artifacts that would otherwise translate into high-frequency static.
* **Auditory Edges:** By grouping pixels into discrete intensity levels, the system creates "contrast", allowing the brain to perceive clear geometric shapes.
* **Efficiency:** Simplifies the mathematical workload before the synthesis engine generates the final waveform.

---

## Sonification Rules (Mapping Logic)
PixelTone follows a strict coordinate-to-audio mapping system:

* **X-Axis (Width) $\rightarrow$ Time:** The image is scanned sequentially from left to right.
* **Y-Axis (Height) $\rightarrow$ Frequency (Pitch):** Pixels at the top generate **High Pitches**, while pixels at the bottom generate **Low Pitches**.
* **Brightness (K-Clusters) $\rightarrow$ Amplitude (Volume):** Higher cluster intensity directly correlates to **Higher Volume (Gain)**.

---

## Application Modes
PixelTone features a versatile graphical interface allowing users to interact with visual data through three distinct modes:

### 1. Global Scan Mode (The Soundscape)
* **Function:** Automatically scans the entire image from left to right over a set duration (e.g., 1 second).
* **Use Case:** Provides an instant, holistic auditory representation of the scene, allowing the user to grasp the general context and large structures through a complex polyphonic soundscape.

### 2. Tactile-Audio Explorer (WASD Mode) (**Work In Progress**)
* **Function:** Transforms the user from a passive listener into an active explorer. Using directional keys (WASD), the user controls a "sonic cursor", hearing only the frequency and amplitude of the specific location they are "touching".
* **Use Case:** Designed as an accessibility and educational tool (e.g., for the visually impaired) to manually trace outlines, understand data charts, and pinpoint precise structural details.

### 3. Sentinel Mode (AI Target Detection) (**Conceptual**)
* **Function:** Integrates deep learning models to actively search for specific target objects or visual anomalies within the image.
* **Use Case:** While scanning globally, if the system's scanline hits a pre-identified target, the audio halts, an auditory alarm is triggered at the target's specific pitch, and a bounding box highlights the area. Might be useful for **hands-free monitoring**.

## Setup
1. Create virtual environment (only once):
```python
   python3 -m venv .venv
```

2. Activate environment:
```python
   source .venv/bin/activate
```

3. Install dependencies:
```python
   pip install -r requirements.txt   
```
## Execution
- VS Code: **Press Ctrl + Shift + B**
- Terminal: python3 src/main.py

## Project Structure
- src/: Source code
- data/: Resources
- .venv/: Python virtual environment (WSL)

## Requirements
- WSL (Ubuntu 22.04)
- Python 3.10+