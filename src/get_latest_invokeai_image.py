#!/usr/bin/env python3
"""
Get the latest generated image from InvokeAI output directory
This is a workaround for the API cache issue
"""

import sys
import time
from pathlib import Path
import shutil


def get_latest_image(wait_time=3):
    """Get the most recently created image from InvokeAI output directory"""
    
    # Wait for image to be saved
    print(f"Waiting {wait_time}s for image to be saved...")
    time.sleep(wait_time)
    
    # InvokeAI output directory
    output_dir = Path.home() / "DEV" / "invokeai" / "outputs" / "images"
    
    if not output_dir.exists():
        print(f"Error: InvokeAI output directory not found: {output_dir}")
        return None
    
    # Get all PNG files
    png_files = list(output_dir.glob("*.png"))
    
    if not png_files:
        print("No PNG files found in InvokeAI output directory")
        return None
    
    # Sort by modification time (newest first)
    png_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    latest_file = png_files[0]
    mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(latest_file.stat().st_mtime))
    
    print(f"Latest image: {latest_file.name}")
    print(f"Modified: {mod_time}")
    
    return latest_file


def copy_latest_to_destination(dest_path):
    """Copy the latest InvokeAI image to destination"""
    latest = get_latest_image()
    
    if latest:
        shutil.copy2(latest, dest_path)
        print(f"Copied to: {dest_path}")
        return True
    
    return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        dest = sys.argv[1]
        success = copy_latest_to_destination(dest)
        sys.exit(0 if success else 1)
    else:
        # Just print info about latest image
        get_latest_image()