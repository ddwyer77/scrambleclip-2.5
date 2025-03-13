#!/bin/bash
# Scramble Clip 2 Mac Launcher
# By ClipmodeGo

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Display a cool ASCII art header
echo "
██████╗ ██╗     ██╗██████╗ ███╗   ███╗ ██████╗ ██████╗ ███████╗     ██████╗  ██████╗ 
██╔════╝██║     ██║██╔══██╗████╗ ████║██╔═══██╗██╔══██╗██╔════╝    ██╔════╝ ██╔═══██╗
██║     ██║     ██║██████╔╝██╔████╔██║██║   ██║██║  ██║█████╗      ██║  ███╗██║   ██║
██║     ██║     ██║██╔═══╝ ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝      ██║   ██║██║   ██║
╚██████╗███████╗██║██║     ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗    ╚██████╔╝╚██████╔╝
 ╚═════╝╚══════╝╚═╝╚═╝     ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝     ╚═════╝  ╚═════╝ 
                             Scramble Clip 2                                          
                           By ClipmodeGo                                             
"

# Check for Python 3.6+
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
if [[ -z "$python_version" ]]; then
    echo "⚠️  Python 3 is not installed or not in PATH."
    echo "Please install Python 3.6 or higher from python.org"
    echo "Press Return to continue anyway (may not work)..."
    read -n 1
elif [[ $(echo "$python_version < 3.6" | bc) -eq 1 ]]; then
    echo "⚠️  Python version $python_version detected. Version 3.6+ is recommended."
    echo "Press Return to continue anyway..."
    read -n 1
else
    echo "✅ Python version $python_version detected."
fi

# Check for required packages
echo "Checking required packages..."
packages=("PyQt5" "moviepy")
missing=()

for pkg in "${packages[@]}"; do
    if ! python3 -c "import $pkg" &>/dev/null; then
        missing+=("$pkg")
    fi
done

if [ ${#missing[@]} -gt 0 ]; then
    echo "⚠️  Missing packages: ${missing[*]}"
    read -p "Install them now? (y/n): " answer
    if [[ $answer == "y" ]]; then
        echo "Installing packages..."
        python3 -m pip install "${missing[@]}"
    fi
fi

echo "Launching Scramble Clip 2..."
echo "--------------------------------"

# Run the application
python3 "$DIR/main.py"

# Check if the application exited with an error
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo "⚠️  Application crashed with error code $exit_code"
    echo "Press Return to exit..."
    read -n 1
fi 