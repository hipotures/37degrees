#!/usr/bin/env python3
"""
Generate videos for all books sequentially
"""

import os
import sys
import yaml
from pathlib import Path
import subprocess
import time

def load_series(series_file):
    """Load series configuration"""
    with open(series_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def generate_book_video(book_path):
    """Generate video for a single book"""
    print(f"\n{'='*60}")
    print(f"Processing: {book_path}")
    print(f"{'='*60}")
    
    book_dir = Path(book_path).parent
    
    # Step 1: Generate images with InvokeAI
    print("\n1. Generating images with InvokeAI...")
    cmd = [sys.executable, "src/invokeai_generator.py", book_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error generating images: {result.stderr}")
        return False
    print("✓ Images generated")
    
    # Step 2: Apply text overlays
    print("\n2. Applying text overlays...")
    cmd = [sys.executable, "src/text_overlay.py", book_path, "--process-all"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error applying text: {result.stderr}")
        # Continue anyway - maybe text overlay is not needed
    else:
        print("✓ Text overlays applied")
    
    # Step 3: Create video
    print("\n3. Creating video...")
    os.chdir(book_dir)
    cmd = [sys.executable, "create_video.py"]
    result = subprocess.run(cmd, input="n\n", capture_output=True, text=True)
    os.chdir("../..")
    
    if result.returncode == 0 or "Video created successfully" in result.stdout:
        print("✓ Video created successfully")
        
        # Find the video file
        video_files = list(book_dir.glob("*_tiktok.mp4"))
        if video_files:
            print(f"✓ Output: {video_files[0]}")
        return True
    else:
        print(f"Error creating video: {result.stderr}")
        return False

def main():
    """Main function"""
    series_file = "content/classics.yaml"
    
    if len(sys.argv) > 1:
        series_file = sys.argv[1]
    
    if not Path(series_file).exists():
        print(f"Error: Series file not found: {series_file}")
        sys.exit(1)
    
    # Load series
    series = load_series(series_file)
    books = series.get('books', [])
    
    print(f"37 DEGREES - Video Generator")
    print(f"Series: {series.get('title', 'Unknown')}")
    print(f"Books to process: {len(books)}")
    print(f"{'='*60}\n")
    
    # Process each book
    successful = 0
    failed = 0
    
    for i, book in enumerate(books, 1):
        book_path = book.get('path', '')
        if not book_path or not Path(book_path).exists():
            print(f"\n⚠️  Skipping book {i}: Invalid path {book_path}")
            failed += 1
            continue
        
        print(f"\nProcessing book {i}/{len(books)}: {book.get('title', 'Unknown')}")
        
        try:
            if generate_book_video(book_path):
                successful += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Error processing {book_path}: {e}")
            failed += 1
        
        # Small delay between books
        time.sleep(2)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total books: {len(books)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()