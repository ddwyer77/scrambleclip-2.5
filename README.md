# Scramble Clip 2

A Python-based video generation tool that creates randomized social media content from your video clips.

## Features

- Process a folder of MP4 and MOV video clips of varying lengths
- Randomly extract four non-overlapping clips (approximately 4 seconds each, with ±1 second variability)
- Assemble multiple unique 16-second output videos with a standardized 9:16 aspect ratio
- Pair video clips with your provided audio file (loops or trims as necessary)
- User-friendly GUI to select input/output directories and manage generation

## Requirements

- Python 3.6+
- FFmpeg (must be installed on your system)
- Required Python packages (see requirements.txt)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/scramble_clip2.git
   cd scramble_clip2
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Make sure FFmpeg is installed on your system:
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **Linux**: `sudo apt install ffmpeg` or equivalent for your distribution

## Usage

1. Prepare your video clips:
   - Place MP4 or MOV video files in the `assets/input_videos` directory
   - Place an audio file (MP3 format recommended) in `assets/input_audio/audio.mp3`

2. Run the application using one of the provided launchers:
   
   **Using the main Python script:**
   ```
   python main.py
   ```
   
   **Using the cross-platform launcher (recommended):**
   ```
   python launcher.py
   ```
   
   **On macOS:**
   ```
   ./launch.sh
   ```
   
   **On Windows:**
   ```
   launch.bat
   ```
   
   **Create a macOS app bundle (optional):**
   ```
   ./create_macos_app.py
   ```
   
   This will create a standalone .app that you can move to your Applications folder.

3. Using the GUI:
   - Customize the input/output paths as needed
   - Set the number of videos to generate
   - Click "Generate Videos" to start the process
   - The generated videos will be saved to the output directory

## Launcher Scripts

The project includes several launcher options for different platforms:

- **launcher.py**: A cross-platform Python launcher that checks requirements and handles errors gracefully
- **launch.sh**: A shell script for macOS and Linux systems
- **launch.bat**: A batch file for Windows systems
- **create_macos_app.py**: Creates a macOS .app bundle for easy launching
- **automator_script.sh**: Script for creating a launcher with macOS Automator

## Project Structure

```
scramble_clip2/
├── assets/
│   ├── input_videos/    # Place your source videos here
│   └── input_audio/     # Place your audio file here
├── outputs/             # Generated videos will be saved here
├── src/
│   ├── generator.py     # Core video generation logic
│   ├── utils.py         # Utility functions
│   ├── pil_patch.py     # Compatibility patch for Pillow
│   └── pyqt_gui.py      # PyQt graphical user interface
├── main.py              # Application entry point
├── launcher.py          # Cross-platform launcher
├── launch.sh            # macOS/Linux launcher script
├── launch.bat           # Windows launcher script
├── create_macos_app.py  # macOS .app bundle creator
├── automator_script.sh  # macOS Automator script
├── requirements.txt     # Required Python packages
└── README.md            # This file
```

## License

MIT

## Credits

Created by ClipmodeGo 