import cv2
import numpy as np
from scipy.io import wavfile
import os

# macros & constants
# 32767 is the limit for 16-bit audio, 30000 is used as a safety ceiling
SOUND_CEILING = 30000 

# setup paths
input_path = "data/png/primitives/square_white.png"
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
total_scan_duration = 1.0  # full second duration (vOICe standard)
samples_per_col = int(sample_rate * (total_scan_duration / image.shape[1]))
t = np.linspace(0, total_scan_duration / image.shape[1], samples_per_col, endpoint=False)

# generate frequency range: top pixels (y=0) are high pitch, bottom pixels (y=49) are low pitch
# 50 frequencies for the 50 rows of the image
freqs = np.linspace(2000, 200, image.shape[0]) 

# create a 5ms fade envelope to prevent clicking between columns
fade_samples = int(sample_rate * 0.005)
window = np.ones(samples_per_col)
if samples_per_col > 2 * fade_samples:
    fade_curve = np.linspace(0, 1, fade_samples)
    window[:fade_samples] = fade_curve
    window[-fade_samples:] = fade_curve[::-1]

audio_buffer = []

print(f"processing {file_name} as a full soundscape...")

# core algorithm
# ScanX: time moves from left to right
for x in range(image.shape[1]):
    column_signal = np.zeros(samples_per_col)
    
    # ScanY: overlay sound for each pixel in the current column
    for y in range(image.shape[0]):
        brightness = image[y, x] / 255.0
        
        if brightness > 0.01:  # ignore near-black pixels
            # frequency depends on Y position
            selected_freq = freqs[y]
            
            # amplitude depends on brightness
            # add the pixel's sine wave to the column signal
            pixel_tone = (brightness / image.shape[0]) * np.sin(2 * np.pi * selected_freq * t)
            column_signal += pixel_tone
            
    # apply fade window and add to final buffer
    audio_buffer.append(column_signal * window)

# combine all columns into a single signal
audio_output = np.concatenate(audio_buffer)

# normalization & saving
# essential: volume can exceed limits when overlaying 50 rows
# max_val = np.max(np.abs(audio_output))
# if max_val > 0:
#     audio_output = audio_output / max_val

# convert to 16-bit pcm
audio_final = (audio_output * SOUND_CEILING).astype(np.int16)
output_filename = os.path.join(output_dir, f"{file_name}_sonified.wav")
wavfile.write(output_filename, sample_rate, audio_final)

print(f"saved soundscape: {output_filename}")