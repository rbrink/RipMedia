import tkinter as tk
from tkinter import ttk

class ProgressDialog(tk.Toplevel):
    def __init__(self, parent, title="Working...", message="Please wait...",
                 mode="determinate", max_value=100):
        super().__init__(parent)
        self.title(title)
        self.geometry(self.center_geometry(400, 130))
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self._mode = mode

        self.label = ttk.Label(self, text=message)
        self.label.pack(pady=(20,10), padx=10)

        self.progressbar = ttk.Progressbar(self, mode=mode, maximum=100, length=300)
        self.progressbar.pack(pady=(0, 10))

        if mode == "determinate":
            self.progressbar["maximum"] = max_value
            self.progressbar["value"] = 0

        self.btn_cancel = ttk.Button(self, text="Cancel", command=self.close)
        self.btn_cancel.pack(pady=(0, 10))

        self.protocol("WM_DELETE_WINDOW", lambda: None)    # Disable close button

    def update_progress(self, value=None, message=None):
        if message:
            self.label.config(text=message)
        if self._mode == "determinate" and value is not None:
            self.progressbar["value"] = value
        self.update_idletasks()

    def switch_to_determinate(self):
        self.progressbar.stop()
        self.progressbar.config(mode="determinate", value=0)
        self._mode = "determinate"

    def close(self):
        if self._mode == "indeterminate":
            self.progressbar.stop()
        self.grab_release()
        self.destroy()       # Close the dialog

    def center_geometry(self, width, height):
        self.master.update_idletasks()
        root_x, root_y = self.master.winfo_x(), self.master.winfo_y()
        root_w, root_h = self.master.winfo_width(), self.master.winfo_height()
        x = root_x + (root_w - width) // 2
        y = root_y + (root_h - height) // 2
        return f"{width}x{height}+{x}+{y}"
