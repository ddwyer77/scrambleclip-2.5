#!/usr/bin/env python3
"""
This script updates the pad_clip_to_ratio function in src/utils.py
to ensure videos are fit to full width with padding only on top and bottom.
"""

import os

# The new implementation of the pad_clip_to_ratio function
NEW_FUNCTION = '''
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
'''

# Read the current utils.py file
with open('src/utils.py', 'r') as f:
    content = f.read()

# Find the start and end of the current pad_clip_to_ratio function
start_marker = 'def pad_clip_to_ratio'
start_idx = content.find(start_marker)

if start_idx == -1:
    print("Error: Could not find the pad_clip_to_ratio function in src/utils.py")
    exit(1)

# Find the next function definition or the end of the file
next_def_idx = content.find('def ', start_idx + len(start_marker))
if next_def_idx == -1:
    # No more functions, use the end of the file
    end_idx = len(content)
else:
    # Find the start of the line with the next function
    end_idx = content.rfind('\n', 0, next_def_idx) + 1

# Replace the function
new_content = content[:start_idx] + NEW_FUNCTION.strip() + content[end_idx:]

# Write the updated content back to the file
with open('src/utils.py', 'w') as f:
    f.write(new_content)

print("Successfully updated the pad_clip_to_ratio function in src/utils.py") 