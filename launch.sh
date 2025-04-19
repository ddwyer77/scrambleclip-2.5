#!/bin/bash

# Scramble Clip 2 Launcher for macOS/Linux
# Created by ClipmodeGo

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 to run Scramble Clip 2."
    exit 1
fi

# Run the application
echo "Launching Scramble Clip 2..."
python3 main.py

# If the application crashes, keep the terminal open
if [ $? -ne 0 ]; then
    echo "Scramble Clip 2 crashed. Press any key to close this window."
    read -n 1
fi 