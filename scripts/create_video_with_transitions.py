#!/usr/bin/env python3
from moviepy import *
from moviepy.video.fx import FadeIn, FadeOut
import os
import glob

# Find project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_dir = os.path.join(project_root, "output")
os.makedirs(output_dir, exist_ok=True)

audio_path = "audio/0036_podcast_01.wav"
images_dir = "generated"
output_path = os.path.join(output_dir, "0036_treasure_island_smooth.mp4")

audio = AudioFileClip(audio_path)
audio_duration = audio.duration

image_files = sorted(glob.glob(f"{images_dir}/0036_scene_*.png"))
num_images = len(image_files)

print(f"Audio duration: {audio_duration:.2f}s")
print(f"Number of images: {num_images}")

fade_duration = 2.5
overlap_duration = 5.0

base_duration = audio_duration / num_images
total_clip_duration = base_duration
start_interval = base_duration - overlap_duration

print(f"Scene duration: {base_duration:.2f}s")
print(f"Start interval: {start_interval:.2f}s")
print(f"Overlap duration: {overlap_duration:.2f}s")

clips = []
for i, img_path in enumerate(image_files):
    img_clip = ImageClip(img_path, duration=total_clip_duration)
    
    if i > 0:
        img_clip = img_clip.with_effects([FadeIn(fade_duration)])
    if i < num_images - 1:
        img_clip = img_clip.with_effects([FadeOut(fade_duration)])
    
    start_time = i * start_interval
    img_clip = img_clip.with_start(start_time)
    
    clips.append(img_clip)
    print(f"Image {i+1}: starts at {start_time:.2f}s, duration {total_clip_duration:.2f}s")

video = CompositeVideoClip(clips)
video = video.with_audio(audio)

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