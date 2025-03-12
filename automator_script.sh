#!/bin/bash
# Scramble Clip 2 Automator Script
# This script is designed to be used with macOS Automator to create a quick launcher app

# Set the application path - replace this with the actual path to your application
APP_PATH="/Users/danieldwyer/Desktop/scramble_clip2"

# Navigate to the app directory
cd "$APP_PATH"

# Run the Python application
python3 "$APP_PATH/main.py"

# Instructions for using this script with Automator:
# 1. Open Automator.app
# 2. Create a new Application
# 3. Add a "Run Shell Script" action
# 4. Copy this entire script into the shell script field
# 5. Update the APP_PATH variable to the correct path to your Scramble Clip 2 folder
# 6. Save the Automator application with a name like "Scramble Clip 2"
# 7. Optionally, add a custom icon to the saved application 