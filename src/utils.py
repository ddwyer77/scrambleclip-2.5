import glob
import random
from moviepy.editor import VideoFileClip

def get_video_files(input_folder):
    return glob.glob(f"{input_folder}/*.mp4") + glob.glob(f"{input_folder}/*.mov")

def get_random_clip(video_path, duration=4):
    clip = VideoFileClip(video_path)
    if clip.duration <= duration:
        return clip.subclip(0, clip.duration)
    start = random.uniform(0, clip.duration - duration)
    return clip.subclip(start, start + duration)

def pad_clip_to_ratio(clip, target_ratio=(9,16)):
    clip_ratio = clip.w / clip.h
    target_aspect = target_ratio[0] / target_ratio[1]

    if clip_ratio > target_aspect:
        new_height = clip.w / target_aspect
        padding = (new_height - clip.h) / 2
        return clip.margin(top=int(padding), bottom=int(padding), color=(0,0,0))
    elif clip_ratio < target_aspect:
        new_width = clip.h * target_aspect
        padding = int((new_width - clip.w) // 2)
        return clip.margin(left=padding, right=padding, color=(0,0,0))
    else:
        return clip
