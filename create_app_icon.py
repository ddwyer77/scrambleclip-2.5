#!/usr/bin/env python3
"""
Create App Icon for Scramble Clip 2
This script creates a simple app icon (AppIcon.icns) for macOS
"""

import os
import sys
import subprocess
from pathlib import Path
import tempfile

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow is required to create the icon. Installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image, ImageDraw, ImageFont

# Icon configuration
ICON_SIZE = 1024  # Base size for the icon
BG_COLOR = (18, 18, 18)  # Dark background
FG_COLOR = (0, 230, 118)  # Green text
ICON_TEXT = "SC2"  # Text to display in the icon

def create_temp_iconset():
    """Create a temporary iconset directory with all required sizes."""
    temp_dir = tempfile.mkdtemp()
    iconset_path = Path(temp_dir) / "AppIcon.iconset"
    iconset_path.mkdir()
    
    # Create base icon image
    img = Image.new('RGB', (ICON_SIZE, ICON_SIZE), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Try to use a font if available, otherwise use default
    try:
        # Try to find a good font - system dependent
        font_size = int(ICON_SIZE * 0.45)
        try:
            font = ImageFont.truetype("Arial Bold.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()
                font_size = int(ICON_SIZE * 0.3)  # Smaller size for default font
    except:
        font = ImageFont.load_default()
        font_size = int(ICON_SIZE * 0.3)  # Smaller size for default font
    
    # Calculate text position to center it
    text_width = font.getlength(ICON_TEXT) if hasattr(font, 'getlength') else font_size * len(ICON_TEXT) * 0.6
    text_x = (ICON_SIZE - text_width) / 2
    text_y = (ICON_SIZE - font_size) / 2 - font_size * 0.1
    
    # Draw text
    draw.text((text_x, text_y), ICON_TEXT, font=font, fill=FG_COLOR)
    
    # Draw a circular background
    circle_margin = int(ICON_SIZE * 0.1)
    ellipse_coords = [circle_margin, circle_margin, ICON_SIZE - circle_margin, ICON_SIZE - circle_margin]
    draw.ellipse(ellipse_coords, outline=FG_COLOR, width=int(ICON_SIZE * 0.02))
    
    # Generate all required sizes for macOS
    icon_sizes = [16, 32, 64, 128, 256, 512, 1024]
    for size in icon_sizes:
        # Regular image
        resized_img = img.resize((size, size), Image.LANCZOS)
        resized_img.save(iconset_path / f"icon_{size}x{size}.png")
        
        # High-resolution (2x) image
        if size * 2 <= ICON_SIZE:
            double_size = size * 2
            resized_img = img.resize((double_size, double_size), Image.LANCZOS)
            resized_img.save(iconset_path / f"icon_{size}x{size}@2x.png")
    
    return iconset_path

def create_icns_file():
    """Create an ICNS file from the iconset."""
    print("Creating macOS app icon (AppIcon.icns)...")
    
    # Create the iconset
    iconset_path = create_temp_iconset()
    
    # Use iconutil (macOS only) to convert to icns
    output_path = Path("AppIcon.icns")
    if output_path.exists():
        output_path.unlink()
    
    cmd = ["iconutil", "-c", "icns", str(iconset_path)]
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    
    # Move the output file to the current directory
    output_icns = Path("AppIcon.icns")
    if output_icns.exists():
        print(f"Icon created successfully: {output_icns}")
        return True
    else:
        print(f"Failed to create icon: {process.stderr}")
        return False

def main():
    """Main function."""
    if sys.platform != "darwin":
        print("This script is designed to run on macOS.")
        return False
    
    return create_icns_file()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 