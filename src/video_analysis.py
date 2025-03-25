import os
import numpy as np
import cv2
from moviepy.editor import VideoFileClip
import random
from collections import defaultdict

class VideoContentAnalyzer:
    """
    A class that provides AI-based video content analysis features:
    1. Analyzes video content for interesting segments
    2. Detects similarity between video clips
    3. Scores clip "interestingness" for better content selection
    """
    
    def __init__(self, cache_dir=".clip_cache"):
        """
        Initialize the video analyzer.
        
        Args:
            cache_dir: Directory to store processed frame features
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Frame features cache to avoid recomputing for the same clip
        self.frame_features_cache = {}
        
        # Track clip similarity scores between clips
        self.similarity_scores = defaultdict(dict)
        
        # Track clips used in each output video
        self.clips_used_in_videos = defaultdict(list)
    
    def extract_frame_features(self, video_path, num_frames=10):
        """
        Extract visual features from key frames of the video.
        
        Args:
            video_path: Path to the video file
            num_frames: Number of frames to sample from the video
            
        Returns:
            A list of feature vectors for sampled frames
        """
        # Check if we've already processed this video
        cache_key = f"{video_path}_{num_frames}"
        if cache_key in self.frame_features_cache:
            return self.frame_features_cache[cache_key]
        
        # Open video and get frame features
        video = VideoFileClip(video_path)
        
        # Sample frames evenly throughout the video
        frame_times = np.linspace(0, video.duration, num_frames)
        features = []
        
        for time in frame_times:
            # Get frame at specified time
            frame = video.get_frame(time)
            
            # Convert frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            
            # Resize to a standard size for comparison
            resized = cv2.resize(gray, (32, 32))
            
            # Flatten and normalize
            flat_features = resized.flatten() / 255.0
            features.append(flat_features)
        
        # Store in cache and return
        self.frame_features_cache[cache_key] = features
        return features
    
    def calculate_clip_similarity(self, clip1_path, clip1_start, clip1_end, 
                                 clip2_path, clip2_start, clip2_end):
        """
        Calculate the similarity between two clips.
        
        Args:
            clip1_path: Path to the first video
            clip1_start: Start time of first clip
            clip1_end: End time of first clip
            clip2_path: Path to the second video
            clip2_start: Start time of second clip
            clip2_end: End time of second clip
            
        Returns:
            A similarity score between 0 and 1, where 1 means identical
        """
        # If comparing the same clip in the same video, they're identical
        if (clip1_path == clip2_path and 
            abs(clip1_start - clip2_start) < 0.1 and 
            abs(clip1_end - clip2_end) < 0.1):
            return 1.0
            
        # If they're from the same video and overlap significantly, high similarity
        if clip1_path == clip2_path:
            # Calculate overlap
            overlap_start = max(clip1_start, clip2_start)
            overlap_end = min(clip1_end, clip2_end)
            
            if overlap_end > overlap_start:
                overlap_duration = overlap_end - overlap_start
                clip1_duration = clip1_end - clip1_start
                clip2_duration = clip2_end - clip2_start
                
                # Normalized overlap (0 to 1)
                overlap_ratio = overlap_duration / min(clip1_duration, clip2_duration)
                return overlap_ratio
        
        # For different videos or non-overlapping segments, compare frame features
        # (simplified - in a real implementation, we'd compute features for specific time ranges)
        clip1_features = self.extract_frame_features(clip1_path)
        clip2_features = self.extract_frame_features(clip2_path)
        
        # Compare feature sets (using a simple average for demonstration)
        # In a real implementation, we'd use more sophisticated comparison
        similarity_sum = 0
        comparisons = 0
        
        for f1 in clip1_features:
            for f2 in clip2_features:
                # Calculate cosine similarity
                dot_product = np.dot(f1, f2)
                norm_f1 = np.linalg.norm(f1)
                norm_f2 = np.linalg.norm(f2)
                
                if norm_f1 > 0 and norm_f2 > 0:
                    similarity = dot_product / (norm_f1 * norm_f2)
                    similarity_sum += similarity
                    comparisons += 1
        
        # Return average similarity
        if comparisons > 0:
            return similarity_sum / comparisons
        return 0.0
    
    def score_clip_interestingness(self, video_path, start_time, end_time):
        """
        Score how interesting a clip is based on visual content.
        
        Args:
            video_path: Path to the video file
            start_time: Start time of the clip
            end_time: End time of the clip
            
        Returns:
            An "interestingness" score from 0-10
        """
        # Extract features for the specific time range
        video = VideoFileClip(video_path).subclip(start_time, end_time)
        
        # Sample frames evenly throughout the clip
        num_frames = 5
        frame_times = np.linspace(0, video.duration, num_frames)
        
        # Metrics to evaluate interestingness
        visual_entropy = 0
        motion_score = 0
        brightness_score = 0
        
        prev_frame = None
        for i, time in enumerate(frame_times):
            # Get frame at specified time
            frame = video.get_frame(time)
            
            # Calculate brightness (simple average)
            brightness = np.mean(frame)
            brightness_score += brightness / 255.0
            
            # Convert to grayscale for further analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            
            # Calculate visual entropy (how much information/detail in the frame)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist = hist / hist.sum()  # Normalize
            non_zero_hist = hist[hist > 0]
            entropy = -np.sum(non_zero_hist * np.log2(non_zero_hist))
            visual_entropy += entropy
            
            # Calculate motion if not the first frame (simple difference)
            if prev_frame is not None:
                motion = np.mean(np.abs(gray.astype(float) - prev_frame.astype(float)))
                motion_score += motion / 255.0
            
            prev_frame = gray
        
        # Normalize scores
        visual_entropy = visual_entropy / num_frames / 8.0  # Max entropy is ~8 for 256 bins
        brightness_score = brightness_score / num_frames
        if num_frames > 1:
            motion_score = motion_score / (num_frames - 1)
        
        # Calculate combined score (0-10)
        # Weight the factors based on importance
        combined_score = (
            3.0 * visual_entropy +  # Detail/information
            5.0 * motion_score +    # Movement (most important)
            2.0 * brightness_score  # Brightness
        )
        
        # Scale to 0-10 range
        return min(10, max(0, combined_score * 10))
    
    def find_best_clips(self, video_files, num_clips=4, clip_duration=4.0, 
                        used_segments=None, batch_id=None):
        """
        Find the best clips for a video based on content analysis.
        
        Args:
            video_files: List of video file paths
            num_clips: Number of clips to select
            clip_duration: Duration of each clip
            used_segments: Previously used segments to avoid
            batch_id: ID for the current batch to track usage
            
        Returns:
            A list of (video_path, start_time, end_time, score) tuples
        """
        if used_segments is None:
            used_segments = []
        
        # Track all candidate clips and their scores
        candidate_clips = []
        
        # Analyze each video file
        for video_path in video_files:
            try:
                video = VideoFileClip(video_path)
                
                # Skip if video is too short
                if video.duration <= clip_duration:
                    continue
                
                # Try multiple positions in the video
                num_positions = min(20, int(video.duration / clip_duration))
                
                for _ in range(num_positions):
                    # Pick a random start time
                    start = random.uniform(0, video.duration - clip_duration)
                    end = start + clip_duration
                    
                    # Check if this segment overlaps with any used segment
                    overlap = False
                    for used_vid, used_start, used_end in used_segments:
                        if used_vid == video_path:
                            if not (end <= used_start or start >= used_end):
                                overlap = True
                                break
                    
                    if not overlap:
                        # Score the clip
                        score = self.score_clip_interestingness(video_path, start, end)
                        
                        # Adjust score based on similarity to clips used in this batch
                        if batch_id is not None:
                            for used_clip in self.clips_used_in_videos.get(batch_id, []):
                                used_vid, used_start, used_end = used_clip
                                similarity = self.calculate_clip_similarity(
                                    video_path, start, end, used_vid, used_start, used_end)
                                
                                # Penalize similar clips
                                penalty = similarity * 5.0  # Stronger penalty for similar clips
                                score = max(0, score - penalty)
                        
                        candidate_clips.append((video_path, start, end, score))
            
            except Exception as e:
                print(f"Error analyzing {video_path}: {str(e)}")
                continue
        
        # If we don't have enough candidates, try again with less strict criteria
        if len(candidate_clips) < num_clips:
            # Take any unused segments, even with low scores
            return [(vid, start, end, score) for vid, start, end, score 
                   in candidate_clips[:num_clips]]
        
        # Sort by score and return top clips
        best_clips = sorted(candidate_clips, key=lambda x: x[3], reverse=True)[:num_clips]
        
        # Record these clips as used in this batch
        if batch_id is not None:
            self.clips_used_in_videos[batch_id] = [
                (vid, start, end) for vid, start, end, _ in best_clips
            ]
        
        return best_clips 