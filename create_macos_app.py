#!/usr/bin/env python3
"""
Create macOS App Bundle for Scramble Clip 2
This script creates a macOS .app bundle for Scramble Clip 2 by ClipmodeGo
"""

import os
import sys
import shutil
import plistlib
import subprocess
from pathlib import Path

APP_NAME = "Scramble Clip 2"
BUNDLE_ID = "com.clipmodego.scrambleclip2"
VERSION = "1.0"
ICON_NAME = "AppIcon.icns"  # Note: Icon file should be created separately

def create_app_bundle():
    """Create a macOS .app bundle for Scramble Clip 2."""
    # Get the script directory
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Define app bundle paths
    app_bundle_path = script_dir / f"{APP_NAME}.app"
    contents_path = app_bundle_path / "Contents"
    macos_path = contents_path / "MacOS"
    resources_path = contents_path / "Resources"
    
    # Create directory structure
    print(f"Creating app bundle structure at {app_bundle_path}...")
    for path in [contents_path, macos_path, resources_path]:
        path.mkdir(parents=True, exist_ok=True)
    
    # Create Info.plist
    print("Creating Info.plist...")
    info_plist = {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleIdentifier': BUNDLE_ID,
        'CFBundleVersion': VERSION,
        'CFBundleShortVersionString': VERSION,
        'CFBundleExecutable': "launcher",
        'CFBundleIconFile': ICON_NAME,
        'CFBundlePackageType': 'APPL',
        'CFBundleInfoDictionaryVersion': '6.0',
        'CFBundleSupportedPlatforms': ['MacOSX'],
        'LSMinimumSystemVersion': '10.13',
        'NSHighResolutionCapable': True,
        'NSHumanReadableCopyright': '© 2024 ClipmodeGo. All rights reserved.',
    }
    
    with open(contents_path / "Info.plist", 'wb') as f:
        plistlib.dump(info_plist, f)
    
    # Create launcher script
    print("Creating launcher script...")
    launcher_path = macos_path / "launcher"
    
    with open(launcher_path, 'w') as f:
        f.write(f"""#!/bin/bash

# Scramble Clip 2 macOS App Launcher
# Created by ClipmodeGo

# Get the bundle's resources directory
DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"
RESOURCES_DIR="$DIR/../Resources"
APP_DIR="$RESOURCES_DIR/app"

# Set the Python path to use either system Python or bundled Python
export PATH="/usr/bin:/usr/local/bin:$PATH"

# Navigate to app directory and run the application
cd "$APP_DIR"
python3 main.py
exit $?
""")
    
    # Make launcher executable
    launcher_path.chmod(0o755)
    
    # Create app resources directory and copy files
    app_resources_dir = resources_path / "app"
    app_resources_dir.mkdir(exist_ok=True)
    
    # Copy all app files excluding the .app bundle itself
    print("Copying application files...")
    for item in script_dir.iterdir():
        if item.name != f"{APP_NAME}.app" and item.name != f"create_macos_app.py":
            if item.is_dir():
                shutil.copytree(item, app_resources_dir / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, app_resources_dir / item.name)
    
    # Check for icon file
    icon_path = script_dir / ICON_NAME
    if icon_path.exists():
        print(f"Copying app icon: {ICON_NAME}")
        shutil.copy2(icon_path, resources_path / ICON_NAME)
    else:
        print(f"Warning: Icon file {ICON_NAME} not found. App will use default icon.")
        print("To add a custom icon, create an .icns file and place it in the project directory.")
    
    print(f"\nApp bundle created successfully at: {app_bundle_path}")
    print("\nYou can now move this .app bundle to your Applications folder")
    print("or distribute it to other macOS users.")

if __name__ == "__main__":
    if sys.platform != "darwin":
        print("Error: This script can only be run on macOS.")
        sys.exit(1)
        
    create_app_bundle() 