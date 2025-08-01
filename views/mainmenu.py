import tkinter as tk
from tkinter import messagebox

class MainMenu(tk.Menu):
    def __init__(self, parent, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.create_menu(callbacks)

    def create_menu(self, callbacks):
        # Create the File menu
        file_menu = tk.Menu(self, tearoff=0)
        file_menu.add_command(label="Load DVD", command=callbacks["file -> load_dvd"])
        file_menu.add_command(label="Load Music CD", command=callbacks["file -> load_cd"])
        file_menu.add_command(label="Load ISO", command=callbacks["file -> load_iso"])
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        
        # Create the Edit Menu
        edit_menu = tk.Menu(self, tearoff=0)
        edit_menu.add_command(label="Edit Metadata", command=callbacks["edit -> edit_metadata"])
        edit_menu.add_command(label="Edit Titles", command=callbacks["edit -> edit_titles"])

        # Create the Tools menu
        tools_menu = tk.Menu(self, tearoff=0)
        tools_menu.add_command(label="History", command=callbacks["tools -> history"])
        tools_menu.add_separator()
        tools_menu.add_command(label="Preferences", command=callbacks["tools -> preferences"])

        # Create the Help menu
        help_menu = tk.Menu(self, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)

        # Add menus to the main menu
        self.add_cascade(label="File", menu=file_menu)
        self.add_cascade(label="Edit", menu=edit_menu)
        self.add_cascade(label="Tools", menu=tools_menu)
        self.add_cascade(label="Help", menu=help_menu)

    def show_about(self):
        messagebox.showinfo("About", "This is a sample application using Tkinter.")
