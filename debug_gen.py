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
        
        # Generate just 1 video for testing
        print("Starting generation...")
        generate_batch(
            input_videos=input_video_path,
            audio_files=[input_audio_path],
            num_videos=1,
            output_dir=output_path,
            progress_callback=debug_progress_callback,
            target_duration=16
        )
        
        # Check if video was created
        output_files = [f for f in os.listdir(output_path) if f.endswith('.mp4')]
        print(f"Output files: {output_files}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 