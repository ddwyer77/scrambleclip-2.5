import os
import sys
import traceback
from src.generator import generate_batch

# Set up debugging
import logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_progress_callback(progress, status):
    print(f"PROGRESS: {progress}% - {status}")

def main():
    try:
        # Simple paths with no special characters
        input_video_path = os.path.abspath("assets/input_videos")
        input_audio_path = os.path.abspath("assets/input_audio/audio.mp3")
        output_path = os.path.expanduser("~/Desktop/scramble_test_output")
        
        print(f"Input video path: {input_video_path}")
        print(f"Input audio path: {input_audio_path}")
        print(f"Output path: {output_path}")
        
        # Ensure output directory exists
        os.makedirs(output_path, exist_ok=True)
        
        # Test text overlay feature
        custom_text = "TEST TEXT OVERLAY"
        print(f"Testing with text overlay. Custom text: '{custom_text}'")
        
        # Generate just 1 video for testing with text overlay enabled
        print("Starting generation...")
        generate_batch(
            num_videos=1,
            input_video_path=input_video_path,
            input_audio_path=input_audio_path,
            output_path=output_path,
            progress_callback=debug_progress_callback,
            use_ai=True,
            use_effects=False,
            use_text=True,  # Enable text overlay
            custom_text=custom_text  # Use custom text
        )
        
        # Check if video was created
        output_files = [f for f in os.listdir(output_path) if f.endswith('.mp4')]
        print(f"Output files: {output_files}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 