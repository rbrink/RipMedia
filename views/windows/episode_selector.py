import tkinter as tk
from tkinter import ttk, messagebox

from modules.api.tvmaze import TVMazeAPI

class EpisodeSelectorWizard(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("TV Show Import")
        self.geometry(self.center_geometry(500, 450))
        self.transient(parent)
        self.grab_set()

        self.parent = parent
        self.show_results = []
        self.episodes = []
        self.selected_show = None
        self.selected_episodes = []

        self.build_ui()
        self.show_page_1()
        self.wait_window()

    def build_ui(self):
        frm_spacer = ttk.Frame(self, height=50)
        frm_spacer.pack(fill=tk.X)
        self.page1 = ttk.Frame(self)
        self.page2 = ttk.Frame(self)

        # Page 1: Search & select show
        ttk.Label(self.page1, text="Search for TV show:").pack(padx=85, pady=(10, 2), anchor=tk.W)
        entry_frame = ttk.Frame(self.page1)
        entry_frame.pack(pady=5)
        self.entry = ttk.Entry(entry_frame, width=40)
        self.entry.focus()
        self.entry.bind("<Return>", self.perform_search)
        self.entry.pack(side=tk.LEFT)
        ttk.Button(entry_frame, text="Search", command=self.perform_search).pack(side=tk.LEFT, padx=5)

        self.listbox = tk.Listbox(self.page1, width=55, height=10)
        self.listbox.bind("<<ListboxSelect>>", self.show_sel_show)
        self.listbox.pack(padx=10, pady=10)

        self.label_selected = ttk.Label(self.page1, text="Selected show: None")
        self.label_selected.pack(padx=85, anchor=tk.W)

        btn1_frame = ttk.Frame(self.page1)
        btn1_frame.pack(padx=15, pady=10, anchor=tk.E)
        ttk.Button(btn1_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn1_frame, text="Next >", command=self.show_page_2).pack(side=tk.LEFT, padx=5)

        # Page 2: Select episodes
        control_frame = ttk.Frame(self.page2)
        control_frame.pack(padx=5)
        self.side1 = ttk.Frame(control_frame)
        self.side1.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Label(self.side1, text="Seasons:").pack(padx=5)
        self.list_seasons = tk.Listbox(self.side1, width=25, height=15)
        self.list_seasons.bind("<<ListboxSelect>>", self.show_episodes)
        self.list_seasons.pack(padx=5)
        self.side2 = ttk.Frame(control_frame)
        self.side2.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Label(self.side2, text="Episodes:").pack(anchor="w", padx=5)
        frm_episodes = ttk.Frame(self.side2, relief=tk.SUNKEN, borderwidth=1)
        frm_episodes.pack(fill=tk.BOTH)
        self.btn_sel_all = ttk.Button(self.side2, text="Select All", command=self.select_all_episodes)
        self.btn_sel_all.pack(pady=10, anchor=tk.W)
        # Scrollable canvas
        canvas = tk.Canvas(frm_episodes, width=270, height=235)
        scrollbar = ttk.Scrollbar(frm_episodes, orient="vertical", command=canvas.yview)
        self.episode_container = ttk.Frame(canvas)

        self.episode_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.episode_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.episode_canvas = canvas

        btn2_frame = ttk.Frame(self.page2)
        btn2_frame.pack(pady=10)
        ttk.Button(btn2_frame, text="< Previous", command=self.show_page_1).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn2_frame, text="OK", command=self.confirm_selection).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn2_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def perform_search(self, event):
        query = self.entry.get().strip()
        if not query:
            return
        self.show_results = TVMazeAPI().search_show(query)
        self.listbox.delete(0, tk.END)
        for item in self.show_results:
            show = item['show']
            name = show['name']
            year = show.get('premiered', '')[:4] if show.get('premiered') else ''
            self.listbox.insert(tk.END, f"{name} ({year})")

    def show_page_1(self):
        # Clear season listbox
        self.list_seasons.delete(0, tk.END)

        # Clear episode container widgets
        for widget in self.episode_container.winfo_children():
            widget.destroy()

        # Clear season -> episode state
        self.season_episode_vars = {}

        # Reset Select All button
        self.btn_sel_all.config(text="Select All", command=self.select_all_episodes)

        # Switch pages
        self.page2.pack_forget()
        self.page1.pack(fill=tk.BOTH, expand=True)

    def show_page_2(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("No selection", "Please select a show first.")
            return
        self.selected_show = self.show_results[selection[0]]['show']
        self.seasons = TVMazeAPI().get_seasons(self.selected_show['id'])
        self.label_selected.config(text=f"Selected show: {self.selected_show['name']}")

        for i in range(len(self.seasons)):
            season = f"Season {self.seasons[i]['number']}"
            self.list_seasons.insert(tk.END, season)

        self.page1.pack_forget()
        self.page2.pack(fill=tk.BOTH, expand=True)
    
    def show_episodes(self, event):
        selected = self.list_seasons.curselection()
        if not selected:
            return

        season_number = self.seasons[selected[0]]['number']
        show_id = self.selected_show['id']
        episodes = TVMazeAPI().get_episodes(show_id, season=season_number)
        
        # Clear previous
        for widget in self.episode_container.winfo_children():
            widget.destroy()

        # Save episode checkboxes per season
        if not hasattr(self, 'season_episode_vars'):
            self.season_episode_vars = {}

        self.season_episode_vars[season_number] = []

        for ep in episodes:
            var = tk.BooleanVar(value=False)
            text = f"S{ep['season']:02}E{ep['number']:02} - {ep['name']}"
            cb = ttk.Checkbutton(self.episode_container, text=text, variable=var)
            cb.pack(anchor="w", padx=15)
            self.season_episode_vars[season_number].append((var, ep))
        self.btn_sel_all.config(text="Select All", command=self.select_all_episodes)
        
    def select_all_episodes(self):
        selected = self.list_seasons.curselection()
        if not selected:
            return
        season_number = self.seasons[selected[0]]['number']
        if season_number in self.season_episode_vars:
            for var, _ in self.season_episode_vars[season_number]:
                var.set(True)
            self.btn_sel_all.config(text="Select None", command=self.deselect_all_episodes)

    def deselect_all_episodes(self):
        selected = self.list_seasons.curselection()
        if not selected:
            return
        season_number = self.seasons[selected[0]]['number']
        if season_number in self.season_episode_vars:
            for var, _ in self.season_episode_vars[season_number]:
                var.set(False)
            self.btn_sel_all.config(text="Select All", command=self.select_all_episodes)

    def confirm_selection(self):
        selected = []
        if hasattr(self, 'season_episode_vars'):
            for season_vars in self.season_episode_vars.values():
                for var, ep in season_vars:
                    if var.get():
                        selected.append(ep)
        self.selected_episodes = selected
        self.destroy()

    def show_sel_show(self, event):
        selection = self.listbox.curselection()
        selected = self.show_results[selection[0]]['show']['name']
        year = self.show_results[selection[0]]['show']['premiered'][:4]
        self.label_selected.config(text=f"Selected Show: {selected} ({year})")

    def center_geometry(self, width, height):
        self.master.update_idletasks()
        root_x, root_y = self.master.winfo_x(), self.master.winfo_y()
        root_w, root_h = self.master.winfo_width(), self.master.winfo_height()
        x = root_x + (root_w - width) // 2
        y = root_y + (root_h - height) // 2
        return f"{width}x{height}+{x}+{y}"
