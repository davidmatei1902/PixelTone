import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw
import cv2
import os
from engine_audio import AudioEngine

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
        self.img_data = None # stores the original grayscale matrix
        self.pil_img_original = None # stores PRE-RESIZED rgb image for fast drawing
        
        # scale factors mapping real matrix coords to 400x400 visual box
        self.scale_x = 1.0
        self.scale_y = 1.0

        # variables for throttling inputs (fixing lag)
        self.input_dirty = False 
        self.update_interval_ms = 30 # runs at ~30 fps max
        self.is_app_running = True 

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
            
            # load raw image for logic
            self.img_data = cv2.imread(self.current_image_path, cv2.IMREAD_GRAYSCALE)
            
            if self.img_data is not None:
                # reset cursor to center of matrix
                self.cursor_y, self.cursor_x = self.img_data.shape[0] // 2, self.img_data.shape[1] // 2
                
                # pre-resize visual image to exactly 400x400 so copying it is instant
                raw_pil = Image.open(self.current_image_path).convert("RGB")
                self.pil_img_original = raw_pil.resize((400, 400), Image.Resampling.LANCZOS)
                
                # calculate scale factors to sync real coordinates with visual coordinates
                self.scale_y = 400 / self.img_data.shape[0]
                self.scale_x = 400 / self.img_data.shape[1]
                
                # ensure WASD is OFF when a new image is loaded
                self.wasd_active = False
                self.btn_wasd.configure(fg_color=["#3B8ED0", "#1F6AA5"])
                
                # draw pure image (cursor is hidden because wasd is off)
                self.update_visual_cursor()
            
            print(f"loaded image: {self.current_image_path} | res: {self.img_data.shape}")

    def update_visual_cursor(self):
        # draw visuals without lag
        if self.pil_img_original is not None:
            temp_img = self.pil_img_original.copy()
            
            # only draw the red cursor if WASD mode is ON
            if self.wasd_active:
                draw = ImageDraw.Draw(temp_img)
                
                r = 10 # radius
                
                # apply scale to draw cursor at correct visual spot
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
        if self.img_data is None:
            messagebox.showwarning("warning", "load an image first!")
            return
        
        self.wasd_active = not self.wasd_active
        color = "green" if self.wasd_active else ["#3B8ED0", "#1F6AA5"] 
        self.btn_wasd.configure(fg_color=color)
        print(f"wasd mode: {'ON' if self.wasd_active else 'OFF'}")
        
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
        print(f"cursor at Y:{self.cursor_y} X:{self.cursor_x} | brightness: {brightness:.2f}")

    def update_cursor_state(self, dx, dy):
        if self.wasd_active and self.img_data is not None:
            # dynamic step size based on image resolution (e.g., 2% of image width per step)
            step_x = max(10, int(self.img_data.shape[1] * 0.02))
            step_y = max(10, int(self.img_data.shape[0] * 0.02))
            
            new_x = self.cursor_x + (dx * step_x)
            new_y = self.cursor_y + (dy * step_y)

            # limit boundaries to avoid crashing
            if new_y >= 0 and new_y < self.img_data.shape[0] and \
               new_x >= 0 and new_x < self.img_data.shape[1]:
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