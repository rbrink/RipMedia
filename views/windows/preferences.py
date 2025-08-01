import tkinter as tk
from tkinter import ttk, filedialog

from config import Config
from views.widgets.labelInput import LabelInput
from views.widgets.colorpickerinput import ColorPickerInput

class PreferencesWindow(tk.Toplevel):
    DIRECTORY_FIELDS = {"Output Directory", "Encode Directory", "Cache Directory",
                        "MakeMKV Path", "HandBrake Path", "HB Presets File"}
    
    def __init__(self, parent, on_apply=None):
        super().__init__(parent)
        self.title("Preferences")
        self.geometry("500x400")
        self.on_apply = on_apply

        self.fields = {}
        self.current_category = None
        self.handbrake_presets = Config.load_handbrake_presets(Config.get('HB Presets File'))

        self.create_widgets()
        self.load_first_category()

    def create_widgets(self):
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.category_list = tk.Listbox(container, width=20, height=15)
        self.category_list.pack(side=tk.LEFT, fill=tk.Y)
        self.category_list.bind("<<ListboxSelect>>", self.on_category_select)

        for category in Config.SETTINGS_CATEGORIES:
            self.category_list.insert(tk.END, category)

        self.settings_frame = ttk.Frame(container)
        self.settings_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        container.columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        apply_btn = ttk.Button(btn_frame, text="Apply", command=self.apply_settings)
        apply_btn.pack(side=tk.RIGHT, padx=5)
        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

    def load_first_category(self):
        self.category_list.select_set(0)
        self.on_category_select(None)

    def on_category_select(self, event):
        selected_index = self.category_list.curselection()
        if not selected_index:
            return

        self.current_category = self.category_list.get(selected_index)
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        self.fields.clear()

        settings = Config.SETTINGS_CATEGORIES.get(self.current_category, [])
        for i, setting in enumerate(settings):
            value = Config.get(setting)
            input_var = tk.StringVar(value=value)

            if setting == 'Theme':
                input_widget = LabelInput(
                    self.settings_frame,
                    label=setting,
                    input_class=ttk.Combobox,
                    input_var=input_var,
                    input_args={
                        'textvariable': input_var,
                        'values': list(Config.PRESET_THEMES.keys()),
                        'state': 'readonly'
                    }
                )
                self.fields[setting] = input_widget
                input_widget.grid(row=i, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
                continue
            elif setting == 'HandBrake Presets':
                preset_cat_var = tk.StringVar()
                preset_name_var = tk.StringVar()

                def update_presets(*args):
                    selected_cat = preset_cat_var.get()
                    presets = self.handbrake_presets.get(selected_cat, [])
                    preset_combobox['values'] = presets
                    if presets:
                        preset_name_var.set(presets[0])

                ttk.Label(self.settings_frame, text="Preset Category:").grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
                cat_combobox = ttk.Combobox(self.settings_frame, textvariable=preset_cat_var, values=list(self.handbrake_presets.keys()), state='readonly')
                cat_combobox.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=2)
                cat_combobox.bind("<<ComboboxSelected>>", update_presets)

                ttk.Label(self.settings_frame, text="Preset Name:").grid(row=i+1, column=0, sticky=tk.W, padx=5, pady=2)
                preset_combobox = ttk.Combobox(self.settings_frame, textvariable=preset_name_var, state='readonly')
                preset_combobox.grid(row=i+1, column=1, sticky=tk.EW, padx=5, pady=2)

                # Preselect preset
                current_value = Config.get(setting)
                for cat, names in self.handbrake_presets.items():
                    if current_value in names:
                        preset_cat_var.set(cat)
                        preset_name_var.set(current_value)
                        preset_combobox['values'] = names
                        break

                self.fields[setting] = preset_name_var
                continue
            elif setting in {"Primary Color", "Accent Color"}:
                input_widget = ColorPickerInput(self.settings_frame, label=setting, input_var=input_var)
                self.fields[setting] = input_widget
                input_widget.grid(row=i, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
                continue
            elif isinstance(Config.get(setting), bool):
                input_var = tk.BooleanVar(value=Config.get(setting))
                input_widget = LabelInput(
                    self.settings_frame,
                    label=setting,
                    input_class=ttk.Checkbutton,
                    input_var=input_var
                )
                self.fields[setting] = input_widget
                input_widget.grid(row=i, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
                continue
            else:
                input_widget = LabelInput(
                    self.settings_frame,
                    label=setting,
                    input_class=ttk.Entry,
                    input_var=input_var,
                    input_args={'textvariable': input_var}
                )
                self.fields[setting] = input_widget
                if setting in self.DIRECTORY_FIELDS:
                    input_widget.grid(row=i, column=0, sticky=tk.EW, padx=5, pady=5)
                    def browse_dir(var=input_var):
                        dirname = filedialog.askdirectory(initialdir=var.get() or ".", title=f"Select {setting}")
                        if dirname:
                            var.set(dirname)
                    browse_btn = ttk.Button(self.settings_frame, text="Browse", command=browse_dir)
                    browse_btn.grid(row=i, column=1, sticky=tk.SW, padx=2, pady=5)
                else:
                    input_widget.grid(row=i, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        self.settings_frame.columnconfigure(0, weight=1)
        self.settings_frame.columnconfigure(1, weight=0)

    def apply_settings(self):
        for setting, widget in self.fields.items():
            value = widget.get()
            Config.set(setting, value)

        Config.save()

        if self.on_apply:
            self.on_apply({s: w.get() for s, w in self.fields.items()})

        self.destroy()
