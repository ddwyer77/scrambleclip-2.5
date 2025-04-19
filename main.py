#!/usr/bin/env python3

import sys
import os
import traceback

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Apply Pillow compatibility patch
    print("Applying Pillow compatibility patch...")
    import src.pil_patch
    
    # Configure MoviePy to use the correct ImageMagick binary
    print("Configuring MoviePy with ImageMagick...")
    import moviepy_config
    
    print("Importing PyQt GUI application...")
    # Import GUI application
    from src.pyqt_gui import main
    
    if __name__ == "__main__":
        print("Starting PyQt application...")
        main()
except Exception as e:
    print(f"Error: {e}")
    print(traceback.format_exc()) 