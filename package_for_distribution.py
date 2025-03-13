#!/usr/bin/env python3
"""
Package Scramble Clip 2 for Distribution

This script creates distribution packages for Scramble Clip 2 including:
- ZIP archive
- macOS DMG (on macOS only)
- macOS App bundle (on macOS only)

By ClipmodeGo
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def print_header(text):
    """Print a nicely formatted header."""
    print("\n" + "=" * 80)
    print(f"   {text}")
    print("=" * 80)

def run_script(script_name):
    """Run a Python script and return success status."""
    if not os.path.exists(script_name):
        print(f"Error: {script_name} not found.")
        return False
    
    print(f"Running {script_name}...")
    result = subprocess.run([sys.executable, script_name], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE, 
                           universal_newlines=True)
    
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error running {script_name}:")
        print(result.stderr)
        return False
    return True

def create_zip_package():
    """Create a ZIP package."""
    print_header("Creating ZIP Package")
    return run_script("create_zip_package.py")

def create_macos_dmg():
    """Create a macOS DMG."""
    print_header("Creating macOS DMG")
    
    # First, create the app icon if it doesn't exist
    if not os.path.exists("AppIcon.icns"):
        print("App icon not found. Creating one...")
        if not run_script("create_app_icon.py"):
            print("Warning: Failed to create app icon. Continuing without it.")
    
    # Now create the DMG
    return run_script("create_macos_dmg.py")

def verify_files_exist():
    """Verify that all required files exist."""
    required_files = [
        "main.py",
        "src/generator.py",
        "src/utils.py",
        "src/pyqt_gui.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("Error: The following required files are missing:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    return True

def main():
    """Main function to handle packaging."""
    print_header("Packaging Scramble Clip 2 for Distribution")
    
    if not verify_files_exist():
        return False
    
    # Always create the ZIP package
    zip_success = create_zip_package()
    
    # Create macOS specific packages if on macOS
    if sys.platform == "darwin":
        dmg_success = create_macos_dmg()
        if not dmg_success:
            print("Warning: Failed to create macOS DMG.")
    else:
        print("Not running on macOS, skipping DMG creation.")
    
    print_header("Packaging Complete")
    
    # List created package files
    print("Created package files:")
    for file in os.listdir("."):
        if file.endswith(".zip") or file.endswith(".dmg"):
            print(f"  - {file} ({os.path.getsize(file) / (1024*1024):.2f} MB)")
    
    # Print upload instructions
    print("\nTo upload to your website:")
    print("1. Copy the ZIP file (and DMG file if on macOS) to your web server")
    print("2. Create a download link to the files on your website")
    print("3. Consider adding installation instructions for your users")
    
    return zip_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 