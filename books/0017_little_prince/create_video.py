#!/usr/bin/env python3
"""
Create TikTok video for Little Prince using generated scenes
"""

import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Simple video generation without moviepy
def create_video_frames():
    """Create video frames from scenes and book content"""
    
    # Load book configuration
    import yaml
    with open('book.yaml', 'r', encoding='utf-8') as f:
        book_config = yaml.safe_load(f)
    
    slides = book_config['slides']
    scenes_dir = Path('scenes_v2')  # Use improved scenes
    frames_dir = Path('frames')
    frames_dir.mkdir(exist_ok=True)
    
    # Process each slide
    frame_number = 0
    for i, slide in enumerate(slides):
        scene_file = list(scenes_dir.glob(f"{i+1:02d}_*.png"))[0]
        scene_img = Image.open(scene_file)
        
        # Add text overlay
        draw = ImageDraw.Draw(scene_img)
        
        # Text settings
        text = slide['text']
        text_color = "white"
        shadow_color = "black"
        
        # Try to use a better font, fallback to default
        try:
            font_size = 48  # Smaller font to fit better
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position (centered)
        img_width, img_height = scene_img.size
        
        # Define the overlay box boundaries
        margin = 100
        box_top = img_height // 3
        box_bottom = 2 * img_height // 3
        box_padding = 40  # Inner padding
        
        # Wrap text to fit within the box
        words = text.split()
        lines = []
        current_line = []
        max_width = img_width - (2 * margin) - (2 * box_padding)  # Account for margins and padding
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            try:
                bbox = draw.textbbox((0, 0), test_line, font=font)
                line_width = bbox[2] - bbox[0]
            except:
                # Fallback for older PIL versions
                line_width = len(test_line) * 30  # rough estimate
            
            if line_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw text with shadow - ensure it fits within the box
        line_height = 60  # Adjusted for smaller font
        total_text_height = len(lines) * line_height
        
        # Center text vertically within the box
        box_height = box_bottom - box_top - (2 * box_padding)
        y_start = box_top + box_padding + (box_height - total_text_height) // 2
        
        # Ensure text doesn't go outside the box
        if y_start < box_top + box_padding:
            y_start = box_top + box_padding
        
        y_offset = y_start
        
        for line in lines:
            # Don't draw if we're outside the box
            if y_offset + line_height > box_bottom - box_padding:
                break
                
            try:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
            except:
                line_width = len(line) * 25  # Adjusted for smaller font
            
            x = (img_width - line_width) // 2
            
            # Shadow
            draw.text((x+2, y_offset+2), line, fill=shadow_color, font=font)
            # Main text
            draw.text((x, y_offset), line, fill=text_color, font=font)
            
            y_offset += line_height
        
        # Save frame multiple times for duration
        duration = slide.get('duration', 3.0)
        fps = 30
        num_frames = int(duration * fps)
        
        for j in range(num_frames):
            frame_path = frames_dir / f"frame_{frame_number:06d}.png"
            scene_img.save(frame_path)
            frame_number += 1
        
        print(f"Created {num_frames} frames for slide {i+1}")
    
    print(f"\nTotal frames created: {frame_number}")
    return frames_dir, frame_number

def create_ffmpeg_video(frames_dir, total_frames):
    """Use ffmpeg to create video from frames"""
    output_path = "little_prince_tiktok.mp4"
    
    # FFmpeg command to create video
    # -r 30: 30 fps
    # -i: input pattern
    # -c:v libx264: H.264 codec
    # -pix_fmt yuv420p: pixel format for compatibility
    # -s 1080x1920: TikTok vertical format
    
    cmd = f"ffmpeg -r 30 -i {frames_dir}/frame_%06d.png -c:v libx264 -pix_fmt yuv420p -s 1080x1920 -y {output_path}"
    
    print(f"\nCreating video with command:")
    print(cmd)
    
    os.system(cmd)
    
    if os.path.exists(output_path):
        print(f"\n✅ Video created successfully: {output_path}")
        print(f"Duration: {total_frames/30:.1f} seconds")
    else:
        print("\n❌ Failed to create video")

def main():
    """Main function"""
    print("Creating TikTok video for Little Prince...")
    
    # Create frames
    frames_dir, total_frames = create_video_frames()
    
    # Create video with ffmpeg
    create_ffmpeg_video(frames_dir, total_frames)
    
    # Cleanup frames (optional)
    cleanup = input("\nDelete temporary frames? (y/n): ")
    if cleanup.lower() == 'y':
        import shutil
        shutil.rmtree(frames_dir)
        print("Frames deleted.")

if __name__ == "__main__":
    main()