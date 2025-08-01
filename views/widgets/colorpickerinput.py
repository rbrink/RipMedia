import tkinter as tk
from tkinter import ttk

class ColorPickerInput(tk.Frame):
    def __init__(self, parent, label='', input_var=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.variable = input_var or tk.StringVar()
        self.label = ttk.Label(self, text=label)
        self.label.pack(side=tk.LEFT, padx=(0, 5))

        self.color_display = tk.Label(self, background=self.variable.get(), width=4, relief=tk.SUNKEN)
        self.color_display.pack(side=tk.LEFT, padx=(0, 5), pady=2)

        self.button = ttk.Button(self, text="Choose", command=self.choose_color)
        self.button.pack(side=tk.LEFT)

    def choose_color(self):
        from tkinter.colorchooser import askcolor
        color_code, hex_code = askcolor(title="Select Color", initialcolor=self.variable.get())
        if hex_code:
            self.variable.set(hex_code)
            self.color_display.config(background=hex_code)

    def get(self):
        return self.variable.get()

    def set(self, value):
        self.variable.set(value)
        self.color_display.config(background=value)
