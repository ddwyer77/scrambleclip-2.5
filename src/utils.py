import glob
import random
from moviepy.editor import VideoFileClip

def get_video_files(input_folder):
    return glob.glob(f"{input_folder}/*.mp4") + glob.glob(f"{input_folder}/*.mov")

def get_random_clip(video_path, duration=4, used_segments=None):
    """
    Get a random clip from a video file, avoiding previously used segments.
    
    Args:
        video_path: Path to the video file
        duration: Desired duration of the clip (in seconds)
        used_segments: List of (video_path, start_time, end_time) tuples of segments already used
    
    Returns:
        A VideoFileClip object with the random segment
    """
    clip = VideoFileClip(video_path)
    
    # If video is shorter than requested duration, return the whole clip
    if clip.duration <= duration:
        return clip.subclip(0, clip.duration)
    
    # If no used segments for this video, just pick a random start time
    if used_segments is None or not any(s[0] == video_path for s in used_segments):
        start = random.uniform(0, clip.duration - duration)
        return clip.subclip(start, start + duration)
    
    # Get all used segments for this specific video
    video_used_segments = [(s[1], s[2]) for s in used_segments if s[0] == video_path]
    
    # Try to find a non-overlapping segment (max 10 attempts)
    max_attempts = 10
    for _ in range(max_attempts):
        # Pick a random start time
        start = random.uniform(0, clip.duration - duration)
        end = start + duration
        
        # Check if this segment overlaps with any used segment
        overlap = False
        for used_start, used_end in video_used_segments:
            # Check for overlap: not (end <= used_start or start >= used_end)
            if not (end <= used_start or start >= used_end):
                overlap = True
                break
        
        # If no overlap, use this segment
        if not overlap:
            return clip.subclip(start, end)
    
    # If we couldn't find a non-overlapping segment after max attempts,
    # try to find the segment with the least overlap
    least_overlap = float('inf')
    best_start = None
    
    # Try several random positions
    for _ in range(20):
        start = random.uniform(0, clip.duration - duration)
        end = start + duration
        
        # Calculate total overlap with used segments
        total_overlap = 0
        for used_start, used_end in video_used_segments:
            # Calculate overlap duration
            overlap_start = max(start, used_start)
            overlap_end = min(end, used_end)
            if overlap_end > overlap_start:
                total_overlap += overlap_end - overlap_start
        
        # If this has less overlap than our current best, update
        if total_overlap < least_overlap:
            least_overlap = total_overlap
            best_start = start
    
    # Use the segment with the least overlap
    if best_start is not None:
        return clip.subclip(best_start, best_start + duration)
    
    # Fallback: just use a random segment
    start = random.uniform(0, clip.duration - duration)
    return clip.subclip(start, start + duration)

def pad_clip_to_ratio(clip, target_ratio=(9,16)):
    """
    Pad a clip to the target aspect ratio (default 9:16).
    
    For clips that are already 9:16, no padding is added.
    For all other aspect ratios:
    - Fit to full width (horizontal edges)
    - Add black padding only on top and bottom
    """
    clip_ratio = clip.w / clip.h
    target_aspect = target_ratio[0] / target_ratio[1]
    
    # If already 9:16 (or very close), return as is
    if abs(clip_ratio - target_aspect) < 0.01:
        return clip
    
    # For all other aspect ratios, we want to fit to width
    # Calculate the height needed for the target aspect ratio
    target_height = clip.w / target_aspect
    
    if target_height > clip.h:
        # The clip is wider than 9:16 (landscape or wide)
        # Add padding to top and bottom to reach target height
        padding = (target_height - clip.h) / 2
        return clip.margin(top=int(padding), bottom=int(padding), color=(0,0,0))
    else:
        # The clip is taller than 9:16 (narrow portrait)
        # Resize to fit width while maintaining aspect ratio
        resized_clip = clip.resize(width=clip.w)
        return resized_clip