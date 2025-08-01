import os
import yaml
import json

class Config:
    SETTINGS_CATEGORIES = {
        'General': ['OMDB API Key'],
        'Paths': ['Output Directory', 'Cache Directory'],
        'Ripping': ['MakeMKV Path', 'Delete Original After Transcode'],
        'Transcoding': ['HandBrake Path', 'HB Presets File', 'HandBrake Presets'],
        'User Interface': ['Theme', 'Primary Color', 'Accent Color']
    }

    PRESET_THEMES = {
        'Default': {
            'theme': 'winnative',
            'primary_color': '#3498db',
            'accent_color': '#00ff00',
        },
        'Dark': {
            'theme': 'clam',
            'primary_color': '#2c3e50',
            'accent_color': '#95a5a6',
        },
        'Light': {
            'theme': 'alt',
            'primary_color': '#ecf0f1',
            'accent_color': '#e74c3c',
        }
    }

    DEFAULTS = {
        'OMDB API Key': "",
        'Output Directory': './output',
        'Encode Directory': './hboutput',
        'Cache Directory': './data/cache',
        'MakeMKV Path': 'C:/Program Files (x86)/MakeMKV/makemkvcon64.exe',
        'HandBrake Path': 'C:/Program Files/HandBrake/HandBrakeCLI.exe',
        'HB Presets File': './data/presets.json',
        'HandBrake Presets': 'Fast 1080p30',
        'Delete Original After Transcode': False,
        'Theme': 'Default',
        'Primary Color': "#3498db",
        'Accent Color': '#00ff00',
    }

    _config_file = "data/settings.yaml"
    _data = DEFAULTS.copy()
    _handbrake_presets = None  # Internal cache

    @classmethod
    def load(cls):
        if os.path.exists(cls._config_file):
            with open(cls._config_file, "r") as f:
                user_data = yaml.safe_load(f) or {}
                cls._data.update(user_data)

    @classmethod
    def load_handbrake_presets(cls, json_path="./data/presets.json"):
        if cls._handbrake_presets is None:
            with open(json_path, "r") as f:
                data = json.load(f)
            cls._handbrake_presets = {}
            for category in data.get("PresetList", []):
                cat_name = category.get("PresetName", "Uncategorized")
                children = category.get("ChildrenArray", [])
                names = [c["PresetName"] for c in children if "PresetName" in c]
                cls._handbrake_presets[cat_name] = names
        return cls._handbrake_presets
    
    @classmethod
    def save(cls):
        with open(cls._config_file, "w") as f:
            yaml.dump(cls._data, f)

    @classmethod
    def get(cls, key):
        return cls._data.get(key, "")

    @classmethod
    def set(cls, key, value):
        cls._data[key] = value
