#!/usr/bin/env python3
"""
Generate complete video for a book with intro, all scenes, and outro.

Usage: python generate_full_video.py 0024_pan_tadeusz
"""

import argparse
import os
import sys
import subprocess
import yaml
import uuid
from datetime import datetime
from pathlib import Path


def load_book_yaml(book_dir: str) -> dict:
    """Load book.yaml and extract title and author."""
    book_yaml_path = Path(f"books/{book_dir}/book.yaml")
    if not book_yaml_path.exists():
        raise FileNotFoundError(f"book.yaml not found in books/{book_dir}/")
    
    with open(book_yaml_path, 'r', encoding='utf-8') as f:
        book_data = yaml.safe_load(f)
    
    # Data is under 'book_info' section
    book_info = book_data.get('book_info', {})
    
    return {
        'title': book_info.get('title', 'Unknown Title'),
        'author': book_info.get('author', 'Unknown Author')
    }


def create_directories(book_dir: str):
    """Create necessary directories if they don't exist."""
    dirs_to_create = [
        f"books/{book_dir}/assets",
        f"books/{book_dir}/intro_frames",
        f"books/{book_dir}/images",
        f"books/{book_dir}/audio",
        "shared_assets/outro_frames",
        "output"
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Ensured directory exists: {dir_path}")


def create_personalized_intro_html(book_dir: str, book_data: dict):
    """Create personalized intro HTML from template."""
    template_path = Path("shared_assets/www/podcast-intro-screen.html")
    target_path = Path(f"books/{book_dir}/assets/podcast-intro-screen.html")
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    
    # Read template
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Replace placeholders
    html_content = html_content.replace('[BOOK-TITLE]', book_data['title'])
    html_content = html_content.replace('[BOOK-AUTHOR]', book_data['author'])
    
    # Write personalized version
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Created personalized intro HTML: {target_path}")
    return target_path


def generate_intro_frames(book_dir: str, intro_html_path: Path, force: bool = False):
    """Generate intro frames for the specific book."""
    frames_dir = Path(f"books/{book_dir}/intro_frames")
    
    if not force and frames_dir.exists() and list(frames_dir.glob("*.png")):
        print(f"✓ Intro frames already exist: {frames_dir}")
        return frames_dir
    
    if force and frames_dir.exists():
        print(f"🔥 Force mode: removing existing intro frames: {frames_dir}")
        for png_file in frames_dir.glob("*.png"):
            png_file.unlink()
    
    print(f"🎬 Generating intro frames...")
    temp_video = f"temp_intro_{uuid.uuid4().hex[:8]}.mp4"
    cmd = [
        "python", "scripts/html_to_video_30fps.py",
        str(intro_html_path),
        temp_video,  # unique temp file
        "3",  # duration
        "30",  # fps
        "1080", "1920",  # resolution
        "1",  # DPR
        "--frames-only",
        f"--frames-dir={frames_dir}"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error generating intro frames: {result.stderr}")
        sys.exit(1)
    
    print(f"✓ Generated intro frames: {frames_dir}")
    return frames_dir


def generate_outro_frames(force: bool = False):
    """Generate shared outro frames (once for all books)."""
    frames_dir = Path("shared_assets/outro_frames")
    
    if not force and frames_dir.exists() and list(frames_dir.glob("*.png")):
        print(f"✓ Outro frames already exist: {frames_dir}")
        return frames_dir
    
    if force and frames_dir.exists():
        print(f"🔥 Force mode: removing existing outro frames: {frames_dir}")
        for png_file in frames_dir.glob("*.png"):
            png_file.unlink()
    
    print(f"🎬 Generating outro frames...")
    temp_video = f"temp_outro_{uuid.uuid4().hex[:8]}.mp4"
    cmd = [
        "python", "scripts/html_to_video_30fps.py",
        "shared_assets/www/podcast-outro-screen.html",
        temp_video,  # unique temp file
        "3",  # duration
        "30",  # fps
        "1080", "1920",  # resolution
        "1",  # DPR
        "--frames-only",
        f"--frames-dir={frames_dir}"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error generating outro frames: {result.stderr}")
        sys.exit(1)
    
    print(f"✓ Generated outro frames: {frames_dir}")
    return frames_dir


def find_audio_file(book_dir: str) -> Path:
    """Find audio file in book directory."""
    audio_dir = Path(f"books/{book_dir}/audio")
    audio_files = list(audio_dir.glob("*.m4a")) + list(audio_dir.glob("*.mp3")) + list(audio_dir.glob("*.wav"))
    
    if not audio_files:
        raise FileNotFoundError(f"No audio file found in {audio_dir}")
    
    # Use first audio file found
    audio_file = audio_files[0]
    print(f"✓ Found audio file: {audio_file}")
    return audio_file


def generate_final_video(book_dir: str, intro_frames_dir: Path, outro_frames_dir: Path, audio_file: Path):
    """Generate final video with all components."""
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(f"output/{book_dir}_{timestamp}.mp4")
    
    print(f"🎬 Generating final video: {output_file}")
    
    cmd = [
        "python", "scripts/compose_with_moviepy_transitions.py",
        "--images-dir", f"books/{book_dir}/images",
        "--audio", str(audio_file),
        "--intro-frames", str(intro_frames_dir),
        "--intro-fps", "30",
        "--outro-frames", str(outro_frames_dir),
        "--outro-fps", "30",
        "--fade", "2.5",
        "--fps", "30",
        "--output", str(output_file)
    ]
    
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"❌ Error generating final video")
        sys.exit(1)
    
    print(f"✅ Final video generated: {output_file}")
    return output_file


def main():
    parser = argparse.ArgumentParser(description="Generate complete video for a book")
    parser.add_argument("book_dir", help="Book directory name (e.g., 0024_pan_tadeusz)")
    parser.add_argument("--force", action="store_true", help="Force regeneration of intro/outro frames even if they exist")
    args = parser.parse_args()
    
    book_dir = args.book_dir
    print(f"🚀 Generating full video for: {book_dir}")
    
    try:
        # 1. Load book metadata
        print("📖 Loading book metadata...")
        book_data = load_book_yaml(book_dir)
        print(f"   Title: {book_data['title']}")
        print(f"   Author: {book_data['author']}")
        
        # 2. Create necessary directories
        print("📁 Creating directories...")
        create_directories(book_dir)
        
        # 3. Create personalized intro HTML
        print("🎨 Creating personalized intro...")
        intro_html_path = create_personalized_intro_html(book_dir, book_data)
        
        # 4. Generate intro frames
        intro_frames_dir = generate_intro_frames(book_dir, intro_html_path, args.force)
        
        # 5. Generate outro frames (shared)
        outro_frames_dir = generate_outro_frames(args.force)
        
        # 6. Find audio file
        print("🔊 Finding audio file...")
        audio_file = find_audio_file(book_dir)
        
        # 7. Generate final video
        output_file = generate_final_video(book_dir, intro_frames_dir, outro_frames_dir, audio_file)
        
        print(f"""
🎉 SUCCESS! Video generation completed.
   📂 Book: {book_dir}
   🎬 Output: {output_file}
   📏 Size: {output_file.stat().st_size / (1024*1024):.1f}MB
        """)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()