import subprocess
import re
from tkinter import ttk

from config import Config

class HandBrakeHandler:
    def __init__(self, input_file=None, output_dir=None):
        self.output_dir = output_dir or Config.get('Encode Directory')
        self.handbrake_executable = Config.get('HandBrake Path')
        self.preset_file = Config.get('HB Presets File')
        self.preset = Config.get('HandBrake Presets')
        self.input_file = input_file
    
    def transcode(self, output_path, progress_widget=None):
        """Transcode a single file using HandBrakeCLI"""
        cmd = [
            self.handbrake_executable,
            "--preset-import-file", self.preset_file,  # Import presets from the JSON file
            "-Z", self.preset,  # Use the selected preset
            "-i", self.input_file,
            "-o", output_path
        ]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in iter(process.stdout.readline, ""):
            match = re.search(r"(\d{1,3}\.\d{1,2}\s?%)", line)
            if match and progress_widget:
                percent = float(match.group(1).strip().replace('%', ''))
                progress_widget["value"] = percent
                progress_widget.configure(style="transcode.Horizontal.TProgressbar")
                style = ttk.Style()
                style.configure("transcode.Horizontal.TProgressbar", text=f"{percent}%", anchor='center')
                progress_widget.update_idletasks()
        process.stdout.close()
        process.wait()
