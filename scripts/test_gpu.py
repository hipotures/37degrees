from moviepy import VideoClip, ImageClip
import numpy as np
import moviepy.config as moviepy_config
import os

# Enable MoviePy verbose mode
os.environ['MOVIEPY_DEBUG'] = '1'
moviepy_config.FFMPEG_BINARY = "/usr/bin/ffmpeg"

# Create simple test clip
img = np.zeros((480, 640, 3), dtype=np.uint8)
img[:, :] = [255, 0, 0]  # Red background

clip = ImageClip(img).with_duration(2)

# Test GPU encoding
try:
    print("Testing h264_nvenc...")
    print(f"Using ffmpeg: {moviepy_config.FFMPEG_BINARY}")
    clip.write_videofile("test_nvenc.mp4", codec="h264_nvenc", fps=30)
    print("Success!")
except Exception as e:
    print(f"Failed: {e}")

# Test CPU encoding 
try:
    print("\nTesting libx264...")
    clip.write_videofile("test_x264.mp4", codec="libx264", fps=30)
    print("Success!")
except Exception as e:
    print(f"Failed: {e}")