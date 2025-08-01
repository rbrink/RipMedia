import os, re
import subprocess
import threading
from tkinter import ttk, messagebox
from collections import defaultdict

from config import Config
from utils import Logger
from views.dialogs.progress import ProgressDialog
from data.ripdatabase import RippingDatabase

class MakeMKVHandler:
    def __init__(self, disc_idx=0, iso_path=None, progress_callback=None):
        self.disc_idx = disc_idx
        self.iso_path = iso_path
        self.progress_callback = progress_callback
        self._scan_dict = defaultdict(dict)
        self.current_prgt = ""
        self.current_prgc = ""
        self.scan_results = []
        self.makemkv_path = Config.get('MakeMKV Path')
        if not os.path.exists(self.makemkv_path):
            raise FileNotFoundError(f"MakeMKV executable not found at {self.makemkv_path}")
        self._active_proc = None  # Store the current rip process
        self.logger = Logger.get_logger(__name__)
    
    def _emit_progress(self, title, message, percent=None):
        if self.progress_callback:
            self.progress_callback(title, message, percent)
    
    def _parse_output(self, line):
        if match := re.match(r'^PRGT:\d+,\d+,"(.+)"', line):
            self.current_prgt = match.group(1)
            self._emit_progress(self.current_prgt, self.current_prgc or "")
        elif match := re.match(r'^PRGC:\d+,\d+,"(.+)"', line):
            self.current_prgc = match.group(1)
            self._emit_progress(self.current_prgt or "", self.current_prgc)
        elif match := re.match(r'^PRGV:(\d+),(\d+),(\d+)', line):
            completed, _, total = map(int, match.groups())
            percent = int((completed / total) * 100) if total > 0 else 0
            self._emit_progress(self.current_prgt or "", self.current_prgc or "", percent)
        elif match := re.match(r'^MSG:\d+,.+,"(.+)"', line):
            self._emit_progress(self.current_prgt or "", match.group(1))
        elif match := re.match(r'TINFO:(\d+),(\d+),\d+,"(.*)"', line):
            title_idx = int(match.group(1))
            field_id = int(match.group(2))
            value = match.group(3).strip()

            self._scan_dict[title_idx][field_id] = value

            # Only process when both duration (field 9) and name (field 27) are available
            fields = self._scan_dict[title_idx]
            if 9 in fields and 27 in fields and not any(r['index'] == title_idx for r in self.scan_results):
                # Duration format: HH:MM:SS or number of seconds
                duration_raw = fields[9]
                total_seconds = None
                if match := re.match(r'(\d+):(\d+):(\d+)', duration_raw):
                    h, m, s = map(int, match.groups())
                    total_seconds = h * 3600 + m * 60 + s
                elif duration_raw.isdigit():
                    total_seconds = int(duration_raw)

                self.scan_results.append({
                    'index': title_idx,
                    'duration': total_seconds,
                    'name': fields[27] or f"Title_{title_idx}"
                })
    
    def _run_command(self, args):
        self.logger.info("Scanning Disc/ISO...")
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in iter(process.stdout.readline, ""):
            self._parse_output(line.strip())                
        process.stdout.close()
        process.wait()
    
    def scan(self):
        """Scan the disc or ISO for titles."""
        # Determine if Disc or ISO
        if self.iso_path:
            cmd = [self.makemkv_path, '-r', '--progress=-same', '--minlength=120', 'info', f"iso:{self.iso_path}"]
        else:
            cmd = [self.makemkv_path, '-r', '--progress=-same', '--minlength=120', 'info', f"disc:{self.disc_idx}"]

        thread = threading.Thread(target=self._run_command, args=(cmd,))
        thread.start()
        return thread
    
    def rip(self, title_index, output_path, iso_path=None, progress_widget=None, status_callback=None):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if iso_path:
            cmd = [self.makemkv_path, '-r', '--progress=-same', 'mkv', f"iso:{iso_path}", str(title_index), output_path]
        else:
            cmd = [self.makemkv_path, '-r', '--progress=-same', 'mkv', f"disc:{self.disc_idx}", str(title_index), output_path]

        self.logger.info(f"Ripping title {title_index}...")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in iter(process.stdout.readline, ""):
            line = line.strip()
            if match := re.match(r'^PRGC:\d+,\d+,"(.+)"', line):
                self.current_prgc = match.group(1)
                if status_callback:
                    status_callback(self.current_prgc)
            elif match := re.match(r'^PRGV:(\d+),(\d+),(\d+)', line):
                completed, _, total = map(int, match.groups())
                percent = int((completed / total) * 100) if total > 0 else 0
                if progress_widget:
                    progress_widget["value"] = percent
                    progress_widget.configure(style="text.Horizontal.TProgressbar")
                    style = ttk.Style()
                    style.configure("text.Horizontal.TProgressbar", text=f"{percent}%", anchor='center')
                    progress_widget.update_idletasks()
        process.stdout.close()
        process.wait()
    
    def rip_selected(self, titles, output_dir, rip_table, iso_path=None, status_callback=None):
        """Rip selected titles using in-row progress bars."""
        if not titles:
            self.logger.info(f"No Titles: No titles found to rip.")
            return
        os.makedirs(output_dir, exist_ok=True)

        def run_rips():
            for i, title in enumerate(titles):
                title_index = title['index']
                tmp_name = title['title_name'] or f"Title_{title_index}"
                tmp_name = "".join(c for c in tmp_name if c.isalnum() or c in (' ', '-', '_','(',')')).rstrip()
                tmp_name = tmp_name.replace(":", "_")
                title_name = tmp_name
                title['final_name'] = title_name
                pattern = re.compile(rf".*_t0*{title_index}\.mkv", re.IGNORECASE)
                old_path = None

                progress_widget = rip_table.start_rip_progress(title['row_index'])
                try:
                    self.rip(title_index, output_dir, iso_path, progress_widget, status_callback=status_callback)
                    for f in os.listdir(output_dir):
                        if pattern.match(f):
                            old_path = os.path.join(output_dir, f)
                            break
                    new_path = os.path.join(output_dir, f"{title_name}.mkv")
                    os.rename(old_path, new_path)
                    progress_widget["value"] = 100  # Complete

                    try:
                        db = RippingDatabase()
                        disc_id = db.add_disc(
                            title=rip_table.master.current_title or "Unknown",
                            media_type=rip_table.master.media_type or "unknown",
                            year=rip_table.master.title_year or "",
                            volume_label="Unknown",  # Optional: replace if you detect volume label
                            metadata=""
                        )
                        db.add_rip(
                            disc_id=disc_id,
                            title_index=title_index,
                            title_name=title_name,
                            duration=title['duration'],
                            output_path=new_path
                        )
                    except Exception as db_err:
                        self.logger.warning(f"Failed to log rip to database: {db_err}")
                except Exception as e:
                    self.logger.error(f"Failed to rip title {title_index}: {e}")
                    messagebox.showerror("Error", f"Failed to rip title {title_index}:\n{e}")
                    progress_widget.config(style="red.Horizontal.TProgressbar")
            if status_callback:
                status_callback("All rips completed. Starting transcoding...")
                self.logger.info("All rips completed. Starting transcoding...")

            if hasattr(rip_table.master, "on_transcode"):
                rip_table.master.on_transcode(titles)
                
            if status_callback:
                status_callback("All transcoding completed.")
                messagebox.showinfo("Info", "All transcoding completed.")
                self.logger.info("All transcoding completed.")

        threading.Thread(target=run_rips, daemon=True).start()

    def rip_all(self, titles, output, parent_win=None):
        """Rip all titles from the disc or ISO."""
        if not titles:
            self.logger.info(f"No Titles: No titles found to rip.")
            return
        os.makedirs(output, exist_ok=True)
        progress = ProgressDialog(parent_win, title="Ripping Titles", message="Ripping all titles...",
                                  mode="determinate", max_value=len(titles))
        progress.start()
        try:
            for i, title in enumerate(titles):
                title_index = title['index']
                title_name = title['title_name'] or f"Title {title_index}"
                output_path = os.path.join(output, f"{title_name}.mkv")
                self.rip(title_index, output_path)
                progress.update_progress(i + 1, f"Ripped {title_name}")
            progress.update_progress(len(titles), "All titles ripped successfully.")
        except Exception as e:
            self.logger.error(f"Failed to rip all titles: {e}")
            messagebox.showerror("Error", f"Failed to rip all titles: {e}")
        finally:
            progress.close()
    
    def cancel(self):
        if self._active_proc and self._active_proc.poll() is None:
            self.logger.info("Cancelling active MakeMKV process...")
            self._active_proc.terminate()  # Sends SIGTERM on Unix, or terminates on Windows
            try:
                self._active_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._active_proc.kill()
            finally:
                self._active_proc = None
