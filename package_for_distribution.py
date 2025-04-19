#!/usr/bin/env python3
"""
Package Scramble Clip 2 for distribution

This script creates:
1. A ZIP file with all necessary files for all platforms
2. A DMG file for macOS users
"""

import os
import sys
import platform
import shutil
import subprocess
import time
from zipfile import ZipFile, ZIP_DEFLATED

def create_zip_package():
    """Create a ZIP package with all necessary files"""
    print("Creating ZIP package...")
    
    # Ensure dist directory exists
    if not os.path.exists("dist"):
        os.makedirs("dist")
    
    # Define the zip filename
    zip_filename = "dist/ScrambleClip2.zip"
    
    # Create a new zip file
    with ZipFile(zip_filename, 'w', ZIP_DEFLATED) as zipf:
        # Add main Python files
        for file in os.listdir("."):
            if file.endswith(".py") or file.endswith(".sh") or file.endswith(".bat"):
                zipf.write(file)
        
        # Add src directory
        for root, _, files in os.walk("src"):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path)
        
        # Add assets directory
        for root, _, files in os.walk("assets"):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path)
        
        # Add requirements.txt
        if os.path.exists("requirements.txt"):
            zipf.write("requirements.txt")
        
        # Add README
        if os.path.exists("README.md"):
            zipf.write("README.md")
    
    print(f"ZIP package created at {os.path.abspath(zip_filename)}")
    return os.path.abspath(zip_filename)

def create_macos_dmg():
    """Create a DMG file for macOS users"""
    if platform.system() != "Darwin":
        print("DMG creation is only supported on macOS.")
        return None
    
    print("Creating macOS DMG package...")
    
    # Ensure dist directory exists
    if not os.path.exists("dist"):
        os.makedirs("dist")
    
    # Define the DMG filename
    dmg_filename = "dist/ScrambleClip2.dmg"
    
    # Create a temporary directory for app bundle
    temp_dir = "dist/temp_app"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # Create app bundle structure
    app_dir = os.path.join(temp_dir, "ScrambleClip2.app")
    contents_dir = os.path.join(app_dir, "Contents")
    macos_dir = os.path.join(contents_dir, "MacOS")
    resources_dir = os.path.join(contents_dir, "Resources")
    
    os.makedirs(macos_dir)
    os.makedirs(resources_dir)
    
    # Create Info.plist
    with open(os.path.join(contents_dir, "Info.plist"), "w") as f:
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>Scramble Clip 2</string>
    <key>CFBundleExecutable</key>
    <string>ScrambleClip2</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.clipmodego.scrambleclip2</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Scramble Clip 2</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>""")
    
    # Create executable shell script
    with open(os.path.join(macos_dir, "ScrambleClip2"), "w") as f:
        f.write("""#!/bin/bash
cd "$(dirname "$0")"
cd ../Resources
python3 main.py
""")
    
    # Make it executable
    os.chmod(os.path.join(macos_dir, "ScrambleClip2"), 0o755)
    
    # Copy Python files to Resources
    for file in os.listdir("."):
        if file.endswith(".py"):
            shutil.copy(file, resources_dir)
    
    # Copy src directory
    shutil.copytree("src", os.path.join(resources_dir, "src"))
    
    # Copy assets directory
    shutil.copytree("assets", os.path.join(resources_dir, "assets"))
    
    # Create outputs directory
    os.makedirs(os.path.join(resources_dir, "outputs"), exist_ok=True)
    
    # Copy requirements.txt
    if os.path.exists("requirements.txt"):
        shutil.copy("requirements.txt", resources_dir)
    
    # Create icon if available, otherwise use a placeholder
    icon_path = os.path.join("assets", "icon.png")
    if os.path.exists(icon_path):
        try:
            # Try to convert PNG to ICNS
            icns_path = os.path.join(resources_dir, "icon.icns")
            subprocess.run(["sips", "-s", "format", "icns", icon_path, "--out", icns_path], 
                          check=True, capture_output=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Warning: Could not convert icon to ICNS format.")
    
    # Create the DMG
    try:
        # Try to use create-dmg if available
        subprocess.run([
            "hdiutil", "create", "-volname", "Scramble Clip 2", 
            "-srcfolder", temp_dir, "-ov", "-format", "UDZO", dmg_filename
        ], check=True)
        print(f"DMG package created at {os.path.abspath(dmg_filename)}")
        return os.path.abspath(dmg_filename)
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Error creating DMG: {e}")
        return None
    finally:
        # Clean up temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def main():
    """Main packaging function"""
    print("Packaging Scramble Clip 2 for distribution...")
    start_time = time.time()
    
    # Create ZIP package
    zip_path = create_zip_package()
    
    # Create DMG package on macOS
    dmg_path = None
    if platform.system() == "Darwin":
        dmg_path = create_macos_dmg()
    
    # Print summary
    elapsed_time = time.time() - start_time
    print("\nPackaging completed in {:.2f} seconds.".format(elapsed_time))
    print("\nPackages created:")
    
    if zip_path:
        size_mb = os.path.getsize(zip_path) / (1024 * 1024)
        print(f"- ZIP: {zip_path} ({size_mb:.2f} MB)")
    
    if dmg_path:
        size_mb = os.path.getsize(dmg_path) / (1024 * 1024)
        print(f"- DMG: {dmg_path} ({size_mb:.2f} MB)")
    
    print("\nDistribution packages are ready!")

if __name__ == "__main__":
    main() 