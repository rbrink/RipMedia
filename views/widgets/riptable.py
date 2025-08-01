import tkinter as tk
from tkinter import ttk

class RipTable(tk.LabelFrame):
    def __init__(self, parent, columns, row_data, cmb_options, *args, **kwargs):
        super().__init__(parent, text="Titles from Disc/ISO", *args, **kwargs)
        self.parent = parent
        self.on_selection_change = None  # Callback for selection change
        self.columns = columns
        self.row_data = row_data
        self.cmb_options = cmb_options
        self.selected_vars = []
        self.combobox_vars = []
        self.rip_widgets = []
        self.transcode_widgets = []

        self.create_widgets()

    def create_widgets(self):
        self.canvas = tk.Canvas(self, relief=tk.SUNKEN, borderwidth=2, width=500)
        self.scroll_y = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Inner frame for the view
        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor='nw')
        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind("<Configure>", self.resize_inner_frame)

        self.build_header()
        self.build_rows()

    def build_header(self):
        for col, text in enumerate(self.columns):
            label = ttk.Label(self.inner_frame, text=text, relief="raised", borderwidth=2, font=("Segoe UI", 10, "bold"),
                              anchor="center", padding=5)
            label.grid(row=0, column=col, pady=2, sticky='ew')
            self.inner_frame.columnconfigure(col, weight=1)
    
    def build_rows(self):
        for i, row in enumerate(self.row_data, start=1):
            selected = tk.BooleanVar()
            combo_val = tk.StringVar(value=self.cmb_options[0] if self.cmb_options else "")

            # Check if row is selected
            def on_check(var=selected):
                if self.on_selection_change:
                    self.on_selection_change()
            # Select title field
            checkbutton = ttk.Checkbutton(self.inner_frame, variable=selected, command=on_check)
            checkbutton.grid(row=i, column=0, sticky=tk.NSEW, padx=5)
            # Title  index and Title Duration field
            title_idx = ttk.Label(self.inner_frame, text=row['index'], font=("Arial", 10), anchor=tk.CENTER)
            title_idx.grid(row=i, column=1, sticky=tk.EW, padx=5)
            title_duration = ttk.Label(self.inner_frame, text=row['duration'], font=("Arial", 10), anchor=tk.CENTER)
            title_duration.grid(row=i, column=2, sticky=tk.EW, padx=5)
            # Title Name field
            title_name = ttk.Combobox(self.inner_frame, textvariable=combo_val, width=40, font=("Arial", 10),
                                      values=self.cmb_options)
            title_name.grid(row=i, column=3, sticky=tk.EW, padx=5)
            # Rip Progress field
            rip_label = ttk.Label(self.inner_frame, text="Pending", font=("Arial", 10), anchor=tk.CENTER)
            rip_label.grid(row=i, column=4, sticky=tk.EW, padx=5)
            self.rip_widgets.append(rip_label)
            # Transcode progress field
            transcode_label = ttk.Label(self.inner_frame, text="Pending", font=("Arial", 10), anchor=tk.CENTER)
            transcode_label.grid(row=i, column=5, sticky=tk.EW, padx=5)
            self.transcode_widgets.append(transcode_label)

            if row.get('default'):
                title_name.set(row['default'])
            
            self.selected_vars.append(selected)
            self.combobox_vars.append(combo_val)
    
    def get_selected(self):
        """Returns a list of selected rows with their data."""
        results = []
        for i, selected_var in enumerate(self.selected_vars):
            if selected_var.get():
                results.append({
                    'index': self.row_data[i]['index'],
                    'duration': self.row_data[i]['duration'],
                    'title_name': self.combobox_vars[i].get(),
                    'row_index': i
                })
        return results
    
    def resize_inner_frame(self, event):
        """Resize the inner frame to fit the canvas."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def start_rip_progress(self, row_index):
        # Destroy old label
        self.rip_widgets[row_index].destroy()    
        # Create and insert progress bar
        style = ttk.Style(self.inner_frame)
        style.layout('text.Horizontal.TProgressbar',
                     [('Horizontal.Progressbar.trough',
                       {'children': [('Horizontal.Progressbar.pbar',
                                      {'side': 'left', 'sticky': 'ns'})],
                        'sticky': 'nsew'}),
                       ('Horizontal.Progressbar.label', {'sticky': 'nswe'})])
        style.configure('text.Horizontal.TProgressbar', text='0%', anchor='center')
        variable = tk.StringVar(self.inner_frame)
        rip_progress = ttk.Progressbar(self.inner_frame, orient=tk.HORIZONTAL, length=100,
                                           mode='determinate', style='text.Horizontal.TProgressbar', variable=variable)
        rip_progress.grid(row=row_index + 1, column=4, sticky=tk.EW, padx=5)  # +1 for header row
        self.rip_widgets[row_index] = rip_progress
        return rip_progress  # So the caller can update the progress bar
    
    def start_transcode_progress(self, row_index):
        self.transcode_widgets[row_index].destroy()
        style = ttk.Style(self.inner_frame)
        style.layout('transcode.Horizontal.TProgressbar',
                     [('Horizontal.Progressbar.trough',
                       {'children': [('Horizontal.Progressbar.pbar',
                                      {'side': 'left', 'sticky': 'ns'})],
                        'sticky': 'nsew'}),
                       ('Horizontal.Progressbar.label', {'sticky': 'nswe'})])
        style.configure('transcode.Horizontal.TProgressbar', text='0%', anchor='center')
        variable = tk.StringVar(self.inner_frame)
        transcode_progress = ttk.Progressbar(self.inner_frame, orient=tk.HORIZONTAL, length=100,
                                                 mode='determinate', style='transcode.Horizontal.TProgressbar', variable=variable)
        transcode_progress.grid(row=row_index + 1, column=5, sticky=tk.EW, padx=5)
        self.transcode_widgets[row_index] = transcode_progress
        return transcode_progress
