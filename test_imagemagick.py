import os
from moviepy.config import get_setting, change_settings
from moviepy.editor import TextClip

def test_imagemagick():
    """Test if ImageMagick is properly configured with MoviePy."""
    
    # Get current ImageMagick setting
    current_setting = get_setting("IMAGEMAGICK_BINARY")
    print(f"Current ImageMagick binary setting: {current_setting}")
    
    # Check if the setting points to an existing file
    if current_setting == "unset" or not os.path.exists(current_setting):
        print("ImageMagick binary not properly configured or not found.")
        
        # Try to find ImageMagick binary
        possible_paths = [
            "/opt/homebrew/bin/convert",  # M1/M2 Mac typical path
            "/usr/local/bin/convert",     # Intel Mac typical path
            "/usr/bin/convert"            # Linux typical path
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found ImageMagick binary at: {path}")
                # Update MoviePy configuration
                change_settings({"IMAGEMAGICK_BINARY": path})
                print(f"Updated MoviePy configuration to use {path}")
                break
        else:
            print("Could not find ImageMagick binary in standard locations.")
            return False
    
    # Test creating a text clip
    try:
        print("Attempting to create a text clip with effects...")
        text = TextClip(
            "Testing ImageMagick", 
            font="Arial", 
            fontsize=70, 
            color="white",
            stroke_color="black",
            stroke_width=2,
            method='caption',
            size=(600, None)
        )
        print(f"Success! Created text clip with dimensions {text.size}")
        return True
    except Exception as e:
        print(f"Error creating text clip: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing ImageMagick integration with MoviePy...")
    success = test_imagemagick()
    
    if success:
        print("\nImageMagick is properly configured and working!")
    else:
        print("\nImageMagick configuration needs to be fixed.")
        print("You might need to manually set the path to the ImageMagick 'convert' binary.")
        print("Try adding this to your ~/.bashrc or ~/.zshrc file:")
        print("export IMAGEMAGICK_BINARY=/opt/homebrew/bin/convert  # Adjust path as needed") 