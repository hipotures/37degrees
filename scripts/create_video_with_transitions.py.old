#!/usr/bin/env python3
from moviepy import *
from moviepy.video.fx import FadeIn, FadeOut, CrossFadeIn, CrossFadeOut
import os
import glob
import sys

# Debug mode - use first N images only
DEBUG_MODE = False
DEBUG_IMAGES = 3  # Number of images to use in debug mode

if len(sys.argv) > 1:
    DEBUG_MODE = True
    DEBUG_IMAGES = int(sys.argv[1])
    print(f"DEBUG MODE: Using first {DEBUG_IMAGES} images")

# Find project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_dir = os.path.join(project_root, "output")
os.makedirs(output_dir, exist_ok=True)

audio_path = os.path.join(project_root, "books/0036_treasure_island/audio/0036_podcast_01.wav")
images_dir = os.path.join(project_root, "books/0036_treasure_island/generated")

# Change output filename for debug mode
if DEBUG_MODE:
    output_path = os.path.join(output_dir, f"0036_treasure_island_smooth_debug_{DEBUG_IMAGES}.mp4")
else:
    output_path = os.path.join(output_dir, "0036_treasure_island_smooth.mp4")

audio = AudioFileClip(audio_path)
audio_duration = audio.duration

image_files = sorted(glob.glob(f"{images_dir}/0036_scene_*.png"))

# Limit images in debug mode
if DEBUG_MODE:
    image_files = image_files[:DEBUG_IMAGES]
    # Adjust audio duration proportionally
    audio_duration = (audio_duration / 25) * DEBUG_IMAGES
    print(f"Debug mode: Adjusted audio duration to {audio_duration:.2f}s")

num_images = len(image_files)

print(f"Audio duration: {audio_duration:.2f}s")
print(f"Number of images: {num_images}")

fade_duration = 2.5

# Simple calculation: each scene starts when previous begins fade out
# This creates smooth crossfade transitions
if num_images > 1:
    clip_duration = (audio_duration + fade_duration * (num_images - 1)) / num_images
    start_interval = clip_duration - fade_duration
else:
    clip_duration = audio_duration
    start_interval = 0

print(f"Clip duration: {clip_duration:.2f}s")
print(f"Start interval: {start_interval:.2f}s") 
print(f"Fade duration: {fade_duration:.2f}s")

clips = []
for i, img_path in enumerate(image_files):
    # Create clip
    img_clip = ImageClip(img_path, duration=clip_duration)
    
    # Apply effects based on position
    if i == 0:
        # First clip: fade in from black, crossfade out to next
        img_clip = img_clip.with_effects([FadeIn(fade_duration)])
        if num_images > 1:
            img_clip = img_clip.with_effects([CrossFadeOut(fade_duration)])
    elif i == num_images - 1:
        # Last clip: crossfade in from previous, fade out to black
        img_clip = img_clip.with_effects([CrossFadeIn(fade_duration), FadeOut(fade_duration)])
    else:
        # Middle clips: crossfade in and out
        img_clip = img_clip.with_effects([CrossFadeIn(fade_duration), CrossFadeOut(fade_duration)])
    
    # Set start time
    start_time = i * start_interval
    img_clip = img_clip.with_start(start_time)
    
    clips.append(img_clip)
    print(f"Image {i+1}: {start_time:.2f}s - {start_time + clip_duration:.2f}s")

# Create composite - duration will match audio
video = CompositeVideoClip(clips, size=clips[0].size)

# In debug mode, trim audio to match video length
if DEBUG_MODE:
    audio = audio.subclipped(0, audio_duration)
    
video = video.with_audio(audio)
video = video.with_duration(audio_duration)

print(f"Final video duration: {video.duration:.2f}s")
print("Rendering video...")

video.write_videofile(
    output_path,
    fps=30,
    codec='libx264',
    audio_codec='aac',
    preset='medium'
)

print(f"Video saved as: {output_path}")