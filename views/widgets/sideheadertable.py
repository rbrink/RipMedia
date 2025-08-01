import tkinter as tk
from tkinter import ttk

class SideHeaderTable(tk.Frame):
    def __init__(self, parent, headers, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.headers = headers
        self.data_labels = []
        self._build_table()

    def _build_table(self):
        for i, header in enumerate(self.headers):
            # Header on the left
            header_label = ttk.Label(self, text=header, anchor="w", font=("Segoe UI", 10, "bold"))
            header_label.grid(row=i, column=0, sticky="nw", padx=5, pady=2)

            # Empty data cell on the right
            data_label = ttk.Label(self, text="", anchor="w", font=("Segoe UI", 10), wraplength=400)
            data_label.grid(row=i, column=1, sticky="w", padx=5, pady=2)
            self.data_labels.append(data_label)

    def update_data(self, data):
        """
        Update the data column with a list of values.
        :param data: list of strings (same length as headers)
        """
        for i, value in enumerate(data):
            if i < len(self.data_labels):
                self.data_labels[i].config(text=value)
            else:
                break  # Ignore extra data
