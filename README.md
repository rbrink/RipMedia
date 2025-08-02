# RipMedia

**RipMedia** is a cross-platform GUI-based media ripping and transcoding application built with Python and Tkinter. It supports ripping DVDs and ISO images using MakeMKV, transcoding videos using HandBrake, fetching movie/series metadata from OMDB and TVMaze, and managing rip history via a SQLite database.

---

## ✨ Features

- 🎬 **DVD/ISO Scanning and Ripping** with MakeMKV
- 🎧 **HandBrake Transcoding** using custom presets
- 📀 **Metadata Fetching** from [OMDB](http://www.omdbapi.com/) and [TVMaze](https://www.tvmaze.com/api)
- 🔎 **TV Episode Selector** with multi-season support
- 💾 **Rip History Management** (SQLite)
- 🎨 **Theme Customization** (Dark, Light, Custom Colors)
- 📂 **Directory Preferences and File Path Configs**
- 🔧 **Built-in Preferences UI and Toolbars**

---

## 🖥 Screenshots

> Add screenshots here of:

- The main UI
- Episode selector
- Preferences window
- Rip table in action

---

## 🚀 Installation

1. **Clone the repository:**

```bash
git clone https://github.com/rbrink/ripmedia.git
cd ripmedia
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

> Requirements include:

- `Pillow`
- `requests`
- `pyyaml`

3. **Install MakeMKV and HandBrake:**

- [MakeMKV](https://www.makemkv.com/download/)
- [HandBrakeCLI](https://handbrake.fr/downloads.php)

4. **Set paths in Preferences (via the GUI):**

- MakeMKV Path
- HandBrake Path
- Output & Cache Directories
- HandBrake Preset JSON File

---

## 🛠 Usage

Run the application:

```bash
python application.py
```

From the UI:

- Use the toolbar or menu to load DVDs, ISOs, or music CDs.
- Select titles, set custom names, and rip them.
- Transcoding and metadata fetching are handled automatically.
- View previous rips in the Rip Library.

---

## ⚙ Configuration

Settings are stored in `settings.yaml`. You can adjust them via the GUI or manually.

Preset themes and colors are stored in `Config.PRESET_THEMES`.

---

## 📁 Directory Structure

```
.
├── application.py
├── config.py          # Preferences
├── utils.py
├── assets/            # Button and menu icons
├── data/
    ├── presets.json   # HandBrake preset file
    └── ripdatabase.py
├── logs/              # Application logs
├── modules/           # Main logic
├── output/            # Ripped MKV files
├── hboutput/          # Transcoded files
├── cache/             # OMDB/TVMaze cache
├── views/
├── rips.db            # SQLite database
```

---

## 🔒 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 📬 Acknowledgments

- [OMDb API](http://www.omdbapi.com/)
- [TVMaze API](https://www.tvmaze.com/api)
- [MakeMKV](https://www.makemkv.com/)
- [HandBrakeCLI](https://handbrake.fr/)
