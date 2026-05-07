import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import cv2
import os
from engine_audio import AudioEngine

# setup global appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PixelToneApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # init the audio engine
        self.audio_engine = AudioEngine()
        
        # variables for image and mode state
        self.current_image_path = None
        self.wasd_active = False
        self.cursor_x = 0
        self.cursor_y = 0
        self.img_data = None # stores the grayscale matrix

        # configure main window
        self.title("PixelTone - Sensory Substitution")
        self.geometry("900x600")

        # configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # create sidebar frame for controls
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)

        # application title label
        self.logo_label = ctk.CTkLabel(self.sidebar, text="PixelTone", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        # mode 1 button
        self.btn_scan = ctk.CTkButton(self.sidebar, text="1. Global Scan", command=self.run_global_scan)
        self.btn_scan.grid(row=1, column=0, padx=20, pady=10)

        # mode 2 button (wasd toggle)
        self.btn_wasd = ctk.CTkButton(self.sidebar, text="2. WASD Explorer", command=self.run_wasd_explorer)
        self.btn_wasd.grid(row=2, column=0, padx=20, pady=10)

        # mode 3 button
        self.btn_sentinel = ctk.CTkButton(self.sidebar, text="3. Sentinel Mode", fg_color="#8B0000", hover_color="#FF0000", command=self.run_sentinel)
        self.btn_sentinel.grid(row=3, column=0, padx=20, pady=10)

        # load image button
        self.btn_load = ctk.CTkButton(self.sidebar, text="Load Image...", fg_color="transparent", border_width=2, command=self.load_image)
        self.btn_load.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # create main frame for image display
        self.image_area = ctk.CTkFrame(self)
        self.image_area.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # placeholder for the actual image
        self.img_placeholder = ctk.CTkLabel(self.image_area, text="No Image Loaded\n\nUse WASD to test keys", font=ctk.CTkFont(size=18))
        self.img_placeholder.pack(expand=True, fill="both")

        # bind wasd keys to the application
        self.bind("<w>", self.move_up)
        self.bind("<a>", self.move_left)
        self.bind("<s>", self.move_down)
        self.bind("<d>", self.move_right)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="select an image",
            filetypes=[("image files", "*.png *.jpg *.jpeg")]
        )
        
        if file_path:
            self.current_image_path = file_path
            # load image for cv2 processing (grayscale)
            self.img_data = cv2.imread(self.current_image_path, cv2.IMREAD_GRAYSCALE)
            
            # reset cursor to image center
            if self.img_data is not None:
                self.cursor_y, self.cursor_x = self.img_data.shape[0] // 2, self.img_data.shape[1] // 2
            
            # display in gui
            pil_image = Image.open(self.current_image_path)
            ctk_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(400, 400))
            self.img_placeholder.configure(image=ctk_img, text="")
            print(f"loaded image: {self.current_image_path} | res: {self.img_data.shape}")

    def run_global_scan(self):
        if self.current_image_path:
            self.audio_engine.generate_soundscape(self.current_image_path)
            messagebox.showinfo("success", "global scan complete!")
        else:
            messagebox.showwarning("warning", "load an image first!")

    def run_wasd_explorer(self):
        if self.img_data is None:
            messagebox.showwarning("warning", "load an image first!")
            return
        
        self.wasd_active = not self.wasd_active
        color = "green" if self.wasd_active else ["#3B8ED0", "#1F6AA5"] # default ctk blue
        self.btn_wasd.configure(fg_color=color)
        print(f"wasd mode: {'ON' if self.wasd_active else 'OFF'}")

    def process_pixel_step(self):
        """helper to get brightness and trigger sound engine"""
        if self.wasd_active and self.img_data is not None:
            # get pixel brightness (0-1)
            brightness = self.img_data[self.cursor_y, self.cursor_x] / 255.0
            # send to engine (brightness, current_y, total_height)
            self.audio_engine.play_pixel_tone(brightness, self.cursor_y, self.img_data.shape[0])
            # print for debugging
            print(f"cursor at Y:{self.cursor_y} X:{self.cursor_x} | brightness: {brightness:.2f}")

    def move_up(self, event):
        if self.wasd_active and self.img_data is not None:
            if self.cursor_y > 10:
                self.cursor_y -= 10
                self.process_pixel_step()

    def move_down(self, event):
        if self.wasd_active and self.img_data is not None:
            if self.cursor_y < self.img_data.shape[0] - 11:
                self.cursor_y += 10
                self.process_pixel_step()

    def move_left(self, event):
        if self.wasd_active and self.img_data is not None:
            if self.cursor_x > 10:
                self.cursor_x -= 10
                self.process_pixel_step()

    def move_right(self, event):
        if self.wasd_active and self.img_data is not None:
            if self.cursor_x < self.img_data.shape[1] - 11:
                self.cursor_x += 10
                self.process_pixel_step()

    def run_sentinel(self):
        print("sentinel mode not implemented yet.")