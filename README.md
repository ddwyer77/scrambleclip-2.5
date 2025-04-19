# Scramble Clip 2 by ClipmodeGo

A professional video randomization tool for creating scrambled video clips from multiple source videos.

## Features

- Create randomized video clips from your source videos
- Add your own audio track to the output videos
- Generate multiple video clips in a single batch
- Professional black and green UI theme
- Smart AI-based clip selection for better content
- Prevents reuse of the same footage within a batch

## Smart AI Features

The AI video analysis system:
- Analyzes content for interesting segments (motion, visual complexity, brightness)
- Avoids repetitive content across output videos
- Scores clips on a 0-10 scale for "interestingness"
- Automatically selects the most engaging footage
- Ensures visual variety in generated videos

## Requirements

- Python 3.6 or higher
- Dependencies listed in requirements.txt
  - MoviePy
  - NumPy
  - OpenCV
  - Pillow
  
## Installation

### Method 1: Using the Launcher

1. Unzip the downloaded package
2. Run the appropriate launcher for your system:
   - Windows: `launch.bat`
   - macOS/Linux: `./launch.sh`
   - Any platform: `python launcher.py`

### Method 2: Manual Installation

1. Install Python 3.6 or higher
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python main.py
   ```

## Usage

1. **Add Input Videos:**
   - Click the "Add" button in the Input Videos section
   - Select MP4 or MOV video files
   
2. **Select Audio:**
   - Click "Browse" next to the Input Audio field
   - Select an MP3 audio file
   
3. **Set Output Directory:**
   - By default, videos are saved to the `outputs` directory
   - You can change this by clicking "Browse" next to Output Path
   
4. **Configure Options:**
   - Set the number of videos to generate
   - Enable/disable AI-based clip selection
   
5. **Generate Videos:**
   - Click "Generate Videos" button
   - Progress will be shown in the status bar
   
6. **View Output:**
   - Select a video from the Output Videos list
   - Click "Play" to watch the video
   - Click "Open Folder" to browse all generated videos

## Licensing

A tool by ClipmodeGo. All rights reserved. 