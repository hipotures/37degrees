#!/usr/bin/env python3
"""Create video from scenes with text overlays"""

import os
import sys
import yaml
from pathlib import Path

def create_video_ffmpeg(book_path: str):
    """Create video using ffmpeg directly"""
    book_dir = Path(book_path)
    config_file = book_dir / "book.yaml"
    
    if not config_file.exists():
        print(f"Error: {config_file} not found")
        return
    
    # Load book configuration
    with open(config_file, 'r', encoding='utf-8') as f:
        book_config = yaml.safe_load(f)
    
    # Get technical specs
    tech_specs = book_config.get('technical_specs', {})
    fps = tech_specs.get('fps', 30)
    duration_per_slide = tech_specs.get('duration_per_slide', 3.5)
    
    # Input and output directories
    input_dir = book_dir / "with_text"
    output_dir = book_dir
    frames_dir = book_dir / "frames"
    frames_dir.mkdir(exist_ok=True)
    
    # Get slides configuration
    slides = book_config.get('slides', [])
    
    # Create frame sequence
    frame_number = 0
    for i, slide in enumerate(slides):
        slide_type = slide.get('type', f'slide_{i}')
        slide_duration = slide.get('duration', duration_per_slide)
        
        # Input image path
        input_path = input_dir / f"scene_{i:02d}_{slide_type}_text.png"
        
        if not input_path.exists():
            print(f"Warning: {input_path} not found, skipping...")
            continue
        
        # Calculate number of frames for this slide
        num_frames = int(slide_duration * fps)
        
        # Create symlinks for each frame
        for j in range(num_frames):
            frame_path = frames_dir / f"frame_{frame_number:06d}.png"
            if frame_path.exists():
                frame_path.unlink()
            frame_path.symlink_to(input_path.absolute())
            frame_number += 1
        
        print(f"Slide {i}: {slide_type} - {num_frames} frames ({slide_duration}s)")
    
    # Create video with ffmpeg
    output_path = output_dir / f"{book_dir.name}_video.mp4"
    
    # Build ffmpeg command
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",  # Overwrite output
        "-framerate", str(fps),
        "-i", str(frames_dir / "frame_%06d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "23",
        "-movflags", "+faststart",
        str(output_path)
    ]
    
    print(f"\nCreating video: {output_path}")
    print(f"Total frames: {frame_number}")
    print(f"Duration: {frame_number / fps:.1f} seconds")
    
    # Run ffmpeg
    import subprocess
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"\nVideo created successfully: {output_path}")
        # Clean up frames directory
        for frame in frames_dir.glob("frame_*.png"):
            frame.unlink()
    else:
        print(f"\nError creating video:")
        print(result.stderr)
        return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_video.py <book_path>")
        sys.exit(1)
    
    book_path = sys.argv[1]
    create_video_ffmpeg(book_path)