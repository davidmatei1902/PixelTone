import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from engine_audio import AudioEngine

# setup global appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PixelToneApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # init the audio engine
        self.audio_engine = AudioEngine()
        
        # variable to store the currently loaded image path
        self.current_image_path = None

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

        # mode 2 button
        self.btn_wasd = ctk.CTkButton(self.sidebar, text="2. WASD Explorer", command=self.run_wasd_explorer)
        self.btn_wasd.grid(row=2, column=0, padx=20, pady=10)

        # mode 3 button
        self.btn_sentinel = ctk.CTkButton(self.sidebar, text="3. Sentinel Mode", fg_color="#8B0000", hover_color="#FF0000", command=self.run_sentinel)
        self.btn_sentinel.grid(row=3, column=0, padx=20, pady=10)

        # load image button connected to load image function
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

    # file explorer dialog and image rendering
    def load_image(self):
        # open file dialog to select image
        file_path = filedialog.askopenfilename(
            title="select an image",
            filetypes=[("image files", "*.png *.jpg *.jpeg")]
        )
        
        if file_path:
            self.current_image_path = file_path
            print(f"loaded image: {self.current_image_path}")
            
            # load and display image on gui
            pil_image = Image.open(self.current_image_path)
            
            # create a customtkinter image object
            ctk_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(400, 400))
            
            # update the label with the image and remove the placeholder text
            self.img_placeholder.configure(image=ctk_img, text="")

    # functions for mode buttons
    def run_global_scan(self):
        if self.current_image_path:
            print(f"starting global soundscape for {self.current_image_path}...")
            # trigger engine with the dynamically loaded image
            self.audio_engine.generate_soundscape(self.current_image_path)
        else:
            print("warning: please load an image first!")

    def run_wasd_explorer(self):
        print("wasd mode active. cursor ready.")

    def run_sentinel(self):
        print("sentinel armed. ai target detection running...")

    # key press handlers
    def move_up(self, event):
        print("cursor moved up")

    def move_down(self, event):
        print("cursor moved down")

    def move_left(self, event):
        print("cursor moved left")

    def move_right(self, event):
        print("cursor moved right")