import cv2
import numpy as np
from scipy.io import wavfile
import os

class AudioEngine:
    def __init__(self):
        # safety ceiling for 16 bit audio
        self.sound_ceiling = 30000
        self.sample_rate = 44100
        self.output_dir = "output/audio"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_soundscape(self, input_path):
        file_name = os.path.splitext(os.path.basename(input_path))[0]
        
        # load and process image
        image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            print(f"error: could not find image at {input_path}")
            return

        # resize for consistent processing speed
        image = cv2.resize(image, (50, 50))

        total_scan_duration = 1.0  
        samples_per_col = int(self.sample_rate * (total_scan_duration / image.shape[1]))

        # logarithmic frequency mapping
        freqs = np.geomspace(2000, 200, image.shape[0]) 

        # generate random start phase for each row to avoid robotic distortion
        phases = np.random.uniform(0, 2 * np.pi, image.shape[0])

        audio_buffer = []
        current_time = 0.0

        print(f"processing {file_name} as a full soundscape...")

        # core algorithm scanning left to right
        for x in range(image.shape[1]):
            column_signal = np.zeros(samples_per_col)
            t = np.linspace(current_time, current_time + (total_scan_duration / image.shape[1]), samples_per_col, endpoint=False)
            current_time += total_scan_duration / image.shape[1]
            
            # overlay sound for each pixel in the current column
            for y in range(image.shape[0]):
                brightness = image[y, x] / 255.0
                
                if brightness > 0.01:
                    selected_freq = freqs[y]
                    # add phase offset to the formula
                    pixel_tone = (brightness / image.shape[0]) * np.sin(2 * np.pi * selected_freq * t + phases[y])
                    column_signal += pixel_tone
                    
            # append column signal to buffer
            audio_buffer.append(column_signal)

        # combine all columns into a single signal
        audio_output = np.concatenate(audio_buffer)

        # apply global fade window at the ends
        fade_samples = int(self.sample_rate * 0.05)
        global_window = np.ones(len(audio_output))
        global_window[:fade_samples] = np.linspace(0, 1, fade_samples)
        global_window[-fade_samples:] = np.linspace(1, 0, fade_samples)

        audio_output = audio_output * global_window

        # convert to 16 bit pcm
        audio_final = (audio_output * self.sound_ceiling).astype(np.int16)

        # save dynamic filename
        output_filename = os.path.join(self.output_dir, f"{file_name}_sonified.wav")
        wavfile.write(output_filename, self.sample_rate, audio_final)

        print(f"saved crisp soundscape: {output_filename}")