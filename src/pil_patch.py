"""
This module provides a patch for Pillow's removal of the ANTIALIAS constant.
It ensures backward compatibility with libraries that still use the old constant.
"""

from PIL import Image

# Add ANTIALIAS constant if it doesn't exist (for Pillow >= 9.1.0)
if not hasattr(Image, 'ANTIALIAS'):
    # LANCZOS is the new name for ANTIALIAS
    if hasattr(Image, 'LANCZOS'):
        # Provide backward compatibility
        Image.ANTIALIAS = Image.LANCZOS
    # If using Pillow with Resampling enum
    elif hasattr(Image, 'Resampling') and hasattr(Image.Resampling, 'LANCZOS'):
        Image.ANTIALIAS = Image.Resampling.LANCZOS 