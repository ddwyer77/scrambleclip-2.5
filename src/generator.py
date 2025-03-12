import os, random
import warnings
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, vfx
from src.utils import get_video_files, get_random_clip, pad_clip_to_ratio

# Suppress MoviePy warnings that might confuse users
warnings.filterwarnings("ignore", category=UserWarning)

# Default paths (can be overridden when called from GUI)
INPUT_VIDEO_PATH = "../assets/input_videos"
INPUT_AUDIO_PATH = "../assets/input_audio/audio.mp3"
OUTPUT_PATH = "../outputs"

def generate_batch(num_videos=15, input_video_path=None, input_audio_path=None, output_path=None, progress_callback=None):
    """
    Generate a batch of randomized video clips.
    
    Args:
        num_videos: Number of videos to generate
        input_video_path: Path to input videos directory
        input_audio_path: Path to input audio file
        output_path: Path to save output videos
        progress_callback: Function to call with progress updates
    """
    # Use provided paths or fallback to defaults
    video_path = input_video_path or INPUT_VIDEO_PATH
    audio_path = input_audio_path or INPUT_AUDIO_PATH
    out_path = output_path or OUTPUT_PATH
    
    # Find video files
    video_files = get_video_files(video_path)
    if len(video_files) == 0:
        raise ValueError(f"No video files (MP4/MOV) found in {video_path}. Please add video files.")
    elif len(video_files) < 4:
        # Warn but allow generation with fewer videos
        if progress_callback:
            progress_callback(0, f"Warning: Only {len(video_files)} videos found. Some clips will be repeated.")
    
    try:
        # Load audio
        if progress_callback:
            progress_callback(0, f"Loading audio file: {os.path.basename(audio_path)}")
            
        audio = AudioFileClip(audio_path)
        audio = audio.fx(vfx.loop, duration=16) if audio.duration < 16 else audio.subclip(0,16)
        
        # Generate each video
        for i in range(num_videos):
            try:
                # Update progress
                if progress_callback:
                    progress = int((i / num_videos) * 80)  # 80% for generating, 20% for writing
                    progress_callback(progress, f"Generating video {i+1}/{num_videos}")
                
                # Randomly select videos (with replacement if needed)
                if len(video_files) >= 4:
                    selected_videos = random.sample(video_files, 4)
                else:
                    # Use all videos and duplicate some
                    selected_videos = random.choices(video_files, k=4)
                
                clips = []
                
                # Process each selected video
                for j, vid in enumerate(selected_videos):
                    try:
                        if progress_callback:
                            progress_callback(progress, f"Processing clip {j+1}/4 for video {i+1}")
                            
                        # Get random clip with variable duration
                        clip_duration = random.uniform(3, 5)  # ±1 sec variability
                        clip = get_random_clip(vid, duration=clip_duration)
                        
                        # Pad to target aspect ratio
                        padded_clip = pad_clip_to_ratio(clip)
                        clips.append(padded_clip)
                    except Exception as e:
                        # If a clip fails, try to get another one
                        if progress_callback:
                            progress_callback(progress, f"Warning: Failed to process clip from {os.path.basename(vid)}: {str(e)}")
                            
                        # Try to get another clip from a random video
                        fallback_vid = random.choice(video_files)
                        try:
                            clip = get_random_clip(fallback_vid, duration=4)
                            padded_clip = pad_clip_to_ratio(clip)
                            clips.append(padded_clip)
                        except:
                            # If still failing, create a black clip as placeholder
                            if len(clips) > 0:
                                # Use the first successful clip again
                                clips.append(clips[0].copy())
                            else:
                                # Skip this video if we can't get any clips
                                raise ValueError("Could not process any clips for this video")
                
                # Make sure we have enough clips
                while len(clips) < 4:
                    if len(clips) > 0:
                        clips.append(random.choice(clips).copy())
                    else:
                        raise ValueError("Failed to create any usable clips")
                
                # Create final video
                if progress_callback:
                    progress_callback(progress, f"Creating video {i+1}/{num_videos}")
                    
                # Concatenate clips and add audio    
                final_clip = concatenate_videoclips(clips, method='compose').set_audio(audio)
                output_file = f"{out_path}/output_{str(i+1).zfill(2)}.mp4"
                final_clip = final_clip.resize(height=1920)
                
                # Define callback for writing progress
                def writing_callback(t):
                    if progress_callback:
                        writing_progress = int(t / final_clip.duration * 20)
                        total_progress = min(80 + writing_progress, 99)
                        progress_callback(total_progress, f"Writing video {i+1}/{num_videos}")
                
                # Write final video
                if progress_callback:
                    progress_callback(80, f"Writing video {i+1}/{num_videos}")
                    
                # Try with different parameters depending on MoviePy version
                try:
                    final_clip.write_videofile(
                        output_file, 
                        codec="libx264", 
                        audio_codec="aac",
                        logger=None,
                        callback=writing_callback
                    )
                except TypeError as e:
                    # If the callback or logger parameter fails, try without them
                    if "got an unexpected keyword argument" in str(e):
                        if progress_callback:
                            progress_callback(80, f"Using alternate writing method for video {i+1}/{num_videos}")
                        final_clip.write_videofile(
                            output_file, 
                            codec="libx264", 
                            audio_codec="aac"
                        )
                    else:
                        raise
                
                # Clean up clips
                for c in clips:
                    try:
                        c.close()
                    except:
                        pass
                try:
                    final_clip.close()
                except:
                    pass
                    
            except Exception as e:
                # If one video fails, try to continue with others
                if progress_callback:
                    progress_callback(0, f"Error generating video {i+1}: {str(e)}")
        
        # Signal completion
        if progress_callback:
            progress_callback(100, "Generation complete!")
            
    except Exception as e:
        # Handle overall errors
        if progress_callback:
            progress_callback(0, f"Error: {str(e)}")
        raise
    finally:
        # Try to clean up audio
        try:
            audio.close()
        except:
            pass

if __name__ == "__main__":
    generate_batch()
