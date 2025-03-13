# Distributing Scramble Clip 2

This document provides instructions for distributing Scramble Clip 2 by ClipmodeGo.

## Packaging Options

Scramble Clip 2 can be distributed in several formats:

1. **ZIP Package**: Works on all platforms (Windows, macOS, Linux)
2. **macOS DMG**: Mac-specific installer disk image
3. **macOS App Bundle**: Standalone Mac application

## Creating Distribution Packages

### Easy Method (Recommended)

Run the all-in-one packaging script:

```bash
python package_for_distribution.py
```

This script will:
- Create a ZIP package for all platforms
- Create a macOS DMG file (if on macOS)
- Generate an app icon (if on macOS)

### Individual Packaging Methods

#### ZIP Package

```bash
python create_zip_package.py
```

#### macOS DMG (Mac only)

```bash
python create_macos_dmg.py
```

#### macOS App Icon (Mac only)

```bash
python create_app_icon.py
```

## Distribution Files

After running the packaging scripts, you'll have the following files available for distribution:

- `Scramble-Clip-2-1.0_TIMESTAMP.zip`: ZIP archive of the application
- `Scramble-Clip-2-1.0.dmg`: macOS disk image (Mac only)
- `Scramble Clip 2.app`: macOS application bundle (Mac only)

## Uploading to Your Website

1. Upload the ZIP file to your web server (and DMG if available)
2. Create download links on your website
3. Provide installation instructions for your users

## Installation Instructions for Users

Include these instructions on your website:

### Windows Users

1. Download the ZIP file
2. Extract all files to a folder
3. Run `launch.bat` or `launcher.py`

### macOS Users

#### Option 1: DMG Installation
1. Download the DMG file
2. Open the DMG file
3. Drag the "Scramble Clip 2" app to your Applications folder
4. Launch from Applications

#### Option 2: ZIP Installation
1. Download the ZIP file
2. Extract all files to a folder
3. Run `mac_launcher.command` or `launcher.py`

### Linux Users

1. Download the ZIP file
2. Extract all files to a folder
3. Run `./launch.sh` or `python launcher.py`

## System Requirements

- Python 3.6 or higher
- PyQt5
- MoviePy
- FFmpeg

Note: The launcher scripts will attempt to install required Python packages if needed.

## License

MIT

## Credits

Created by ClipmodeGo 