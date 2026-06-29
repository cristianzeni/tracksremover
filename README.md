# TracksRemover 🎧

TracksRemover is a reusable, object-oriented Python core engine and CLI tool designed to extract custom backing tracks or isolate specific stems from any MP3 file. Powered by Meta's Demucs AI (htdemucs_6s), it provides high-quality source separation, allowing musicians, singers, and producers to easily create customized audio mixes.

⚠️ **Educational Purpose & Disclaimer**
This tool is strictly intended and developed for educational, instructional, and personal research purposes only. The author does not condone, promote, or encourage any misuse or illegal distribution of copyrighted material using this software. By using this tool, you acknowledge that you are entirely responsible for ensuring compliance with copyright laws in your jurisdiction. The creator totally disclaims any liability for unauthorized or unlawful use of the generated audio files.

---

## Purpose & Scope

When practicing an instrument or studying a song, standard backing tracks often don't fit your exact needs. TracksRemover solves this by letting you mute exactly what you don't want to hear while preserving the rest of the arrangement. 

The architecture is built on SOLID principles, completely decoupling the processing core (TracksRemover) from the presentation layer (rich terminal UI). This means the engine can be effortlessly imported and reused in other projects, such as desktop GUI applications (e.g., PySide6/Qt), web servers, or automation scripts.

---

## Features

- Multi-Stem Selective Removal: Mute vocals, guitars, bass, or drums individually or in combination.
- Intelligent Audio Preservation: Automatically keeps background elements like pianos, keyboards, and synths intact unless explicitly excluded.
- Smart Suffixing: Output files are automatically named based on the removed components (e.g., song_noVocals_noGuitars.mp3).
- Automatic Overwrite: Instantly overwrites existing outputs to streamline batch processing or iterative testing.
- Beautiful CLI Experience: Features a sleek terminal interface with real-time process execution timers and formatted report panels.
- Developer Ready: Exposes an extensible API with hook support (status_callback) for external UI updates.

---

## Requirements

### System Dependencies
TracksRemover requires FFmpeg installed on your system to handle audio decoding and encoding operations through pydub.

- Linux (Arch-based) 🥰: 
```bash
sudo pacman -S ffmpeg
```
- Linux (Ubuntu/Debian) 🥱:
```bash
sudo apt install ffmpeg
```
- macOS 💸:
```bash
brew install ffmpeg
```
- Windows 🤮: Install via Chocolatey (choco install ffmpeg) or download from the official site and add it to your System PATH.

### Python Dependencies
The tool is compatible with Python 3.9 up to the latest releases (including explicit support for Python 3.13+ via audioop-lts). 

All required Python libraries are listed in the requirements.txt:

- demucs>=4.0.0
- pydub>=0.25.1
- rich>=13.0.0
- audioop-lts; python_version >= "3.13"
- torch>=2.0.0
- torchaudio>=2.0.0
- torchcodec
- lameenc>=1.4.0

---

## Quick Start & Installation

1. Clone or navigate to your project directory.
2. Create and activate a virtual environment (change activate.bash depending on your shell):
```bash
   python -m venv venv
   source venv/bin/activate.fish  
```

3. Install the dependencies:
```bash
   pip install -r requirements.txt
```
---

## Documentation & Usage Examples

### Command Line Interface (CLI) Options

| Argument | Long Flag | Type | Description |
| :--- | :--- | :--- | :--- |
| -f | --file | string | Path to a single MP3 file to process. |
| -d | --dir | string | Path to a directory to scan recursively. |
| -rm | --remove | string | Comma-separated stems to remove: vocals, guitars, bass, drums (Default: guitars). |

### Execution Examples

#### 1. Basic Usage (Remove Guitars Only)
Omitting the -rm argument defaults to removing guitars, generating an output with the _noGuitars.mp3 suffix.
```bash
python tracks_remover.py -f "/path/to/music/Jet - She's A Genius.mp3"
```

#### 2. Create a Backing Track for Singers (Remove Vocals & Guitars)
Pass multiple stems separated by a comma to exclude both elements from the final mix.
```bash
python tracks_remover.py -f "/path/to/music/Blink-182 - All The Small Things.mp3" -rm "vocals,guitars"
```

*Output generated:* Blink-182 - All The Small Things_noVocals_noGuitars.mp3

#### 3. Create a Drumless Track for Drummers (Remove Drums & Bass)
```bash
python tracks_remover.py -f "/path/to/music/The Clash - London Calling.mp3" -rm "drums,bass"
```

*Output generated:* The Clash - London Calling_noDrums_noBass.mp3

#### 4. Recursive Directory Batch Processing
Process an entire folder structure recursively. It automatically searchs for mp3 files like a wildcard (*.mp3).
```bash
python tracks_remover.py -d "/path/to/my_backing_tracks_folder/" -rm "guitars"
```

---

## Reusing the Engine in Code (API Example)

Because the processing module is fully decoupled from the terminal view, you can import it directly into a custom Python script or a desktop UI wrapper:

```python
from tracks_remover import TracksRemover

# Initialize the core engine
engine = TracksRemover()

# Optional UI hook function to capture the elapsed time
def custom_ui_callback(elapsed_time_str):
    print(f"Update GUI Progress Bar/Timer: {elapsed_time_str}")

# Execute the extraction process programmatically
result = engine.execute(
    file_path="song.mp3", 
    remove_argument="vocals,guitars", 
    status_callback=custom_ui_callback
)

if result["success"]:
    print(f"Successfully created: {result['output']} in {result['duration']}s")
else:
    print(f"Error occurred: {result['error']}")
```

---

## License

This project is licensed under the MIT License.

Copyright (c) 2026 Cristian Zeni

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.