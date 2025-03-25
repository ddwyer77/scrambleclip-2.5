import os
from src.generator import generate_batch
import glob
import shutil

def run_test_generation():
    """
    Generate a test video using the generator module without the GUI.
    """
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create test outputs directory if it doesn't exist
    test_output_dir = os.path.join(current_dir, "test_outputs")
    os.makedirs(test_output_dir, exist_ok=True)
    
    # Create audio directory if it doesn't exist
    audio_dir = os.path.join(current_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    # Copy the default audio file if it exists
    default_audio = "/Users/danieldwyer/Downloads/Pengu Library/audio.mp3"
    if os.path.exists(default_audio):
        audio_output = os.path.join(audio_dir, "audio.mp3")
        if not os.path.exists(audio_output):
            shutil.copy2(default_audio, audio_output)
            print(f"Copied audio file to: {audio_output}")
    
    # Find all mp4 files in the inputs directory
    input_dir = os.path.join(current_dir, "inputs")
    input_videos = glob.glob(os.path.join(input_dir, "*.mp4"))
    
    if not input_videos:
        print("No input videos found in the 'inputs' directory!")
        print(f"Please add some .mp4 files to: {input_dir}")
        return
    
    print(f"Found {len(input_videos)} input videos:")
    for video in input_videos:
        print(f"- {os.path.basename(video)}")
    
    # Find audio files
    audio_files = glob.glob(os.path.join(audio_dir, "*.mp3"))
    if audio_files:
        print(f"\nFound {len(audio_files)} audio files:")
        for audio in audio_files:
            print(f"- {os.path.basename(audio)}")
    else:
        print("\nNo audio files found in the 'audio' directory!")
    
    print("\nGenerating test video...")
    try:
        # Generate just one video for testing
        output_paths = generate_batch(
            input_videos=input_videos,
            audio_files=audio_files,  # Pass the audio files
            num_videos=1,  # Generate just one video for quick testing
            min_clips=8,
            max_clips=12,
            min_clip_duration=1.5,
            max_clip_duration=2.5,
            output_dir=test_output_dir,
            use_effects=True,  # Enable effects for testing
            progress_callback=lambda progress, message: print(f"Progress {progress}%: {message}")
        )
        
        if output_paths:
            print(f"\nTest video generated successfully!")
            print(f"Output video location: {output_paths[0]}")
            
            # Try to open the output folder
            try:
                if os.name == 'nt':  # Windows
                    os.system(f'explorer "{test_output_dir}"')
                elif os.name == 'posix':  # macOS and Linux
                    if os.system('which open') == 0:  # macOS
                        os.system(f'open "{test_output_dir}"')
                    else:  # Linux
                        os.system(f'xdg-open "{test_output_dir}"')
            except Exception as e:
                print(f"Note: Could not automatically open output folder: {e}")
                print(f"Please open the folder manually at: {test_output_dir}")
        
    except Exception as e:
        print(f"Error generating test video: {e}")

if __name__ == "__main__":
    run_test_generation() 