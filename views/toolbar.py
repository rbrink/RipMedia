import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class ToolBar(tk.Frame):
    def __init__(self, parent, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.callbacks = callbacks
        self.btn_images = {
            "load_dvd": ImageTk.PhotoImage(Image.open("assets/images/.png/disc-blue (32x32).png")),
            "load_iso": ImageTk.PhotoImage(Image.open("assets/images/.png/iso_img (32x32).png")),
            "load_cd": ImageTk.PhotoImage(Image.open("assets/images/.png/music (32x32).png")),
            "rip_library": ImageTk.PhotoImage(Image.open("assets/images/.png/database (32x32).png")),
            "preferences": ImageTk.PhotoImage(Image.open("assets/images/.png/preferences (32x32).png")),
            "transcode": ImageTk.PhotoImage(Image.open("assets/images/.png/transcode (32x32).png")),
            "start_rip": ImageTk.PhotoImage(Image.open("assets/images/.png/start (32x32).png")),
            "stop_rip": ImageTk.PhotoImage(Image.open("assets/images/.png/stop (32x32).png"))
        }
        self.create_widgets()
    
    def create_widgets(self):
        self.load_disc = ttk.Button(self, text="Load DVD", image=self.btn_images['load_dvd'], compound=tk.LEFT,
                   command=self.callbacks["file -> load_dvd"])
        self.load_disc.pack(side=tk.LEFT, padx=2, pady=2)
        self.load_iso = ttk.Button(self, text="Load ISO", image=self.btn_images['load_iso'], compound=tk.LEFT,
                   command=self.callbacks["file -> load_iso"])
        self.load_iso.pack(side=tk.LEFT, padx=2, pady=2)
        self.load_cd = ttk.Button(self, text="Load CD", image=self.btn_images['load_cd'], compound=tk.LEFT,
                   command=self.callbacks["file -> load_cd"])
        self.load_cd.pack(side=tk.LEFT, padx=2, pady=2)
        self.btn_rip = ttk.Button(self, text="Start", image=self.btn_images['start_rip'], compound=tk.LEFT,
                   command=self.callbacks['rip -> start_rip'], state=tk.DISABLED)
        self.btn_rip.pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(self, text="Rip History", image=self.btn_images['rip_library'], compound=tk.LEFT,
                   command=self.callbacks["tools -> history"]).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(self, text="Preferences", image=self.btn_images['preferences'], compound=tk.LEFT,
                   command=self.callbacks["tools -> preferences"]).pack(side=tk.LEFT, padx=2, pady=2)
