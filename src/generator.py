import os, random
import warnings
import hashlib
import numpy as np
from collections import defaultdict
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, TextClip, ColorClip
# Import specific effects for transitions only
from moviepy.video.fx.loop import loop
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.video.fx.crop import crop
from moviepy.video.fx.colorx import colorx  # used for preview fades
from moviepy.video.fx.speedx import speedx
import subprocess, tempfile, os, shutil

from src.utils import get_video_files, get_random_clip, pad_clip_to_ratio, prepare_clip_for_concat
from src.video_analysis import VideoContentAnalyzer

# Suppress MoviePy warnings that might confuse users
warnings.filterwarnings("ignore", category=UserWarning)

# Default paths (can be overridden when called from GUI)
INPUT_VIDEO_PATH = "../assets/input_videos"
INPUT_AUDIO_PATH = "../assets/input_audio/audio.mp3"
OUTPUT_PATH = "../outputs"

# Initialize video analyzer
video_analyzer = VideoContentAnalyzer()

# Time-margin (sec) we leave between chosen sub-clip end and source video end to avoid ffprobe rounding
SAFE_MARGIN = 0.25  # seconds

def generate_batch(input_videos, audio_files=None, num_videos=5, min_clips=10, max_clips=30, 
                   min_clip_duration=1.5, max_clip_duration=3.5, output_dir="outputs", base_name="output",
                   use_effects=False, use_text=False, custom_text=None,
                   font_name="Arial", bold=False, italic=False, underline=False,
                   text_position="top", speed_factor=1.0, effects_intensity=50, effects_style="classic",
                   overlay_video_path=None,
                   progress_callback=None, target_duration=16.0):
    """
    Generate a batch of videos by randomly selecting clips from input videos
    and concatenating them.
    
    Parameters:
        input_videos (list): List of paths to input video files
        audio_files (list, optional): List of paths to audio files
        num_videos (int): Number of videos to generate in batch
        min_clips (int): Minimum number of clips per output video
        max_clips (int): Maximum number of clips per output video
        min_clip_duration (float): Minimum duration of each clip in seconds
        max_clip_duration (float): Maximum duration of each clip in seconds
        output_dir (str): Directory to save output videos
        base_name (str): Base name for output video files
        use_effects (bool): Whether to use AI effects and transitions
        use_text (bool): Whether to add text overlay to videos
        custom_text (str): Custom text to use (if None, random captions will be used)
        font_name (str): Font name to use for text overlay
        bold (bool): Whether to use bold font for text overlay
        italic (bool): Whether to use italic font for text overlay
        underline (bool): Whether to use underline font for text overlay
        text_position (str): "top", "center", or "bottom" overlay region
        speed_factor (float): Speed multiplier for final output
        effects_intensity (int): 0-100 slider controlling how strong effects are
        effects_style (str): classic or graincore etc.
        overlay_video_path (str, optional): Path to an overlay video
        progress_callback (callable): Function to report progress (progress_pct, status_message)
        target_duration (float): Target duration for output videos in seconds
    
    Returns:
        list: Paths to the generated video files
    """
    # Target duration for output videos (in seconds)
    TARGET_DURATION = target_duration
    
    if not input_videos:
        raise ValueError("No input videos provided")

    if progress_callback:
        progress_callback(0, f"Loading {len(input_videos)} videos...")
    else:
        print(f"Loading {len(input_videos)} videos...")
    
    # Load all input videos as MoviePy clips
    try:
        input_clips = [VideoFileClip(video_path) for video_path in input_videos]
    except Exception as e:
        # If we fail to load some videos, try to load them one by one to identify which ones work
        input_clips = []
        for video_path in input_videos:
            try:
                clip = VideoFileClip(video_path)
                input_clips.append(clip)
                if progress_callback:
                    progress_callback(5, f"Successfully loaded {os.path.basename(video_path)}")
                else:
                    print(f"Successfully loaded {video_path}")
            except Exception as e:
                if progress_callback:
                    progress_callback(5, f"Failed to load {os.path.basename(video_path)}: {e}")
                else:
                    print(f"Failed to load {video_path}: {e}")
    
    if not input_clips:
        raise ValueError("No valid input videos could be loaded")
    
    # Check if we have enough input clips
    if len(input_clips) < 2:
        if progress_callback:
            progress_callback(5, "Warning: Only one input video available. This may limit clip variety.")
        else:
            print("Warning: Only one input video available. This may limit clip variety.")
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create a global history of used clip segments across all videos in batch
    # This tracks which parts of which clips have been used to avoid reuse across the batch
    clip_history = {}  # Maps clip_index to a list of (start_time, end_time) tuples
    
    # Track visual similarity of clips to avoid similar looking clips
    # Create a visual fingerprint for each video to compare similarity
    if len(input_clips) > 1:  # Only calculate if we have multiple clips
        if progress_callback:
            progress_callback(5, "Creating visual signatures for clip diversity...")
        visual_signatures = create_video_signatures(input_clips)
    else:
        visual_signatures = None
        
    output_paths = []
    
    # Set consistent dimensions for output videos
    TARGET_WIDTH = 1080
    TARGET_HEIGHT = 1920
    
    # Normalize intensity between 0 and 1 for internal use
    intensity_norm = max(0, min(effects_intensity, 100)) / 100.0
    
    for i in range(num_videos):
        # Calculate overall progress: each video is worth (90/num_videos)% of progress
        base_progress = 10 + (i * (80 / num_videos))
        
        if progress_callback:
            progress_callback(int(base_progress), f"Building video {i+1}/{num_videos}...")
        else:
            print(f"Building {output_dir}/{base_name}_{i+1:02d}.mp4 using MoviePy...")
        
        output_path = os.path.join(output_dir, f"{base_name}_{i+1:02d}.mp4")
        
        # Calculate clip parameters based on target duration
        # For 16 second videos, aim for 8-12 clips with 1.5-2.5 seconds each
        min_clip_count = 8
        max_clip_count = 12
        num_clips = random.randint(min_clip_count, max_clip_count)
        
        # Calculate average clip duration to fit target duration
        avg_clip_duration = TARGET_DURATION / num_clips
        # Add some variation around the average
        min_clip_dur = max(1.5, avg_clip_duration * 0.8)  # Min 1.5 seconds
        max_clip_dur = min(3.0, avg_clip_duration * 1.2)  # Max 3.0 seconds
        
        # Randomly select clips and durations
        selected_clips = []
        total_duration = 0
        
        # Track the already used clips for this video to avoid repetition
        used_clips_memory = []
        memory_size = min(5, len(input_clips) // 2)  # Remember last 5 clips or half of available clips
        
        # Initialize local clip history for this video
        local_clip_history = defaultdict(list)
        
        for j in range(num_clips):
            # Progress update for clip selection
            clip_progress = base_progress + ((j / num_clips) * (20 / num_videos))
            if progress_callback:
                progress_callback(int(clip_progress), f"Selecting clip {j+1}/{num_clips} for video {i+1}/{num_videos}")
            
            # Get available clip indices, avoiding recently used clips
            available_clip_indices = list(range(len(input_clips)))
            
            # Remove recently used clips from consideration
            for used_idx in used_clips_memory:
                if used_idx in available_clip_indices and len(available_clip_indices) > 1:
                    available_clip_indices.remove(used_idx)
            
            # If we have visual signatures, try to select dissimilar clips
            if visual_signatures and len(available_clip_indices) > 1:
                # If we have at least one selected clip already, try to find a dissimilar one
                if selected_clips:
                    clip_index = select_dissimilar_clip(
                        available_clip_indices, 
                        used_clips_memory, 
                        visual_signatures
                    )
                else:
                    # For the first clip, just choose randomly
                    clip_index = random.choice(available_clip_indices)
            else:
                # If no visual signatures or only one clip available, choose randomly
                clip_index = random.choice(available_clip_indices)
                
            input_clip = input_clips[clip_index]
            
            # Add to used clips memory
            used_clips_memory.append(clip_index)
            if len(used_clips_memory) > memory_size:
                used_clips_memory.pop(0)  # Remove oldest
            
            # Avoid selecting the same clip consecutively
            if selected_clips:
                last_clip_index = used_clips_memory[-1]  # Use the last used clip index
                if clip_index == last_clip_index:
                    available_clip_indices.remove(clip_index)
                    if available_clip_indices:
                        clip_index = random.choice(available_clip_indices)
                        input_clip = input_clips[clip_index]

            # Calculate remaining duration needed to hit the target
            remaining_clips = num_clips - j
            remaining_duration = max(0, TARGET_DURATION - total_duration)
            
            # Adjust duration for this clip
            if remaining_clips > 1:
                # Leave some duration for remaining clips
                max_this_clip = min(max_clip_dur, remaining_duration / remaining_clips * 1.5)
                clip_duration = random.uniform(min_clip_dur, max_this_clip)
            else:
                # Last clip - use remaining duration
                clip_duration = min(max_clip_dur, remaining_duration)
                clip_duration = max(min_clip_dur, clip_duration)  # Ensure minimum duration
            
            # Attempt to find an available segment with a limited retry loop
            attempts = 0
            max_attempts = 20
            available_segments = []
            while attempts < max_attempts and not available_segments:
                available_segments = find_available_segments(
                    clip_index, clip_duration, input_clip.duration,
                    global_history=None,
                    local_history=local_clip_history.get(clip_index, [])
                )
                if available_segments:
                    break
                # Pick another clip index and retry
                if len(available_clip_indices) > 1:
                    available_clip_indices.remove(clip_index)  # Remove the failed clip index
                    clip_index = random.choice(available_clip_indices)
                    input_clip = input_clips[clip_index]
                else:
                    # If we only have one clip left, try to use it anyway
                    break
                attempts += 1
            
            if not available_segments:
                # If we couldn't find a free segment, try to use any part of the clip
                if input_clip.duration >= clip_duration:
                    start_time = random.uniform(0, input_clip.duration - clip_duration)
                    available_segments = [(start_time, input_clip.duration)]
                else:
                    # If the clip is too short, skip it
                    if progress_callback:
                        progress_callback(int(clip_progress), f"Skipping clip {j+1}/{num_clips} - too short")
                    continue
            
            # Choose a random segment from available ones with a safety margin so we don't hit EOF
            segment_start, segment_end = random.choice(available_segments)
            max_start = max(segment_start, segment_end - clip_duration - SAFE_MARGIN)
            if max_start < segment_start:
                max_start = segment_start  # fallback
            start_time = random.uniform(segment_start, max_start)
            
            # Record this usage in both global and local history
            used_segment = (start_time, start_time + clip_duration)
            if clip_index not in clip_history:
                clip_history[clip_index] = []
            clip_history[clip_index].append(used_segment)
            
            if clip_index not in local_clip_history:
                local_clip_history[clip_index] = []
            local_clip_history[clip_index].append(used_segment)
            
            # Extract the subclip
            try:
                # Robust extraction – retry a few times if we get a zero-length clip (metadata edge-cases)
                retry = 0
                subclip = None
                while retry < 5:
                    sc = input_clip.subclip(start_time, start_time + clip_duration)
                    if sc.duration >= clip_duration - 0.05:  # accept small drift
                        subclip = sc
                        break
                    # Otherwise pick a new start inside the same segment
                    start_time = random.uniform(segment_start, max_start)
                    retry += 1
                if subclip is None:
                    raise ValueError("Could not create valid subclip after retries")
                
                # Ensure consistent dimensions and padding for all clips
                processed_clip = ensure_consistent_dimensions(subclip)
                
                # Apply AI-powered effects if enabled (but with reduced probability)
                if use_effects and intensity_norm > 0 and random.random() < (0.3 + 0.4*intensity_norm):
                    try:
                        processed_clip = apply_smart_effects(processed_clip, intensity=intensity_norm)
                    except Exception as e:
                        print(f"Error applying effects to clip: {e}")
                
                # Verify the clip is valid before adding it
                if processed_clip is not None and processed_clip.duration > 0:
                    selected_clips.append(processed_clip)
                    total_duration += clip_duration
                else:
                    print(f"Warning: Invalid processed clip, skipping")
                    continue
                
            except Exception as e:
                print(f"Error processing clip: {e}")
                continue
            
            # If we've reached the target duration, stop adding clips
            if total_duration >= TARGET_DURATION:
                break
        
        # If we don't have enough duration, add more clips
        while total_duration < TARGET_DURATION and len(selected_clips) < max_clip_count * 2:
            # Try to add more clips to reach target duration
            try:
                # Select a new clip
                available_clip_indices = list(range(len(input_clips)))
                clip_index = random.choice(available_clip_indices)
                input_clip = input_clips[clip_index]
                
                # Calculate remaining duration needed
                remaining_duration = TARGET_DURATION - total_duration
                clip_duration = min(max_clip_dur, remaining_duration)
                clip_duration = max(min_clip_dur, clip_duration)
                
                # Find available segment
                available_segments = find_available_segments(
                    clip_index, clip_duration, input_clip.duration,
                    global_history=None,
                    local_history=local_clip_history.get(clip_index, [])
                )
                
                # If no available segments, break to avoid infinite loop
                if not available_segments:
                    if progress_callback:
                        progress_callback(int(base_progress), "No more available segments, stopping additional clip addition")
                    break
                
                if available_segments:
                    segment_start, segment_end = random.choice(available_segments)
                    max_start = max(segment_start, segment_end - clip_duration - SAFE_MARGIN)
                    if max_start < segment_start:
                        max_start = segment_start  # fallback
                    start_time = random.uniform(segment_start, max_start)
                    
                    # Extract and process the subclip
                    subclip = input_clip.subclip(start_time, start_time + clip_duration)
                    processed_clip = ensure_consistent_dimensions(subclip)
                    
                    if use_effects and intensity_norm > 0 and random.random() < (0.3 + 0.4*intensity_norm):
                        try:
                            processed_clip = apply_smart_effects(processed_clip, intensity=intensity_norm)
                        except Exception as e:
                            print(f"Error applying effects to clip: {e}")
                    
                    # Verify the clip is valid before adding it
                    if processed_clip is not None and processed_clip.duration > 0:
                        selected_clips.append(processed_clip)
                        total_duration += clip_duration
                        
                        # Record usage
                        used_segment = (start_time, start_time + clip_duration)
                        if clip_index not in clip_history:
                            clip_history[clip_index] = []
                        clip_history[clip_index].append(used_segment)
                    else:
                        print(f"Warning: Invalid processed clip, skipping")
                        continue
                    
            except Exception as e:
                print(f"Error adding additional clip: {e}")
                break
        
        # If still short after attempts, try to grab an ultra-short slice (<=1s) from random clips
        ultra_attempts = 0
        while total_duration < TARGET_DURATION - 0.05 and ultra_attempts < 10:
            clip_idx = random.randrange(len(input_clips))
            base_clip = input_clips[clip_idx]
            seg_len = min(1.0, TARGET_DURATION - total_duration)
            if base_clip.duration <= seg_len + 0.1:
                seg_start = 0
            else:
                seg_start = random.uniform(0, base_clip.duration - seg_len)
            seg_end = seg_start + seg_len
            seg = base_clip.subclip(seg_start, seg_end)
            seg = ensure_consistent_dimensions(seg)
            if seg.duration > 0:
                selected_clips.append(seg)
                total_duration += seg.duration
            else:
                ultra_attempts += 1
                continue

        # Final safety: if still short, loop last clip
        if total_duration < TARGET_DURATION - 0.05:
            last_clip = selected_clips[-1]
            pad_needed = TARGET_DURATION - total_duration
            padded = loop(last_clip, duration=last_clip.duration + pad_needed)
            if padded is not None and padded.duration > 0:
                selected_clips[-1] = padded
                total_duration = TARGET_DURATION
        
        # Ensure we have at least one valid clip
        if not selected_clips or len(selected_clips) == 0:
            # Warn and fallback to using the first input video clip
            if progress_callback:
                progress_callback(int(base_progress), f"No valid clips for video {i+1}, using fallback clip.")
            else:
                print(f"No valid clips for {output_path}, using fallback clip.")
            # Fallback: take the first clip and loop/subclip to match target duration
            base_clip = input_clips[0]
            # Determine subclip duration
            sub_dur = min(TARGET_DURATION, base_clip.duration)
            fallback_clip = base_clip.subclip(0, sub_dur)
            fallback_clip = ensure_consistent_dimensions(fallback_clip)
            if sub_dur < TARGET_DURATION:
                fallback_clip = loop(fallback_clip, duration=TARGET_DURATION)
            selected_clips = [fallback_clip]
            total_duration = TARGET_DURATION
        
        final_clip = None

        try:
            # Progress update for effect stage
            effect_progress = base_progress + (60 / num_videos)
            if progress_callback:
                progress_callback(int(effect_progress), f"Applying effects and transitions for video {i+1}/{num_videos}")
            
            # Ensure we have valid clips before proceeding
            if not selected_clips or len(selected_clips) == 0:
                raise ValueError("No valid clips available for concatenation")
            
            # Verify all clips are valid before concatenation
            valid_clips = []
            for clip in selected_clips:
                if clip is not None and clip.duration > 0:
                    valid_clips.append(clip)
                else:
                    print(f"Warning: Invalid clip found, skipping")
            
            if not valid_clips:
                raise ValueError("No valid clips available after validation")
            
            selected_clips = valid_clips  # Use only valid clips
            
            # If we're using effects, add simple transitions between clips
            if use_effects and intensity_norm > 0:
                # Choose effects pipeline based on style
                if effects_style == "graincore":
                    # Hardcore glitchy B&W aesthetic: strong contrast, noise, and frame blending
                    filter_str = (
                        "format=gray,"
                        "eq=contrast=5:brightness=-0.2,"
                        # heavy static noise
                        "noise=alls=100:allf=u+random,"
                        # blending adjacent frames for glitch flicker
                        "tblend=all_mode=difference:opacity=0.8,"
                        "format=yuv420p"
                    )
                else:
                    pass  # Graincore effect now applied in FFmpeg stage

                # Classic transitions (MoviePy fades only)
                processed = []
                for idx, clip in enumerate(selected_clips):
                    c = clip
                    if idx == 0:
                        c = c.fx(fadein, 0.4)
                    if idx == len(selected_clips) - 1:
                        c = c.fx(fadeout, 0.4)
                    # Subtle brightness boost for variety
                    c = colorx(c, 1.03)
                    processed.append(c)

                # Concatenate with 0.3-second cross-fade between clips
                final_clip = concatenate_videoclips(processed, method="compose", padding=-0.3)
            else:
                # Simple concatenation without transitions
                final_clip = concatenate_videoclips(selected_clips)
            
            # Apply global speed factor if not 1.0
            if abs(speed_factor - 1.0) > 0.01:
                final_clip = final_clip.fx(speedx, speed_factor)

                # If speeding up shortened the clip, pad/loop to ensure 16-s output
                if final_clip.duration < TARGET_DURATION - 0.05:
                    try:
                        pad_needed = TARGET_DURATION - final_clip.duration
                        # Loop the clip end portion to pad
                        final_clip = loop(final_clip, duration=final_clip.duration + pad_needed)
                    except Exception as le:
                        print(f"Warning: could not loop for padding: {le}")
                elif final_clip.duration > TARGET_DURATION + 0.05:
                    # Trim if overshoot
                    final_clip = final_clip.subclip(0, TARGET_DURATION)

            # Check final clip dimensions and ensure they're correct
            final_clip = ensure_consistent_dimensions(final_clip)
            
            # Check if the final clip is too long and trim if necessary
            if final_clip.duration > TARGET_DURATION + 1:  # Allow 1 second buffer
                if progress_callback:
                    progress_callback(int(effect_progress), f"Trimming video to target duration ({TARGET_DURATION}s)")
                final_clip = final_clip.subclip(0, TARGET_DURATION)
            
            # Add text overlay if enabled
            if use_text:
                text_progress = base_progress + (65 / num_videos)
                if progress_callback:
                    progress_callback(int(text_progress), f"Adding text overlay to video {i+1}/{num_videos}")
                
                try:
                    # Use custom text if provided, otherwise generate a random caption
                    if custom_text:
                        caption = custom_text
                    else:
                        # Generate a random caption
                        captions = [
                            "WATCH TILL THE END 😱",
                            "POV: When the beat drops 🔥",
                            "This is INSANE 🤯",
                            "Wait for it... 👀",
                            "Best moments 💯",
                            "Try not to be amazed 😮",
                            "Crazy skills 💪",
                            "Ultimate compilation 🏆",
                            "The perfect edit doesn't exi- 😲",
                            "Caught in 4K 📸",
                            "Vibe check ✅",
                            f"Part {i+1} 🎬"
                        ]
                        caption = random.choice(captions)
                    
                    # Create text overlay
                    txt_clip = create_text_overlay(
                        caption,
                        (final_clip.w, final_clip.h),
                        position=text_position,
                        font_name=font_name,
                        bold=bold,
                        italic=italic,
                        underline=underline,
                        fontsize=int(final_clip.w * 0.07),  # Scale font to video width
                        color="white",
                        bg_color=(0, 0, 0, 0.6),  # Semi-transparent black
                        stroke_color="black",
                        stroke_width=2
                    )
                    
                    # Add text to the video if creation was successful
                    if txt_clip is not None:
                        # Ensure the text duration matches the video
                        txt_clip = txt_clip.set_duration(final_clip.duration)
                        
                        # Composite the text on top of the video
                        final_clip = CompositeVideoClip([final_clip, txt_clip])
                        
                        if progress_callback:
                            progress_callback(int(text_progress), f"Added text overlay: '{caption}'")
                    else:
                        if progress_callback:
                            progress_callback(int(text_progress), f"Warning: Text overlay creation failed")
                except Exception as e:
                    if progress_callback:
                        progress_callback(int(text_progress), f"Error adding text: {e}")
                    else:
                        print(f"Error adding text overlay: {e}")
            
            # -------------------------------------------------------------
            # Transparent overlay video (e.g., animated lyrics)
            # -------------------------------------------------------------
            if overlay_video_path:
                overlay_progress = base_progress + (68 / num_videos)
                if progress_callback:
                    progress_callback(int(overlay_progress), f"Adding overlay video to video {i+1}/{num_videos}")

                try:
                    overlay_clip = VideoFileClip(overlay_video_path, has_mask=True)

                    # Scale overlay to fit within the final clip while PRESERVING aspect ratio.
                    # Never stretch – only scale up/down uniformly so that it fully fits inside.
                    if overlay_clip.w != final_clip.w or overlay_clip.h != final_clip.h:
                        scale_factor = min(final_clip.w / overlay_clip.w, final_clip.h / overlay_clip.h)
                        # Only resize if scale factor meaningfully differs from 1.0 (avoid tiny math jitter)
                        if abs(scale_factor - 1.0) > 0.01:
                            overlay_clip = overlay_clip.resize(scale_factor)

                    # Center the overlay if it does not cover the entire canvas
                    if overlay_clip.w < final_clip.w or overlay_clip.h < final_clip.h:
                        overlay_clip = overlay_clip.set_position("center")

                    # Match overlay duration to final clip
                    if overlay_clip.duration < final_clip.duration - 0.05:
                        overlay_clip = loop(overlay_clip, duration=final_clip.duration)
                    elif overlay_clip.duration > final_clip.duration + 0.05:
                        overlay_clip = overlay_clip.subclip(0, final_clip.duration)

                    overlay_clip = overlay_clip.set_duration(final_clip.duration)

                    # Composite overlay on top of final clip
                    final_clip = CompositeVideoClip([final_clip, overlay_clip])

                    if progress_callback:
                        progress_callback(int(overlay_progress), f"Overlay added to video {i+1}/{num_videos}")
                except Exception as e:
                    # If anything fails, continue without overlay
                    if progress_callback:
                        progress_callback(int(overlay_progress), f"Warning: Failed to apply overlay: {e}")
                    else:
                        print(f"Warning: Failed to apply overlay video: {e}")
            
            # Progress update for audio stage
            audio_progress = base_progress + (70 / num_videos)
            if progress_callback:
                progress_callback(int(audio_progress), f"Adding audio to video {i+1}/{num_videos}")
                
            # Select or generate audio
            if audio_files and len(audio_files) > 0:
                audio_path = random.choice(audio_files)
                try:
                    audio = AudioFileClip(audio_path)
                    
                    # Ensure audio is exactly as long as the video
                    target_duration = final_clip.duration
                    if audio.duration < target_duration:
                        # Loop the audio to match video duration exactly
                        audio = loop(audio, duration=target_duration)
                    else:
                        # Trim audio to match video duration exactly
                        audio = audio.subclip(0, target_duration)
                        
                    final_clip = final_clip.set_audio(audio)
                    if progress_callback:
                        progress_callback(int(audio_progress), f"Added audio to video {i+1}/{num_videos}")
                    else:
                        print(f"Added audio from {audio_path}")
                except Exception as e:
                    if progress_callback:
                        progress_callback(int(audio_progress), f"Error adding audio: {e}")
                    else:
                        print(f"Error adding audio from {audio_path}: {e}")
            
            # Progress update for rendering stage
            render_progress = base_progress + (75 / num_videos)
            if progress_callback:
                progress_callback(int(render_progress), f"Rendering video {i+1}/{num_videos}...")
            else:
                print(f"Writing audio for {output_path}...")
            
            # Ensure final clip has exact 9:16 dimensions before writing
            if final_clip.w != TARGET_WIDTH or final_clip.h != TARGET_HEIGHT:
                final_clip = final_clip.resize(width=TARGET_WIDTH, height=TARGET_HEIGHT)
            
            # Write the final video to temp file first (no heavy effects yet)
            try:
                tmp_no_fx = tempfile.mktemp(suffix="_nofx.mp4")
                final_clip.write_videofile(
                    tmp_no_fx,
                    codec="libx264",
                    audio_codec="aac",
                    preset="fast",
                    threads=4,
                    logger=None
                )

                # Apply FFmpeg effects if requested
                if use_effects and intensity_norm > 0:
                    if progress_callback:
                        progress_callback(int(base_progress + (92 / num_videos)), "Applying FFmpeg effects...")

                    def build_filter(style, t):
                        """Return FFmpeg filter string based on style and normalized intensity t (0-1)."""
                        t = max(0.0, min(t, 1.0))
                        if t < 0.05:  # practically no effect
                            return None

                        if style == "classic":
                            brightness = round(0.0 + 0.10 * t, 3)  # up to +0.10
                            saturation = round(1.0 + 1.5 * t, 2)   # up to 2.5x
                            return f"eq=brightness={brightness}:saturation={saturation}"

                        if style == "graincore":
                            contrast = round(1.0 + 4.0 * t, 2)      # 1-5
                            brightness = round(-0.2 * t, 2)         # 0 to -0.2
                            noise = int(20 + 180 * t)               # 20-200
                            opacity = round(0.1 + 0.8 * t, 2)       # 0.1-0.9
                            return (
                                f"format=gray,eq=contrast={contrast}:brightness={brightness},"
                                f"noise=alls={noise}:allf=u+random,"  # static flicker
                                f"tblend=all_mode=difference:opacity={opacity},format=yuv420p"
                            )

                        # Fallback minimal adjustment
                        return "eq=brightness=0:saturation=1"

                    filter_str = build_filter(effects_style, intensity_norm)

                    if filter_str is None:
                        # No effect needed, simply move original file
                        shutil.move(tmp_no_fx, output_path)
                        if progress_callback:
                            progress_callback(int(base_progress + (98 / num_videos)), f"Video {i+1}/{num_videos} complete!")
                        output_paths.append(output_path)
                        continue

                    tmp_with_fx = tempfile.mktemp(suffix="_fx.mp4")
                    ffmpeg_cmd = [
                        "ffmpeg",
                        "-y",
                        "-i", tmp_no_fx,
                        "-vf", filter_str,
                        "-c:v", "libx264",
                        "-preset", "fast",
                        "-crf", "18",
                        "-c:a", "copy",
                        tmp_with_fx
                    ]
                    subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                    shutil.move(tmp_with_fx, output_path)
                    os.remove(tmp_no_fx)
                else:
                    shutil.move(tmp_no_fx, output_path)

                if progress_callback:
                    progress_callback(int(base_progress + (98 / num_videos)), f"Video {i+1}/{num_videos} complete!")
                output_paths.append(output_path)
            except Exception as e:
                if progress_callback:
                    progress_callback(int(render_progress), f"Error writing video file: {e}. Trying simplifier method...")
                else:
                    print(f"Error writing video file {output_path}: {e}")
                try:
                    # Try a simpler approach if the first attempt fails
                    if progress_callback:
                        progress_callback(int(render_progress), f"Using simplified render settings...")
                    else:
                        print("Trying with simpler options...")
                    final_clip.write_videofile(output_path)
                    output_paths.append(output_path)
                except Exception as e2:
                    if progress_callback:
                        progress_callback(int(render_progress), f"Failed again: {e2}")
                    else:
                        print(f"Failed again: {e2}")
                    
        except Exception as e:
            if progress_callback:
                progress_callback(int(base_progress), f"Error creating final clip: {e}")
            else:
                print(f"Error creating final clip: {e}")
                import traceback
                traceback.print_exc()
        
        # Clean up memory
        if final_clip:
            final_clip.close()
        
        for clip in selected_clips:
            clip.close()
    
    # Clean up
    for clip in input_clips:
        clip.close()
    
    # Final progress update
    if progress_callback:
        progress_callback(100, f"All {len(output_paths)} videos complete!")
    
    return output_paths

def apply_smart_effects(clip, intensity=0.3):
    """
    Apply minimal effects to avoid freezing issues.
    """
    # Only attempt one simple effect
    effect_choice = random.random()
    
    try:
        if effect_choice < 0.4:  # 40% chance of slight color boost
            return colorx(clip, 1.0 + (intensity * 0.2))
        elif effect_choice < 0.6:  # 20% chance of slight fade
            return clip.crossfadein(0.3)
        else:  # 40% chance of no effect
            return clip
    except Exception as e:
        print(f"Effect failed, returning original clip: {e}")
        return clip

def create_text_overlay(text, clip_size, position="top", *,
                        font_name="Arial", bold=False, italic=False, underline=False,
                        fontsize=70, color="white", bg_color=None, stroke_color="black", stroke_width=2):
    """
    Create a text overlay for a video clip in a style common for short-form content.
    
    Args:
        text: Text to display
        clip_size: (width, height) of the video clip
        position: Where to position the text ("bottom", "center", "top")
        font_name: Font name to use
        bold: Whether to use bold font
        italic: Whether to use italic font
        underline: Whether to use underline font
        fontsize: Font size
        color: Font color
        bg_color: Background color (None for transparent)
        stroke_color: Outline color
        stroke_width: Outline width
        
    Returns:
        TextClip object ready to be composited
    """
    try:
        # Build candidate fonts list based on style flags
        candidates = []
        base = font_name
        if bold and italic:
            candidates += [f"{base}-BoldItalic", f"{base} Bold Italic", f"{base}-BoldOblique"]
        if bold and not italic:
            candidates += [f"{base}-Bold", f"{base} Bold"]
        if italic and not bold:
            candidates += [f"{base}-Italic", f"{base} Italic", f"{base}-Oblique"]
        # Always add base font last as fallback
        candidates.append(base)

        txt = None
        last_exc = None
        for cand_font in candidates:
            try:
                txt = TextClip(
                    text,
                    font=cand_font,
                    fontsize=fontsize,
                    color=color,
                    stroke_color=stroke_color,
                    stroke_width=stroke_width,
                    method='caption',
                    align='center',
                    size=(clip_size[0] - 40, None)
                )
                break  # Success
            except Exception as e:
                last_exc = e
                continue
        if txt is None:
            raise last_exc if last_exc else Exception("Unable to create TextClip with provided font")

        # Add underline if requested
        if underline:
            try:
                line_height = max(4, int(fontsize * 0.08))
                underline_clip = ColorClip(size=(txt.w, line_height), color=color)
                underline_clip = underline_clip.set_position(("center", txt.h - int(line_height/2)))
                txt = CompositeVideoClip([txt, underline_clip], size=(txt.w, txt.h + line_height))
            except Exception as ue:
                print(f"Warning: underline failed: {ue}")

        # Positioning within thirds
        try:
            if position in ("bottom", "lower"):
                y_pos = clip_size[1] * 5 / 6 - txt.h / 2  # center of bottom third
                txt = txt.set_position(("center", y_pos))
            elif position in ("top", "upper"):
                y_pos = clip_size[1] / 6 - txt.h / 2  # center of top third
                txt = txt.set_position(("center", y_pos))
            else:  # center
                txt = txt.set_position("center")
        except Exception as pe:
            print(f"Warning positioning text: {pe}")

        return txt
    except Exception as e:
        print(f"Error positioning text: {str(e)}")
        return None

# Add a function to preserve original dimensions 
def preserve_original_dimensions(original_clip, processed_clip):
    """
    Ensure a processed clip maintains the same dimensions and aspect ratio
    as the original clip. This prevents unwanted padding from being added.
    
    Args:
        original_clip: The original video clip with correct dimensions
        processed_clip: The processed clip that might have different dimensions
        
    Returns:
        A clip with the same content as processed_clip but dimensions of original_clip
    """
    # Get original dimensions
    orig_w, orig_h = original_clip.size
    
    # If dimensions already match, return the processed clip
    if processed_clip.w == orig_w and processed_clip.h == orig_h:
        return processed_clip
    
    # Resize the processed clip to match original dimensions exactly
    # without allowing any automatic padding
    return processed_clip.resize(width=orig_w, height=orig_h)

# Update ensure_consistent_dimensions to properly handle 9:16 videos
def ensure_consistent_dimensions(clip, target_ratio=(9, 16)):
    """
    Ensure consistent dimensions for all clips, properly handling vertical videos.
    For 9:16 videos, ensure they fill the screen with no black bars.
    For other ratios, add minimal black bars as needed.
    """
    if clip is None:
        raise ValueError("Clip cannot be None")
        
    # Set fixed target dimensions for 9:16 videos (e.g., 1080x1920)
    TARGET_WIDTH = 1080
    TARGET_HEIGHT = 1920
    
    # Get current dimensions
    w, h = clip.size
    
    # For vertical videos (taller than wide)
    if h > w:  # This is a vertical video
        # Resize to fixed 9:16 dimensions (1080x1920)
        # First scale by height to ensure we fill vertically
        scale_factor = TARGET_HEIGHT / h
        new_width = int(w * scale_factor)
        
        if new_width < TARGET_WIDTH:
            # If scaled width is less than target width, scale by width instead
            # This ensures we fill the full width with no black bars on sides
            return clip.resize(width=TARGET_WIDTH)
        else:
            # If wider than target, crop the sides to fit exactly 9:16
            resized = clip.resize(height=TARGET_HEIGHT)
            # Center crop to target width
            x_center = resized.w // 2
            x1 = max(0, x_center - TARGET_WIDTH // 2)
            x2 = min(resized.w, x_center + TARGET_WIDTH // 2)
            return crop(resized, x1=x1, y1=0, x2=x2, y2=TARGET_HEIGHT)
    
    # For horizontal videos (wider than tall)
    else:
        # Scale by width to ensure we fill horizontally
        scale_factor = TARGET_WIDTH / w
        new_height = int(h * scale_factor)
        
        # Resize first
        resized = clip.resize(width=TARGET_WIDTH)
        
        # Add black bars to top and bottom to make it exactly 9:16
        padding_y = (TARGET_HEIGHT - new_height) // 2
        return resized.margin(top=padding_y, bottom=padding_y, color=(0, 0, 0))

# Helper function to select a clip that is visually dissimilar to recently used clips
def select_dissimilar_clip(available_indices, recently_used, visual_signatures, top_n=3):
    """
    Select a clip that is visually dissimilar to recently used clips.
    
    Args:
        available_indices: List of available clip indices to choose from
        recently_used: List of recently used clip indices
        visual_signatures: Dictionary of clip signatures for comparison
        top_n: Number of candidates to consider
        
    Returns:
        Index of selected clip
    """
    # If no recently used clips or no signatures, choose randomly
    if not recently_used or not visual_signatures:
        return random.choice(available_indices)
    
    # Select a few random candidates
    candidates = random.sample(
        available_indices, 
        min(top_n, len(available_indices))
    )
    
    # Calculate average dissimilarity score for each candidate
    scores = []
    for candidate in candidates:
        # Skip if candidate doesn't have a signature
        if candidate not in visual_signatures:
            scores.append(0)
            continue
            
        # Calculate average dissimilarity to recently used clips
        dissimilarity = 0
        count = 0
        for used in recently_used:
            if used in visual_signatures:
                # Higher score means more dissimilar
                dissimilarity += 1.0 - calculate_similarity(
                    visual_signatures[candidate],
                    visual_signatures[used]
                )
                count += 1
        
        # Average dissimilarity (higher is better)
        avg_dissimilarity = dissimilarity / count if count > 0 else 0
        scores.append(avg_dissimilarity)
    
    # Select the most dissimilar candidate
    if scores:
        # Return the candidate with highest dissimilarity score
        return candidates[scores.index(max(scores))]
    
    # Fallback to random selection
    return random.choice(available_indices)

# Calculate similarity between two visual signatures
def calculate_similarity(sig1, sig2):
    """
    Calculate similarity between two visual signatures.
    Returns a value between 0 and 1, where 1 is identical.
    """
    # Simple implementation: use cosine similarity
    # Convert to numpy arrays if they aren't already
    sig1 = np.array(sig1)
    sig2 = np.array(sig2)
    
    # Calculate cosine similarity
    dot_product = np.dot(sig1, sig2)
    norm1 = np.linalg.norm(sig1)
    norm2 = np.linalg.norm(sig2)
    
    # Avoid division by zero
    if norm1 == 0 or norm2 == 0:
        return 0
        
    return dot_product / (norm1 * norm2)

# Create simple visual signatures for videos
def create_video_signatures(clips, samples=5):
    """
    Create simple visual signatures for a list of video clips.
    This is a simplified approach - in production, you'd use more sophisticated
    visual feature extraction.
    
    Args:
        clips: List of MoviePy VideoFileClip objects
        samples: Number of frames to sample from each clip
        
    Returns:
        Dictionary mapping clip index to signature
    """
    signatures = {}
    
    for i, clip in enumerate(clips):
        try:
            # Sample frames evenly throughout the clip
            duration = clip.duration
            if duration <= 0:
                continue
                
            frame_times = np.linspace(0, duration * 0.9, samples)
            
            # Extract color features from each frame
            signature = []
            for t in frame_times:
                try:
                    # Get frame at this time
                    frame = clip.get_frame(t)
                    
                    # Simple color histogram as signature
                    # Average color values in each channel
                    r_avg = np.mean(frame[:, :, 0])
                    g_avg = np.mean(frame[:, :, 1])
                    b_avg = np.mean(frame[:, :, 2])
                    
                    # Calculate dominant brightness
                    brightness = (r_avg + g_avg + b_avg) / 3
                    
                    # Add to signature
                    signature.extend([r_avg, g_avg, b_avg, brightness])
                    
                except Exception:
                    # If we can't get a frame, add zeros
                    signature.extend([0, 0, 0, 0])
            
            # Store normalized signature
            signatures[i] = signature
            
        except Exception:
            # If we can't process a clip, skip it
            continue
    
    return signatures

# Find available segments in a clip that haven't been used yet
def find_available_segments(clip_index, desired_duration, clip_duration, 
                           global_history=None, local_history=None, 
                           min_segment_size=0.5, buffer=0.1):
    """
    Find available segments in a clip that haven't been used yet.
    
    Args:
        clip_index: Index of the clip
        desired_duration: Desired duration of the segment
        clip_duration: Total duration of the clip
        global_history: List of (start, end) tuples of globally used segments
        local_history: List of (start, end) tuples of locally used segments
        min_segment_size: Minimum size of an available segment to consider
        buffer: Buffer around used segments to avoid too-similar clips
        
    Returns:
        List of (start, end) tuples representing available segments
    """
    if global_history is None:
        global_history = []
    if local_history is None:
        local_history = []
    
    # Combine global and local history
    all_used = global_history + local_history
    
    # If no used segments, the entire clip is available
    if not all_used:
        return [(0, clip_duration - desired_duration)]
    
    # Sort used segments by start time
    used_segments = sorted(all_used, key=lambda x: x[0])
    
    # Add buffer around used segments
    buffered_segments = []
    for start, end in used_segments:
        buffered_start = max(0, start - buffer)
        buffered_end = min(clip_duration, end + buffer)
        buffered_segments.append((buffered_start, buffered_end))
    
    # Merge overlapping segments
    merged = []
    for segment in buffered_segments:
        if not merged or segment[0] > merged[-1][1]:
            merged.append(segment)
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], segment[1]))
    
    # Find available segments
    available = []
    
    # Check if there's space before the first used segment
    if merged[0][0] > desired_duration:
        available.append((0, merged[0][0]))
    
    # Check spaces between used segments
    for i in range(len(merged) - 1):
        gap_start = merged[i][1]
        gap_end = merged[i+1][0]
        
        if gap_end - gap_start >= desired_duration + min_segment_size:
            available.append((gap_start, gap_end - desired_duration))
    
    # Check if there's space after the last used segment
    if clip_duration - merged[-1][1] >= desired_duration + min_segment_size:
        available.append((merged[-1][1], clip_duration - desired_duration))
    
    return available

def apply_graincore_effect(clip):
    """Placeholder graincore effect: add slight noise / BW flicker."""
    try:
        noisy = clip.fx(colorx, 0.9).fx(blackwhite)
        return noisy
    except Exception:
        return clip

if __name__ == "__main__":
    generate_batch()
