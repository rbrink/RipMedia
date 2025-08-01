import tkinter as tk
from tkinter import ttk

from data.ripdatabase import RippingDatabase

class RipLibraryWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Rip Library")
        self.geometry("800x400")
        self.create_widgets()

    def create_widgets(self):
        columns = ("Title", "Disc Title", "Output Path", "Ripped At", "Transcoded")
        tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200 if col != "Output Path" else 300)

        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        db = RippingDatabase()
        for row in db.list_recent_rips():
            tree.insert("", tk.END, values=row)
