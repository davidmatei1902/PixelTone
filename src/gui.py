import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw
import cv2
import os
import numpy as np
from engine_audio import AudioEngine
from engine_vision import VisionEngine

class PixelToneApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # init the audio engine
        self.audio_engine = AudioEngine()
        
        # init the vision engine
        self.vision_engine = VisionEngine()
        
        # variables for image and mode state
        self.current_image_path = None
        self.wasd_active = False
        self.cursor_x = 0
        self.cursor_y = 0
        
        # matrices for logic
        self.raw_img_data = None    
        self.kmeans_img_data = None 
        self.img_data = None        
        
        # images for visual rendering
        self.pil_rgb_display = None    
        self.pil_gray_display = None   
        self.pil_kmeans_display = None 
        self.pil_img_original = None   
        
        # scale factors mapping real matrix coords to 400x400 visual box
        self.scale_x = 1.0
        self.scale_y = 1.0

        # variables for throttling inputs (fixing lag)
        self.input_dirty = False 
        self.update_interval_ms = 30 
        self.is_app_running = True 

        # configure main window
        self.title("PixelTone - Sensory Substitution")
        self.geometry("900x650")

        # configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # create sidebar frame for controls
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)

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

        # ui separator
        self.separator = ctk.CTkFrame(self.sidebar, height=2, fg_color="gray50")
        self.separator.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        # grayscale toggle
        self.switch_gray = ctk.CTkSwitch(self.sidebar, text="Grayscale Mode", command=self.refresh_display_logic, state="disabled")
        self.switch_gray.grid(row=5, column=0, padx=20, pady=10)

        # apply kmeans button (hidden initially)
        self.btn_apply_kmeans = ctk.CTkButton(self.sidebar, text="Apply K-Means", command=self.process_kmeans)
        self.btn_apply_kmeans.grid(row=6, column=0, padx=20, pady=10)
        self.btn_apply_kmeans.grid_remove()

        # kmeans toggle
        self.switch_kmeans = ctk.CTkSwitch(self.sidebar, text="K-Means Filter", command=self.refresh_display_logic)
        self.switch_kmeans.grid(row=7, column=0, padx=20, pady=10)
        self.switch_kmeans.grid_remove() 

        # load image button
        self.btn_load = ctk.CTkButton(self.sidebar, text="Load Image...", fg_color="transparent", border_width=2, command=self.load_image)
        self.btn_load.grid(row=9, column=0, padx=20, pady=20, sticky="s")

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

        # start the background throttled process loop
        self.after(self.update_interval_ms, self.throttled_process_loop)

    def stop_application(self):
        # stop background loop on exit
        self.is_app_running = False

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="select an image",
            filetypes=[("image files", "*.png *.jpg *.jpeg")]
        )
        
        if file_path:
            self.current_image_path = file_path
            
            # reset kmeans data for the new image
            self.kmeans_img_data = None
            
            # store rgb original
            raw_rgb_pil = Image.open(self.current_image_path).convert("RGB")
            self.pil_rgb_display = raw_rgb_pil.resize((400, 400), Image.Resampling.LANCZOS)
            
            # store grayscale data and visual
            self.raw_img_data = cv2.imread(self.current_image_path, cv2.IMREAD_GRAYSCALE)
            
            if self.raw_img_data is not None:
                # generate visual gray version
                gray_rgb = cv2.cvtColor(self.raw_img_data, cv2.COLOR_GRAY2RGB)
                self.pil_gray_display = Image.fromarray(gray_rgb).resize((400, 400), Image.Resampling.LANCZOS)

                # reset cursor to center of matrix
                self.cursor_y, self.cursor_x = self.raw_img_data.shape[0] // 2, self.raw_img_data.shape[1] // 2
                
                # calculate scale factors
                self.scale_y = 400 / self.raw_img_data.shape[0]
                self.scale_x = 400 / self.raw_img_data.shape[1]
                
                # reset modes
                self.wasd_active = False
                self.btn_wasd.configure(fg_color=["#3B8ED0", "#1F6AA5"])
                
                # enable grayscale switch and hide kmeans switch initially
                self.switch_gray.configure(state="normal")
                self.switch_gray.deselect()
                
                self.switch_kmeans.deselect()
                self.switch_kmeans.grid_remove() 
                
                # hide apply kmeans button initially (shown only when grayscale is on)
                self.btn_apply_kmeans.grid_remove()
                
                self.refresh_display_logic()
            
            print(f"loaded image: {self.current_image_path} | res: {self.raw_img_data.shape}")

    def process_kmeans(self):
        if self.raw_img_data is not None:
            # use the vision engine to apply ai
            self.kmeans_img_data = self.vision_engine.apply_kmeans(self.raw_img_data, k=4)
            
            # create visual display
            km_rgb = cv2.cvtColor(self.kmeans_img_data, cv2.COLOR_GRAY2RGB)
            self.pil_kmeans_display = Image.fromarray(km_rgb).resize((400, 400), Image.Resampling.NEAREST)
            
            # hide apply button, show switch and turn it on
            self.btn_apply_kmeans.grid_remove()
            self.switch_kmeans.grid(row=7, column=0, padx=20, pady=10)
            self.switch_kmeans.select()
            
            self.refresh_display_logic()

    def refresh_display_logic(self):
        # if grayscale is on, manage kmeans ui
        if self.switch_gray.get() == 1:
            if self.kmeans_img_data is None:
                # show apply button if ai has not processed the image yet
                self.btn_apply_kmeans.grid(row=6, column=0, padx=20, pady=10)
                self.switch_kmeans.grid_remove()
                
                self.img_data = self.raw_img_data
                self.pil_img_original = self.pil_gray_display
            else:
                # hide apply button and show switch if ai has already processed
                self.btn_apply_kmeans.grid_remove()
                self.switch_kmeans.grid(row=7, column=0, padx=20, pady=10)
                
                if self.switch_kmeans.get() == 1:
                    self.img_data = self.kmeans_img_data
                    self.pil_img_original = self.pil_kmeans_display
                else:
                    self.img_data = self.raw_img_data
                    self.pil_img_original = self.pil_gray_display
        else:
            # if grayscale is off, hide both kmeans buttons and revert to original rgb
            self.btn_apply_kmeans.grid_remove()
            self.switch_kmeans.grid_remove()
            
            self.img_data = self.raw_img_data
            self.pil_img_original = self.pil_rgb_display
            
        self.update_visual_cursor()

    def update_visual_cursor(self):
        # draw visuals without lag
        if self.pil_img_original is not None:
            temp_img = self.pil_img_original.copy()
            
            # only draw the red cursor if wasd mode is on
            if self.wasd_active:
                draw = ImageDraw.Draw(temp_img)
                r = 10 
                gui_x = int(self.cursor_x * self.scale_x)
                gui_y = int(self.cursor_y * self.scale_y)
                
                left_up = (gui_x - r, gui_y - r)
                right_down = (gui_x + r, gui_y + r)
                
                # draw cursor
                draw.ellipse([left_up, right_down], fill="red", outline="white", width=4)
            
            # update gui directly using the pre-sized image
            ctk_img = ctk.CTkImage(light_image=temp_img, dark_image=temp_img, size=(400, 400))
            self.img_placeholder.configure(image=ctk_img, text="")

    def run_global_scan(self):
        if self.current_image_path:
            self.audio_engine.generate_soundscape(self.current_image_path)
            messagebox.showinfo("success", "global scan complete!")
        else:
            messagebox.showwarning("warning", "load an image first!")

    def run_wasd_explorer(self):
        if self.raw_img_data is None:
            messagebox.showwarning("warning", "load an image first!")
            return
            
        self.wasd_active = not self.wasd_active
        color = "green" if self.wasd_active else ["#3B8ED0", "#1F6AA5"] 
        self.btn_wasd.configure(fg_color=color)
        
        # immediately trigger redraw to show/hide cursor based on new state
        self.update_visual_cursor()

    def throttled_process_loop(self):
        if not self.is_app_running:
            return 

        if self.wasd_active and self.img_data is not None and self.input_dirty:
            self.do_process_and_draw()
            self.input_dirty = False 

        self.after(self.update_interval_ms, self.throttled_process_loop)

    def do_process_and_draw(self):
        brightness = self.img_data[self.cursor_y, self.cursor_x] / 255.0
        self.audio_engine.play_pixel_tone(brightness, self.cursor_y, self.img_data.shape[0])
        self.update_visual_cursor()

    def update_cursor_state(self, dx, dy):
        if self.wasd_active and self.raw_img_data is not None:
            # dynamic step size based on image resolution
            step_x = max(10, int(self.raw_img_data.shape[1] * 0.02))
            step_y = max(10, int(self.raw_img_data.shape[0] * 0.02))
            
            new_x = self.cursor_x + (dx * step_x)
            new_y = self.cursor_y + (dy * step_y)

            # verify boundaries and notify if out of bounds
            is_out_of_bounds = False
            if dy == -1 and self.cursor_y <= 0: is_out_of_bounds = True 
            if dy == 1 and self.cursor_y >= self.raw_img_data.shape[0] - 1: is_out_of_bounds = True 
            if dx == -1 and self.cursor_x <= 0: is_out_of_bounds = True 
            if dx == 1 and self.cursor_x >= self.raw_img_data.shape[1] - 1: is_out_of_bounds = True 

            if is_out_of_bounds:
                # play distinct border sound
                self.audio_engine.play_border_notification()
                return 

            # limit boundaries to avoid crashing
            if new_y >= 0 and new_y < self.raw_img_data.shape[0] and \
               new_x >= 0 and new_x < self.raw_img_data.shape[1]:
                self.cursor_x = new_x
                self.cursor_y = new_y
                self.input_dirty = True 

    def move_up(self, event):
        self.update_cursor_state(0, -1) 

    def move_down(self, event):
        self.update_cursor_state(0, 1)

    def move_left(self, event):
        self.update_cursor_state(-1, 0)

    def move_right(self, event):
        self.update_cursor_state(1, 0)

    def run_sentinel(self):
        print("sentinel mode not implemented yet.")