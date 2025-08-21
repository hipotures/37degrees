#!/usr/bin/env python3
"""
HTML to Video Generator using Playwright

Creates video recordings from HTML files or web pages using Playwright's built-in video recording.
Supports local HTML files, web URLs, animations, and interactive elements.

Usage:
    python scripts/html_to_video.py <html_path> <output_path> [duration] [width] [height]
    python scripts/html_to_video.py "site/index.html" "demo.webm" 10 1920 1080
    python scripts/html_to_video.py "https://example.com" "output.webm" 15
"""

import os
import sys
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

def create_video_from_html(html_path, output_path, duration=10, width=1024, height=1536, 
                          headless=True, interactions=None):
    """
    Creates video from HTML file using Playwright
    
    Args:
        html_path: Path to HTML file or URL
        output_path: Output video path (.webm recommended)
        duration: Recording duration in seconds
        width, height: Video resolution
        headless: Run browser in headless mode
        interactions: Optional list of interactions to perform during recording
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    temp_video_dir = "temp_videos"
    os.makedirs(temp_video_dir, exist_ok=True)
    
    print(f"🎬 Starting video recording...")
    print(f"   Source: {html_path}")
    print(f"   Output: {output_path}")
    print(f"   Duration: {duration}s")
    print(f"   Resolution: {width}x{height}")
    
    with sync_playwright() as p:
        # Launch Chromium browser with highest quality settings for gradients
        browser = p.chromium.launch(
            headless=headless,
            args=[
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--enable-unsafe-swiftshader',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--force-device-scale-factor=1',     # Ensure 1:1 pixel mapping
                '--high-dpi-support=1',              # Better quality on high DPI
                '--force-color-profile=srgb',        # Consistent colors
                '--disable-gpu-sandbox',             # Better video encoding
                '--force-gpu-rasterization',         # Force GPU rendering
                '--enable-gpu-rasterization',        # Enable GPU acceleration
                '--disable-low-res-tiling',          # Disable low resolution optimizations
                '--disable-partial-raster',          # Full quality rendering
                '--disable-checker-imaging'          # Better image quality
            ]
        )
        
        # Create context with high quality video recording
        context = browser.new_context(
            record_video_dir=temp_video_dir,
            record_video_size={"width": width, "height": height},
            viewport={"width": width, "height": height},
            device_scale_factor=1,  # Ensure 1:1 pixel mapping
            # Optional: Set user agent for better compatibility
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        page = context.new_page()
        
        try:
            # Load HTML content
            if html_path.startswith('http'):
                print(f"📡 Loading URL: {html_path}")
                page.goto(html_path, wait_until="networkidle", timeout=30000)
            else:
                print(f"📄 Loading local file: {html_path}")
                if not os.path.exists(html_path):
                    raise FileNotFoundError(f"HTML file not found: {html_path}")
                page.goto(f"file://{os.path.abspath(html_path)}", wait_until="domcontentloaded")
            
            # Wait for page to be fully loaded
            print("⏳ Waiting for page to load...")
            page.wait_for_load_state("networkidle", timeout=15000)
            
            # Additional wait for any animations or dynamic content
            page.wait_for_timeout(2000)
            
            # Perform custom interactions if provided
            if interactions:
                print("🎯 Performing interactions...")
                for interaction in interactions:
                    try:
                        if interaction['type'] == 'click':
                            page.click(interaction['selector'])
                        elif interaction['type'] == 'scroll':
                            page.evaluate(f"window.scrollTo(0, {interaction['y']})")
                        elif interaction['type'] == 'hover':
                            page.hover(interaction['selector'])
                        elif interaction['type'] == 'type':
                            page.fill(interaction['selector'], interaction['text'])
                        elif interaction['type'] == 'wait':
                            page.wait_for_timeout(interaction['duration'])
                        
                        # Small pause between interactions
                        page.wait_for_timeout(500)
                    except Exception as e:
                        print(f"⚠️  Interaction failed: {e}")
            
            # Record for specified duration
            print(f"🎥 Recording for {duration} seconds...")
            
            # Just wait for the specified duration without scrolling
            # This is perfect for intro/outro screens that should be static
            page.wait_for_timeout(duration * 1000)
            
            print("✅ Recording completed")
            
        except Exception as e:
            print(f"❌ Error during recording: {e}")
            return False
        finally:
            context.close()
            browser.close()
    
    # Move video to target location
    video_files = list(Path(temp_video_dir).glob("*.webm"))
    if video_files:
        try:
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(video_files[0]), output_path)
            shutil.rmtree(temp_video_dir)
            print(f"🎉 Video saved: {output_path}")
            
            # Show file info
            file_size = os.path.getsize(output_path) / (1024*1024)  # MB
            print(f"📊 File size: {file_size:.1f} MB")
            
            return True
        except Exception as e:
            print(f"❌ Error saving video: {e}")
            return False
    else:
        print("❌ No video file generated")
        if os.path.exists(temp_video_dir):
            shutil.rmtree(temp_video_dir)
        return False

def create_demo_interactions():
    """
    Example interaction sequence for demos
    """
    return [
        {"type": "wait", "duration": 1000},
        {"type": "scroll", "y": 500},
        {"type": "wait", "duration": 2000},
        {"type": "hover", "selector": "h1"},
        {"type": "wait", "duration": 1000},
        {"type": "scroll", "y": 1000},
        {"type": "wait", "duration": 2000},
        {"type": "scroll", "y": 0},
        {"type": "wait", "duration": 1000}
    ]

def convert_to_mp4(webm_path, mp4_path=None):
    """
    Convert .webm to .mp4 using FFmpeg with high quality settings
    """
    if mp4_path is None:
        mp4_path = webm_path.replace('.webm', '.mp4')
    
    try:
        import subprocess
        cmd = [
            'ffmpeg', '-i', webm_path,
            '-c:v', 'libx264',           # H.264 codec
            '-crf', '15',                # Even higher quality for gradients
            '-preset', 'veryslow',       # Best compression quality
            '-pix_fmt', 'yuv444p',       # Better color depth (if supported)
            '-profile:v', 'high444',     # High quality profile
            '-bf', '0',                  # No B-frames for better gradient quality
            '-g', '1',                   # Every frame is keyframe (best quality)
            '-c:a', 'aac',               # AAC audio codec
            '-b:a', '256k',              # Higher audio bitrate
            '-movflags', '+faststart',   # Better streaming support
            '-y', mp4_path
        ]
        
        print(f"🔄 Converting to high quality MP4: {mp4_path}")
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ High quality MP4 created: {mp4_path}")
        return mp4_path
    except (ImportError, subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"⚠️  MP4 conversion failed: {e}")
        print("   Install FFmpeg for MP4 conversion support")
        return None

def main():
    if len(sys.argv) < 3:
        print("Usage: python html_to_video.py <html_path> <output_path> [duration] [width] [height]")
        print("\nExamples:")
        print("  python scripts/html_to_video.py 'site/index.html' 'demo.webm' 10")
        print("  python scripts/html_to_video.py 'https://example.com' 'output.webm' 15 1280 720")
        print("  python scripts/html_to_video.py 'books/0001_alice_in_wonderland/site/index.html' 'alice_demo.webm'")
        print("  python scripts/html_to_video.py 'site/index.html' 'vertical.webm' 10 1024 1536  # ChatGPT format")
        sys.exit(1)
    
    html_path = sys.argv[1]
    output_path = sys.argv[2]
    duration = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    width = int(sys.argv[4]) if len(sys.argv) > 4 else 1024
    height = int(sys.argv[5]) if len(sys.argv) > 5 else 1536
    
    # Ensure output has .webm extension
    if not output_path.endswith('.webm'):
        output_path += '.webm'
    
    # Create video
    success = create_video_from_html(
        html_path=html_path,
        output_path=output_path,
        duration=duration,
        width=width,
        height=height,
        headless=True,
        interactions=None  # Use default smooth scrolling
    )
    
    if success:
        # Optional: Convert to MP4
        if '--mp4' in sys.argv:
            convert_to_mp4(output_path)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()