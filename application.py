import os, re
import subprocess, threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

from config import Config
from utils import DiscUtils, Logger
from modules.handlers.makemkv import MakeMKVHandler
from modules.handlers.handbrake import HandBrakeHandler
from modules.api.omdb import omdb_api
from modules.api.tvmaze import TVMazeAPI
from views.mainmenu import MainMenu
from views.toolbar import ToolBar
from views.widgets.riptable import RipTable
from views.widgets.sideheadertable import SideHeaderTable
from views.dialogs.progress import ProgressDialog
from views.windows.searchomdb import SearchDialog
from views.windows.episode_selector import EpisodeSelectorWizard
from views.windows.preferences import PreferencesWindow
from views.windows.riplibrary import RipLibraryWindow
from data.ripdatabase import RippingDatabase

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RipMedia v4.0")
        self.geometry("900x750")
        self.resizable(False, False)
        self.iconbitmap("assets/images/.ico/techfun.ico")
        Config.load()
        os.makedirs("logs", exist_ok=True)
        self.logger = Logger.get_logger(__name__)
        self.callbacks = {
            "file -> load_dvd": self.on_open_dvd,
            "file -> load_iso": self.on_open_iso,
            "file -> load_cd": self.on_open_cd,
            "edit -> edit_titles": self.edit_series,
            "edit -> edit_metadata": self.edit_title_metadata,
            "tools -> history": self.open_rip_library,
            "tools -> preferences": lambda: PreferencesWindow(self, on_apply=self.apply_settings),
            "rip -> start_rip": self.on_rip,
            "rip -> stop_rip": lambda: messagebox.showinfo("Rip", "Stop Rip feature not implemented yet."),
        }
        self.iso_path = None # Placeholder for path of ISO image
        self.rows = []  # Placeholder for scanned titles
        self.options = []  # Placeholder for combobox options
        self.disc_info = "Title: None\nPlot:\nNone"  # Placeholder for disc/ISO metadata
        self.current_title = None  # Placeholder for current title being ripped
        self.rip_thread = None
        self.media_type = None
        self.title_year = None
        self.build_UI()
    
    def build_UI(self):
        self.edit_img = ImageTk.PhotoImage(Image.open("assets/images/.png/edit (32x32).png"))
        columns = ["Select", "Index", "Duration", "Title Name", "Rip Progress", "Transcode Progress"]
        # Create the main menu
        self.main_menu = MainMenu(self, self.callbacks)
        self.config(menu=self.main_menu)
        # ToolBar for buttons
        self.toolbar = ToolBar(self, self.callbacks, relief=tk.RAISED, borderwidth=2)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        # Create the RipTable
        self.rip_window = RipTable(self, columns, self.rows, self.options)
        self.rip_window.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        # Disc/ISO Metadata frame
        self.metadata_frame = ttk.LabelFrame(self, text="Disc/ISO Metadata", height=75)
        self.metadata_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        self.poster = ttk.Label(self.metadata_frame, text="Poster Placeholder", font=("Arial", 12), relief=tk.SUNKEN, anchor=tk.CENTER, width=20)
        self.poster.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        headers = ['Title','Year','Plot','Rating','Runtime','Genre','IMDB']
        self.meta_table = SideHeaderTable(self.metadata_frame, headers)
        self.meta_table.pack(side=tk.LEFT, padx=10, pady=10)
        self.edit_title = ttk.Button(self.metadata_frame, text="Edit", image=self.edit_img, compound=tk.LEFT, command=self.edit_title_metadata)
        self.edit_title.pack(padx=10, pady=10)
        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def on_open_dvd(self):
        is_inserted = DiscUtils.is_disc_inserted()
        if is_inserted:
            progress_dialog = ProgressDialog(self, title="Scanning...", message="Initializing...", mode="indeterminate")
        
            mkv = MakeMKVHandler()
            def callback(title, message, percent):
                def update():
                    if percent is not None:
                        if progress_dialog._mode == 'indeterminate':
                            progress_dialog.switch_to_determinate()
                        progress_dialog.update_progress(value=percent, message=message)
                    else:
                        progress_dialog.update_progress(message=message)
                self.after(0, update)
            mkv.progress_callback = callback
            thread = mkv.scan()
        
            def close_when_done():
                thread.join()
                self.after(0, progress_dialog.close)
                self.rows = mkv.scan_results
                self.rip_window.row_data = self.rows
                self.rip_window.selected_vars.clear()
                self.rip_window.combobox_vars.clear()
                for widget in self.rip_window.rip_widgets:
                    widget.destroy()
                self.rip_window.build_header()
                self.rip_window.build_rows()
                self.toolbar.btn_rip.config(state=tk.NORMAL)
        
            threading.Thread(target=close_when_done, daemon=True).start()

            self.current_title = self.guess_title()
            self.update_metadata(self.current_title)
            if self.media_type == "series":
                self.populate_series(self.current_title)
            elif self.media_type == "movie":
                self.populate_movie(self.current_title)

    def on_open_iso(self):
        self.iso_path = filedialog.askopenfilename(title="Select ISO File", filetypes=[("ISO Files", "*.iso")])
        if self.iso_path:
            progress_dialog = ProgressDialog(self, title="Scanning...", message="Initializing...", mode="indeterminate")
        
            mkv = MakeMKVHandler(iso_path=self.iso_path)
            def callback(title, message, percent):
                def update():
                    if percent is not None:
                        if progress_dialog._mode == 'indeterminate':
                            progress_dialog.switch_to_determinate()
                        progress_dialog.update_progress(value=percent, message=message)
                    else:
                        progress_dialog.update_progress(message=message)
                self.after(0, update)
            mkv.progress_callback = callback
            thread = mkv.scan()
        
            def close_when_done():
                thread.join()
                self.after(0, progress_dialog.close)
                self.rows = mkv.scan_results
                self.rip_window.row_data = self.rows
                self.rip_window.selected_vars.clear()
                self.rip_window.combobox_vars.clear()
                for widget in self.rip_window.rip_widgets:
                    widget.destroy()
                self.rip_window.build_header()
                self.rip_window.build_rows()
                self.toolbar.btn_rip.config(state=tk.NORMAL)
        
            threading.Thread(target=close_when_done, daemon=True).start()

            self.current_title = self.guess_title()
            self.update_metadata(self.current_title)
            if self.media_type == "series":
                self.populate_series(self.current_title)
            elif self.media_type == "movie":
                self.populate_movie(self.current_title)
            
    def on_open_cd(self):
        pass

    def on_rip(self):
        self.toolbar.btn_rip.config(state=tk.DISABLED)
        selected = self.rip_window.get_selected()
        if not selected:
            self.logger.info("Rip: No titles selected")
            messagebox.showinfo("Rip", "No titles selected.")
            return

        mkv = MakeMKVHandler()
        output_dir = Config.get("Output Directory")

        def do_rip():
            self.logger.info("Ripping media from Disc/ISO")
            if self.iso_path:
                mkv.rip_selected(selected, output_dir, self.rip_window, iso_path=self.iso_path,
                                 status_callback=lambda text: self.status_var.set(text))
            else:
                mkv.rip_selected(selected, output_dir, self.rip_window, status_callback=lambda text: self.status_var.set(text))

        self.rip_thread = threading.Thread(target=do_rip, daemon=True)
        self.rip_thread.start()
        
    def on_transcode(self, selected):
        encode_dir = Config.get("Encode Directory")
        os.makedirs(encode_dir, exist_ok=True)

        self.logger.info("Encoding selected titles...")
        for i, title in enumerate(selected):
            raw_title = title.get('final_name') or title['title_name']
            input_path = os.path.join(Config.get("Output Directory"), f"{raw_title}.mkv")
            output_path = os.path.join(encode_dir, f"{raw_title}.mkv")
            self.logger.debug(f"Looking for ripped file: {input_path}")
            if not os.path.exists(input_path):
                self.logger.warning(f"Skipping: input file not found: {input_path}")
                continue

            hb = HandBrakeHandler(input_file=input_path)
            progress = self.rip_window.start_transcode_progress(title['row_index'])
            try:
                hb.transcode(output_path, progress_widget=progress)
                try:
                    db = RippingDatabase()
                    db.mark_transcoded(output_path)
                except Exception as e:
                    self.logger.warning(f"Could not mark file as transcoded: {e}")
                if Config.get("Delete Original After Transcode"):
                    try:
                        os.remove(input_path)
                        self.logger.info(f"Deleted original file: {input_path}")
                    except Exception as e:
                        self.logger.warning(f"Could not delete original file: {input_path} — {e}")
            except Exception as e:
                self.logger.error(f"Failed to transcode {input_path}: {e}")
                messagebox.showerror("Error", f"Failed to transcode {input_path}:\n{e}")
                progress.config(style="red.Horizontal.TProgressbar")
        self.toolbar.btn_rip.config(state=tk.NORMAL)

    def open_rip_library(self):
        self.logger.debug("Entered Rip History")
        RipLibraryWindow(self)
    
    def update_metadata(self, title):
        """Update the disc/ISO metadata display."""
        omdb_info = omdb_api().query_omdb(title)
        if not omdb_info:
            dlg = SearchDialog(self, initial_title=title)
            if not dlg.result:
                return
            omdb_info = omdb_api().query_omdb(dlg.result["Title"])
            self.current_title = omdb_info['Title']
        if omdb_info and omdb_info["Poster"] and omdb_info["Poster"] != "N/A":
            img = omdb_api().fetch_poster(omdb_info["Poster"])
            if img:
                img = img.resize((210, 295))
                self.poster_img = ImageTk.PhotoImage(img)
                self.poster.config(image=self.poster_img)
            else:
                self.poster.config(image="", text="Poster Not Found", anchor=tk.CENTER)
            metadata = [
                omdb_info['Title'],
                omdb_info['Year'],
                omdb_info['Plot'],
                omdb_info['Rated'],
                omdb_info['Runtime'],
                omdb_info['Genre'],
                omdb_info['IMDB']
            ]
            self.meta_table.update_data(metadata)
        else:
            self.poster.config(image="", text="Poster Not Available", anchor=tk.CENTER)
        self.media_type = omdb_info["Type"]
        self.title_year = omdb_info["Year"]

    def edit_title_metadata(self):
        dlg = SearchDialog(self)
        if not dlg.result:
            return
        omdb_info = omdb_api().query_omdb(dlg.result["Title"])
        if omdb_info and omdb_info["Poster"] and omdb_info["Poster"] != "N/A":
            img = omdb_api().fetch_poster(omdb_info["Poster"])
            if img:
                img = img.resize((210, 295))
                self.poster_img = ImageTk.PhotoImage(img)
                self.poster.config(image=self.poster_img)
            else:
                self.poster.config(image="", text="Poster Not Found", anchor=tk.CENTER)
            title = omdb_info["Title"]
            plot = omdb_info["Plot"]
            self.metadata.config(text=f"Title: {title}\nPlot:\n{plot}")
        else:
            self.poster.config(image="", text="Poster Not Available", anchor=tk.CENTER)
        self.media_type = omdb_info["Type"]
        self.title_year = omdb_info["Year"]
        self.current_title = title
        if self.media_type == "series":
            self.populate_series(title)
        elif self.media_type == "movie":
            self.populate_movie(title)
        # Refresh table rows and comboboxes after editing title
        self.rip_window.selected_vars.clear()
        self.rip_window.combobox_vars.clear()
        self.rip_window.cmb_options = self.options
        for widget in self.rip_window.inner_frame.winfo_children():
            widget.destroy()
        self.rip_window.build_header()
        self.rip_window.build_rows()
    
    def edit_series(self):
        dialog = EpisodeSelectorWizard(self)
        episodes = dialog.selected_episodes
        if not episodes:
            self.logger.error(f"No episodes found")
            messagebox.showerror("Error", f"No episodes found")
            return
        self.options.clear()
        for ep in episodes:
            show = dialog.selected_show['name']
            year = dialog.selected_show['premiered'][:4] if dialog.selected_show['premiered'] else "Unknown"
            text = f"{show} ({year}) S{ep['season']:02}E{ep['number']:02} - {ep['name']}"
            self.options.append(text)
        
        # Update the combobox values in the UI
        self.rip_window.cmb_options = self.options
        self.rip_window.selected_vars.clear()
        self.rip_window.combobox_vars.clear()
        for widget in self.rip_window.inner_frame.winfo_children():
            widget.destroy()
        self.rip_window.build_header()
        self.rip_window.build_rows()

    def guess_title(self, iso_path=None):
        """Guess the title from the ISO path or disc metadata."""
        if iso_path:
            basename = os.path.splitext(os.path.basename(iso_path))[0]
            name = re.sub(r"[_\.]", " ", basename)
            name = re.sub(r"\b(SEASON|DISC|VOL|DVD|BLURAY|CD|PART|S\d+|D\d+)\b", " ", name, flags=re.IGNORECASE)
            name = re.sub(r"\b(?:\d{1,2})\b", "", name)
            name = re.sub(r"\s+", " ", name).strip()
            self.logger.debug(f"guessed name: {name}")
            return name
        else:
            try:
                result = subprocess.run(
                    ["wmic", "volume", "where", "DriveLetter='D:'", "get", "Label"],
                    capture_output=True, text=True, check=True
                )
                lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
                # Find the first line that isn't the header
                for line in lines:
                    if line.lower() != "label":
                        volume_label = line
                        v_name = re.sub(r"[_\.]", " ", volume_label)
                        v_name = re.sub(r"\b(SEASON|DISC|VOL|DVD|BLURAY|CD|PART|S\d+|D\d+)\b", " ", v_name, flags=re.IGNORECASE)
                        v_name = re.sub(r"\b(?:\d{1,2})\b", "", v_name)
                        v_name = re.sub(r"\s+", " ", v_name).strip()
                        return v_name
                self.logger.warning("Volume label not found.")
                return ""
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Error retrieving volume label: {e}")
                messagebox.showerror("Error", f"Failed to retrieve volume label: {e}")
                return ""

    def extract_season(self, title_name):
        match = re.search(r"(?:season|s)[ _\-\.]?(\d{1,2})", title_name, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 1  # fallback
    
    def populate_series(self, title_name):
        season = self.extract_season(title_name)
        results = TVMazeAPI().search_show(title_name)
        if not results:
            self.logger.error(f"No series found for {title_name}")
            messagebox.showerror("Error", f"No series found for {title_name}")
            return
        show_id = results[0]['show']['id']
        show = f"{results[0]['show']['name']}"
        show_year = f"{results[0]['show']['premiered'][:4]}"
        episodes = TVMazeAPI().get_episodes(show_id, season)
        if not episodes:
            self.logger.error(f"No episodes found for {show} Season {season}")
            messagebox.showerror("Error", f"No episodes found for {show} Season {season}")
            return
        self.options.clear()
        for ep in episodes:
            self.options.append(f"{show} ({show_year}) S{ep['season']:02}E{ep['number']:02} - {ep['name']}")

    def populate_movie(self, title_guess):
        # Query OMDb API for movie details
        omdb_info = omdb_api().query_omdb(title_guess)
        if not omdb_info:
            self.logger.error("Could not retrieve movie details from OMDb.")
            messagebox.showerror("Error", "Could not retrieve movie details from OMDb.")
            return

        # Format the movie title as "Movie Title (Year Released)"
        movie_title = f"{omdb_info['Title']} ({omdb_info['Year']})"

        # Clear and repopulate self.options with the movie title
        self.options.clear()
        self.options.append(movie_title)

        # Update the comboboxes in the CheckComboTable
        for i, row in enumerate(self.rows):
            if i < len(self.rip_window.combobox_vars):
                self.rip_window.combobox_vars[i].set(movie_title)

    def apply_settings(self, new_settings):
        """Apply settings from Preferences dialog."""
        for key, value in new_settings.items():
            Config.set(key, value)
        Config.save()
        self.status_var.set("Settings updated.")
        self.logger.info("Settings applied from Preferences.")

    def refresh_styles(self):
        """Update style colors using the saved config values."""
        primary = Config.get("Primary Color")
        accent = Config.get("Accent Color")

        style = ttk.Style()

        # Rip progress bar
        style.configure("text.Horizontal.TProgressbar", background=primary, foreground="black")

        # Transcode progress bar
        style.configure("transcode.Horizontal.TProgressbar", background=accent, foreground="black")

        self.logger.info(f"Applied primary color: {primary}, accent color: {accent}")

if __name__ == "__main__":
    app = Application()
    app.mainloop()