import cv2
import numpy as np
from scipy.io import wavfile
import os

# --- macros & constants ---
# 32767 is the limit for 16-bit audio, we use 30000 as a "safety ceiling"
SOUND_CEILING = 30000 

# musical notes and their frequencies
notes = {
    "C4": 261.63, # do
    "D4": 293.66, # re
    "E4": 329.63, # mi
    "F4": 349.23, # fa
    "G4": 392.00, # sol
    "A4": 440.00, # la
    "B4": 493.88  # si
}

# setup paths
input_path = "data/png/primitives/triangle.png"
file_name = os.path.splitext(os.path.basename(input_path))[0]
output_dir = "output/audio"
os.makedirs(output_dir, exist_ok=True)

# load and process image
image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)

if image is None:
    print(f"error: could not find image at {input_path}")
    exit(1)

# resize for consistent processing speed
image = cv2.resize(image, (50, 50))

# audio parameters
sample_rate = 44100
duration = 0.1
samples_per_col = int(sample_rate * duration)
t = np.linspace(0, duration, samples_per_col, endpoint=False)

# list of notes to generate
target_notes = ["A4", "D4"]

for note_name in target_notes:
    selected_freq = notes[note_name]
    
    # generate base sine wave
    base_sine = np.sin(2 * np.pi * selected_freq * t)
    
    # create a 5ms fade envelope to prevent clicking/clipping between columns
    window = np.ones(samples_per_col)
    fade_samples = int(sample_rate * 0.005) 
    fade_curve = np.linspace(0, 1, fade_samples)
    window[:fade_samples] = fade_curve
    window[-fade_samples:] = fade_curve[::-1]
    
    smoothed_base = base_sine * window
    audio_buffer = []

    print(f"processing {file_name} with note {note_name}...")

    # scan columns: X = Time, Brightness = Volume
    for x in range(image.shape[1]):
        brightness = np.mean(image[:, x]) / 255.0
        tone = brightness * smoothed_base
        audio_buffer.append(tone)

    # combine all columns
    audio_output = np.concatenate(audio_buffer)

    # normalization: find peak and scale to fit our ceiling
    max_val = np.max(np.abs(audio_output))
    if max_val > 0:
        audio_output = audio_output / max_val
    
    # apply the macro: convert to 16-bit pcm
    audio_final = (audio_output * SOUND_CEILING).astype(np.int16)

    # save file
    output_filename = os.path.join(output_dir, f"{file_name}_{note_name.lower()}.wav")
    wavfile.write(output_filename, sample_rate, audio_final)
    
    print(f"saved clear file: {output_filename}")

print("\ndone! everything sounds smooth now.")