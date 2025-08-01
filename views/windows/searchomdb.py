import tkinter as tk
from tkinter import ttk, messagebox

from utils import Logger
from modules.api.omdb import omdb_api

class SearchDialog(tk.Toplevel):
    def __init__(self, parent, initial_title="", *args, **kwargs):
        super().__init__(parent)
        self.title("Search OMDB")
        self.geometry(self.center_geometry(500, 400))
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.logger = Logger.get_logger(__name__)
        self.result = None

        ttk.Label(self, text="Search for a series or a movie:").pack(pady=(10, 2))
        self.entry = ttk.Entry(self, width=50)
        self.entry.insert(0, initial_title)
        self.entry.bind("<Return>", lambda e: self.perform_search())
        self.entry.pack(pady=5)
        self.entry.focus()

        ttk.Button(self, text="Search", command=self.perform_search).pack()

        self.listbox = tk.Listbox(self, width=70, height=10)
        self.listbox.pack(padx=10, pady=10, fill="both", expand=True)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Select", command=self.select_entry).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

        self.results = []

        self.wait_window()
    
    def perform_search(self):
        query = self.entry.get().strip()
        if not query:
            return
        self.results = omdb_api().search_omdb(query)
        self.listbox.delete(0, tk.END)
        if not self.results:
            self.logger.info(f"No Results: No OMDB results found for '{query}'.")
            messagebox.showinfo(title=f"Info", message=f"No OMDB results for '{query}'.")
            return
        for item in self.results:
            line = f"{item['Title']} ({item['Year']}) - {item['Type'].capitalize()}"
            self.listbox.insert(tk.END, line)

    def select_entry(self):
        sel = self.listbox.curselection()
        if not sel:
            self.logger.warning(f"No Selection: Please select an item")
            messagebox.showwarning("Warning", "Please select an item")
            return
        self.result = self.results[sel[0]]
        self.destroy()
    
    def center_geometry(self, width, height):
        self.master.update_idletasks()
        root_x, root_y = self.master.winfo_x(), self.master.winfo_y()
        root_w, root_h = self.master.winfo_width(), self.master.winfo_height()
        x = root_x + (root_w - width) // 2
        y = root_y + (root_h - height) // 2
        return f"{width}x{height}+{x}+{y}"
