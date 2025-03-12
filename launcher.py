#!/usr/bin/env python3
"""
Scramble Clip 2 Launcher
A cross-platform launcher for Scramble Clip 2 by ClipmodeGo
"""

import os
import sys
import platform
import subprocess
import webbrowser
import time

# ASCII art logo for the console
LOGO = """
╔═════════════════════════════════════════════════╗
║  ███████╗ ██████╗██████╗  █████╗ ███╗   ███╗    ║
║  ██╔════╝██╔════╝██╔══██╗██╔══██╗████╗ ████║    ║
║  ███████╗██║     ██████╔╝███████║██╔████╔██║    ║
║  ╚════██║██║     ██╔══██╗██╔══██║██║╚██╔╝██║    ║
║  ███████║╚██████╗██║  ██║██║  ██║██║ ╚═╝ ██║    ║
║  ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝    ║
║   ██████╗██╗     ██╗██████╗     ██████╗          ║
║  ██╔════╝██║     ██║██╔══██╗   ██╔════╝          ║
║  ██║     ██║     ██║██████╔╝   ██║  ███╗         ║
║  ██║     ██║     ██║██╔═══╝    ██║   ██║         ║
║  ╚██████╗███████╗██║██║        ╚██████╔╝         ║
║   ╚═════╝╚══════╝╚═╝╚═╝         ╚═════╝          ║
╚═════════════════════════════════════════════════╝
            By ClipmodeGo
"""

def clear_screen():
    """Clear the terminal screen based on platform."""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def check_python_version():
    """Check if Python version is 3.6+."""
    version = sys.version_info
    return version.major == 3 and version.minor >= 6

def check_requirements():
    """Check if all required packages are installed."""
    required_packages = ['PyQt5', 'moviepy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_requirements(packages):
    """Install missing requirements."""
    print(f"\nInstalling required packages: {', '.join(packages)}")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Main launcher function."""
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    clear_screen()
    print("\033[92m" + LOGO + "\033[0m")  # Green text
    
    print("Scramble Clip 2 Launcher")
    print("------------------------\n")
    
    # Check Python version
    if not check_python_version():
        print("\033[91mError: Python 3.6 or higher is required.\033[0m")
        print(f"Your Python version: {sys.version}")
        print("\nPlease install a newer version of Python from https://www.python.org/downloads/")
        input("\nPress Enter to exit...")
        return False
    
    print(f"Python version: {sys.version.split()[0]} ✓")
    
    # Check requirements
    missing_packages = check_requirements()
    if missing_packages:
        print(f"\n\033[93mWarning: Some required packages are missing: {', '.join(missing_packages)}\033[0m")
        
        answer = input("Would you like to install them now? (y/n): ").strip().lower()
        if answer == 'y':
            if install_requirements(missing_packages):
                print("\033[92mAll packages installed successfully! ✓\033[0m")
            else:
                print("\033[91mFailed to install packages. Please install them manually:\033[0m")
                print(f"pip install {' '.join(missing_packages)}")
                input("\nPress Enter to continue anyway...")
        else:
            print("\nContinuing without installing missing packages...")
    else:
        print("All required packages installed ✓")
    
    print("\nStarting Scramble Clip 2...")
    try:
        if platform.system() == 'Windows':
            # Using Popen for Windows to avoid console window
            process = subprocess.Popen([sys.executable, "main.py"])
        else:
            # Simple call for Unix-like systems
            subprocess.call([sys.executable, "main.py"])
        print("\033[92mLaunched successfully!\033[0m")
        return True
    except Exception as e:
        print(f"\033[91mError launching Scramble Clip 2: {str(e)}\033[0m")
        input("\nPress Enter to exit...")
        return False

if __name__ == "__main__":
    success = main()
    # Wait a bit before exiting
    if success:
        time.sleep(2)  # Give the application time to start 