#!/usr/bin/env python3
"""
Create macOS DMG for Scramble Clip 2
This script creates a macOS DMG for easy distribution of Scramble Clip 2
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Configuration
APP_NAME = "Scramble Clip 2"
VERSION = "1.0"
VOLUME_NAME = f"{APP_NAME}"
DMG_NAME = f"{APP_NAME.replace(' ', '-')}-{VERSION}.dmg"

def run_command(cmd):
    """Run a shell command and print output."""
    print(f"Running: {' '.join(cmd)}")
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if process.returncode != 0:
        print(f"Error: {process.stderr}")
        return False
    return True

def create_app_bundle():
    """Create a macOS .app bundle for Scramble Clip 2."""
    print("Creating macOS App bundle...")
    # Check if create_macos_app.py exists and run it
    if os.path.exists("create_macos_app.py"):
        result = run_command([sys.executable, "create_macos_app.py"])
        if not result:
            print("Failed to create app bundle. Aborting.")
            return False
        return True
    else:
        print("Error: create_macos_app.py not found.")
        return False

def create_dmg():
    """Create a DMG file for distribution."""
    print(f"Creating DMG file: {DMG_NAME}")
    
    # Make sure the .app bundle exists
    app_bundle = Path(f"{APP_NAME}.app")
    if not app_bundle.exists():
        print(f"Error: {app_bundle} not found. Run create_app_bundle first.")
        return False
    
    # Create temp directory for DMG contents
    temp_dir = Path("dmg_temp")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # Copy the .app bundle to the temp directory
    shutil.copytree(app_bundle, temp_dir / app_bundle.name)
    
    # Create a symlink to /Applications for easy drag-and-drop installation
    os.symlink("/Applications", temp_dir / "Applications")
    
    # Create a background directory
    (temp_dir / ".background").mkdir(exist_ok=True)
    
    # Create a basic background image with a message - this could be improved
    with open(temp_dir / ".background" / "background.txt", "w") as f:
        f.write("Drag Scramble Clip 2 to Applications to install")
    
    # Check if previous DMG exists and remove it
    if os.path.exists(DMG_NAME):
        os.remove(DMG_NAME)
    
    # Create the DMG using hdiutil (macOS only)
    cmd = [
        "hdiutil", "create",
        "-volname", VOLUME_NAME,
        "-srcfolder", str(temp_dir),
        "-ov", "-format", "UDZO",
        DMG_NAME
    ]
    
    result = run_command(cmd)
    
    # Clean up temp directory
    shutil.rmtree(temp_dir)
    
    if result:
        print(f"\nSuccess! DMG created: {DMG_NAME}")
        print(f"File location: {os.path.abspath(DMG_NAME)}")
        return True
    else:
        print("Failed to create DMG file.")
        return False

def main():
    """Main function to create DMG."""
    if sys.platform != "darwin":
        print("Error: This script can only be run on macOS.")
        return False
    
    # First create the app bundle
    if not create_app_bundle():
        return False
    
    # Then create the DMG
    if not create_dmg():
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 