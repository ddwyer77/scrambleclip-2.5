#!/usr/bin/env python3
"""
Cross-platform launcher for Scramble Clip 2
This script checks for required dependencies and launches the application
"""

import os
import sys
import subprocess
import platform

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import moviepy
        import numpy
        import cv2
        from PIL import Image
        print("All dependencies are installed.")
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        
        # Ask user if they want to install dependencies
        response = input("Would you like to install missing dependencies? (y/n): ")
        if response.lower() in ['y', 'yes']:
            try:
                print("Installing dependencies...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
                print("Dependencies installed successfully.")
                return True
            except Exception as e:
                print(f"Error installing dependencies: {e}")
                input("Press Enter to exit...")
                return False
        else:
            print("Cannot run without required dependencies.")
            input("Press Enter to exit...")
            return False

def launch_app():
    """Launch the main application"""
    print("Launching Scramble Clip 2...")
    
    try:
        # Use the appropriate command based on platform
        if platform.system() == "Windows":
            os.system("python main.py")
        else:
            os.system("python3 main.py")
            
        return True
    except Exception as e:
        print(f"Error launching application: {e}")
        input("Press Enter to exit...")
        return False

if __name__ == "__main__":
    print("Scramble Clip 2 Launcher")
    print("========================")
    
    if check_dependencies():
        launch_app() 