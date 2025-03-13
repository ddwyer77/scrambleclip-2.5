#!/usr/bin/env python3
"""
Create ZIP package for Scramble Clip 2
This script creates a ZIP file for distribution of Scramble Clip 2
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
import datetime

# Configuration
APP_NAME = "Scramble Clip 2"
VERSION = "1.0"
ZIP_NAME = f"{APP_NAME.replace(' ', '-')}-{VERSION}.zip"

# Files and directories to exclude from the ZIP
EXCLUDE = [
    "__pycache__",
    ".git",
    ".gitignore",
    ".DS_Store",
    "*.app",
    "*.dmg",
    "dmg_temp",
    "*.zip",
    "create_zip_package.py",
    "create_macos_dmg.py",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "outputs/*.mp4",
    "outputs/*.mov",
]

def should_exclude(path):
    """Check if a path should be excluded from the ZIP."""
    path_str = str(path)
    for pattern in EXCLUDE:
        if pattern.startswith("*."):
            # Handle file extension patterns
            ext = pattern[1:]
            if path_str.endswith(ext):
                return True
        elif pattern in path_str:
            return True
    return False

def create_zip_package():
    """Create a ZIP file containing the application."""
    print(f"Creating ZIP package: {ZIP_NAME}")
    
    # Get the current directory
    root_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Create a timestamp for the ZIP file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = root_dir / f"{APP_NAME.replace(' ', '-')}-{VERSION}_{timestamp}.zip"
    
    # Create a ZIP file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(root_dir):
            # Convert to Path objects for easier handling
            root_path = Path(root)
            
            # Filter out directories to exclude
            dirs[:] = [d for d in dirs if not should_exclude(root_path / d)]
            
            # Add files to the ZIP
            for file in files:
                file_path = root_path / file
                if not should_exclude(file_path):
                    arcname = file_path.relative_to(root_dir)
                    print(f"Adding: {arcname}")
                    zipf.write(file_path, arcname)
    
    print(f"\nSuccess! ZIP package created: {zip_path}")
    print(f"File location: {os.path.abspath(zip_path)}")
    return True

def main():
    """Main function."""
    print(f"Packaging {APP_NAME} version {VERSION}")
    
    # Create the ZIP file
    if not create_zip_package():
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 