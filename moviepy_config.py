import os
from moviepy.config import change_settings

def configure_moviepy():
    """Configure MoviePy to use the correct ImageMagick binary path."""
    
    # List of possible ImageMagick binary paths
    possible_paths = [
        "/opt/homebrew/bin/convert",  # M1/M2 Mac typical path
        "/usr/local/bin/convert",     # Intel Mac typical path
        "/usr/bin/convert"            # Linux typical path
    ]
    
    # Find the first path that exists
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found ImageMagick at: {path}")
            change_settings({"IMAGEMAGICK_BINARY": path})
            return True
    
    print("Warning: ImageMagick not found in standard locations")
    return False

# Auto-configure when imported
configure_moviepy() 