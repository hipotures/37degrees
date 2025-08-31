#!/usr/bin/env python3
"""
Quick test script for video generation with only 2-3 images.
Tests intro/outro rendering without processing all 25 images.

Usage: python scripts/test_video_quick.py 0024_pan_tadeusz [--force]
"""

import argparse
import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import tempfile


def create_test_images_dir(book_dir: str, num_images: int = 2):
    """Create a temporary directory with only first N images."""
    original_images_dir = Path(f"books/{book_dir}/images")
    if not original_images_dir.exists():
        print(f"❌ Images directory not found: {original_images_dir}")
        sys.exit(1)
    
    # Get all PNG files
    all_images = sorted(original_images_dir.glob("*.png"))
    if not all_images:
        print(f"❌ No PNG images found in {original_images_dir}")
        sys.exit(1)
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix=f"test_images_{book_dir}_"))
    
    # Copy only first N images
    for i, img in enumerate(all_images[:num_images]):
        shutil.copy2(img, temp_dir / img.name)
        print(f"  Copied: {img.name}")
    
    # Verify count
    copied_files = list(temp_dir.glob("*.png"))
    print(f"✓ Created test directory with {len(copied_files)} images: {temp_dir}")
    print(f"  Files: {[f.name for f in copied_files]}")
    return temp_dir


def find_audio_file(book_dir: str) -> Path:
    """Use existing 10-second test audio file."""
    test_audio = Path("test_audio_10s.m4a")
    if test_audio.exists():
        print(f"✓ Using existing 10-second test audio: {test_audio}")
        return test_audio
    
    # Fallback: create a short 10-second audio file
    temp_audio = Path(tempfile.mktemp(suffix=".mp3"))
    cmd = [
        "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-t", "10", "-acodec", "mp3", str(temp_audio)
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print(f"❌ Failed to create test audio: {result.stderr}")
        sys.exit(1)
    
    print(f"✓ Created 10-second test audio: {temp_audio}")
    return temp_audio


def main():
    parser = argparse.ArgumentParser(description="Quick test for video generation")
    parser.add_argument("book_dir", help="Book directory name (e.g., 0024_pan_tadeusz)")
    parser.add_argument("--force", action="store_true", help="Force regeneration of intro/outro")
    parser.add_argument("--num-images", type=int, default=2, help="Number of images to use (default: 2)")
    parser.add_argument("--method", choices=["improved", "original"], default="improved",
                        help="Method for intro/outro generation")
    args = parser.parse_args()
    
    book_dir = args.book_dir
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_output/test_{book_dir}_{timestamp}.mp4"
    
    print(f"🚀 Quick test for: {book_dir}")
    print(f"   Using {args.num_images} images only")
    
    # Ensure test output directory exists
    Path("test_output").mkdir(exist_ok=True)
    
    try:
        # 1. Prepare test images directory
        test_images_dir = create_test_images_dir(book_dir, args.num_images)
        
        # 2. Find or create audio
        audio_file = find_audio_file(book_dir)
        
        # 3. Generate intro frames if needed
        intro_frames_dir = Path(f"books/{book_dir}/intro_frames")
        if args.force or not intro_frames_dir.exists() or not list(intro_frames_dir.glob("*.png")):
            print("🎬 Generating intro frames...")
            intro_html = Path(f"books/{book_dir}/assets/podcast-intro-screen.html")
            
            if not intro_html.exists():
                # Create it from template
                print("  Creating personalized intro HTML...")
                subprocess.run([
                    "python", "scripts/generate_full_video.py",
                    book_dir, "--force"
                ], capture_output=True)
            
            # Generate frames using slowdown method for proper animation timing
            temp_video = f"temp_intro_test.mp4"
            cmd = [
                "python", "scripts/html_to_video_improved.py",
                str(intro_html),
                temp_video,
                "3", "30", "1080", "1920", "1",  # DPR=1 for correct size
                "--method=slowdown",  # Always use slowdown for proper animation capture
                "--frames-only",
                f"--frames-dir={intro_frames_dir}"
            ]
            
            result = subprocess.run(cmd)
            if result.returncode != 0:
                print("❌ Failed to generate intro frames")
                sys.exit(1)
        
        # 4. Generate outro frames if needed
        outro_frames_dir = Path("shared_assets/outro_frames")
        if args.force or not outro_frames_dir.exists() or not list(outro_frames_dir.glob("*.png")):
            print("🎬 Generating outro frames...")
            temp_video = f"temp_outro_test.mp4"
            cmd = [
                "python", "scripts/html_to_video_improved.py",
                "shared_assets/www/podcast-outro-screen.html",
                temp_video,
                "3", "30", "1080", "1920", "1",  # DPR=1 for correct size
                "--method=slowdown",  # Always use slowdown for proper animation capture
                "--frames-only",
                f"--frames-dir={outro_frames_dir}"
            ]
            
            result = subprocess.run(cmd)
            if result.returncode != 0:
                print("❌ Failed to generate outro frames")
                sys.exit(1)
        
        # 5. Compose final video with only test images
        test_images_count = len(list(test_images_dir.glob("*.png")))
        print(f"🎬 Composing test video with {test_images_count} images...")
        print(f"   Images directory: {test_images_dir}")
        print(f"   Audio file: {audio_file}")
        
        cmd = [
            "python", "scripts/compose_with_moviepy_transitions.py",
            "--images-dir", str(test_images_dir),
            "--audio", str(audio_file),
            "--intro-frames", str(intro_frames_dir),
            "--intro-fps", "30",
            "--outro-frames", str(outro_frames_dir),
            "--outro-fps", "30",
            "--fade", "2.5",
            "--fps", "30",
            "--output", output_file
        ]
        
        print(f"   Command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print("❌ Failed to compose video")
            sys.exit(1)
        
        # Cleanup
        shutil.rmtree(test_images_dir)
        if "temp_" in str(audio_file):
            audio_file.unlink()
        
        print(f"""
✅ SUCCESS! Test video generated:
   📂 Book: {book_dir}
   🎬 Output: {output_file}
   📏 Size: {Path(output_file).stat().st_size / (1024*1024):.1f}MB
   🖼️ Images used: {args.num_images}
        """)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()