#!/usr/bin/env python3
"""
High Quality HTML to Video - Specialized for gradients

Creates the highest possible quality video from HTML with special focus on smooth gradients.
Uses uncompressed intermediate format to avoid quality loss.
"""

import os
import sys
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
import subprocess

def create_hq_video_from_html(html_path, output_path, duration=10, width=1024, height=1536):
    """
    Creates highest quality video from HTML with focus on gradients
    """
    
    temp_video_dir = "temp_videos_hq"
    os.makedirs(temp_video_dir, exist_ok=True)
    
    print(f"🎬 Creating ULTRA HIGH QUALITY video...")
    print(f"   Source: {html_path}")
    print(f"   Output: {output_path}")
    print(f"   Duration: {duration}s")
    print(f"   Resolution: {width}x{height}")
    
    with sync_playwright() as p:
        # Launch with absolute maximum quality settings
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-web-security',
                '--force-device-scale-factor=1',
                '--force-color-profile=srgb',
                '--disable-gpu-sandbox',
                '--force-gpu-rasterization',
                '--enable-gpu-rasterization', 
                '--disable-low-res-tiling',
                '--disable-partial-raster',
                '--disable-checker-imaging',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-features=TranslateUI',
                '--disable-extensions',
                '--no-first-run',
                '--disable-default-apps'
            ]
        )
        
        # Context with maximum quality
        context = browser.new_context(
            record_video_dir=temp_video_dir,
            record_video_size={"width": width, "height": height},
            viewport={"width": width, "height": height},
            device_scale_factor=1,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        page = context.new_page()
        
        try:
            # Load HTML
            if html_path.startswith('http'):
                print(f"📡 Loading URL: {html_path}")
                page.goto(html_path, wait_until="networkidle", timeout=30000)
            else:
                print(f"📄 Loading local file: {html_path}")
                if not os.path.exists(html_path):
                    raise FileNotFoundError(f"HTML file not found: {html_path}")
                page.goto(f"file://{os.path.abspath(html_path)}", wait_until="domcontentloaded")
            
            # Wait for full load
            print("⏳ Waiting for page to load...")
            page.wait_for_load_state("networkidle", timeout=15000)
            page.wait_for_timeout(3000)  # Extra time for animations to start
            
            # Record static content
            print(f"🎥 Recording static content for {duration} seconds...")
            page.wait_for_timeout(duration * 1000)
            
            print("✅ Recording completed")
            
        except Exception as e:
            print(f"❌ Error during recording: {e}")
            return False
        finally:
            context.close()
            browser.close()
    
    # Find the recorded WebM file
    video_files = list(Path(temp_video_dir).glob("*.webm"))
    if not video_files:
        print("❌ No video file generated")
        if os.path.exists(temp_video_dir):
            shutil.rmtree(temp_video_dir)
        return False
    
    webm_file = str(video_files[0])
    
    # Convert with ultra-high quality settings optimized for gradients
    try:
        print(f"🔄 Converting to ultra-high quality MP4...")
        
        # Two-pass encoding for absolute best quality
        temp_mp4 = output_path.replace('.mp4', '_temp.mp4')
        
        # Pass 1: Analysis (use bitrate for 2-pass)
        cmd_pass1 = [
            'ffmpeg', '-y', '-i', webm_file,
            '-c:v', 'libx264',
            '-preset', 'veryslow',
            '-b:v', '20M',                   # High bitrate for ultra quality
            '-pix_fmt', 'yuv444p10le',       # 10-bit color depth
            '-profile:v', 'high444',         # Highest quality profile
            '-level:v', '5.1',
            '-bf', '0',                      # No B-frames
            '-g', '1',                       # All keyframes
            '-qmin', '0',                    # Minimum quantizer
            '-qmax', '10',                   # Maximum quantizer (very low)
            '-qdiff', '1',                   # Small quantizer difference
            '-me_method', 'tesa',            # Best motion estimation
            '-subq', '11',                   # Maximum subpixel refinement
            '-trellis', '2',                 # Rate distortion optimization
            '-pass', '1',
            '-passlogfile', 'ffmpeg2pass',
            '-f', 'null',
            '/dev/null'
        ]
        
        # Pass 2: Encoding (use bitrate instead of CRF for 2-pass)
        cmd_pass2 = [
            'ffmpeg', '-y', '-i', webm_file,
            '-c:v', 'libx264',
            '-preset', 'veryslow',
            '-b:v', '20M',  # High bitrate instead of CRF
            '-pix_fmt', 'yuv444p10le',
            '-profile:v', 'high444',
            '-level:v', '5.1', 
            '-bf', '0',
            '-g', '1',
            '-qmin', '0',
            '-qmax', '10',
            '-qdiff', '1',
            '-me_method', 'tesa',
            '-subq', '11',
            '-trellis', '2',
            '-pass', '2',
            '-passlogfile', 'ffmpeg2pass',
            '-c:a', 'aac',
            '-b:a', '320k',
            '-movflags', '+faststart',
            temp_mp4
        ]
        
        print("🔄 Pass 1/2: Analyzing video...")
        result1 = subprocess.run(cmd_pass1, capture_output=True, text=True)
        if result1.returncode != 0:
            print(f"⚠️  Pass 1 warning: {result1.stderr}")
        
        print("🔄 Pass 2/2: Encoding ultra-high quality video...")
        result2 = subprocess.run(cmd_pass2, capture_output=True, text=True)
        if result2.returncode != 0:
            print(f"❌ Pass 2 failed: {result2.stderr}")
            return False
        
        # Final step: Convert to standard format for compatibility
        cmd_final = [
            'ffmpeg', '-y', '-i', temp_mp4,
            '-c:v', 'libx264',
            '-crf', '15',
            '-preset', 'slow',
            '-pix_fmt', 'yuv420p',           # Compatible format
            '-profile:v', 'high',
            '-level:v', '4.1',
            '-c:a', 'copy',
            '-movflags', '+faststart',
            output_path
        ]
        
        print("🔄 Creating final compatible version...")
        result3 = subprocess.run(cmd_final, capture_output=True, text=True)
        if result3.returncode != 0:
            print(f"❌ Final conversion failed: {result3.stderr}")
            return False
        
        # Cleanup
        if os.path.exists(temp_mp4):
            os.remove(temp_mp4)
        for log_file in Path('.').glob('ffmpeg2pass*'):
            log_file.unlink()
            
        shutil.rmtree(temp_video_dir)
        
        # Show file info
        file_size = os.path.getsize(output_path) / (1024*1024)  # MB
        print(f"🎉 Ultra-high quality video created: {output_path}")
        print(f"📊 File size: {file_size:.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        if os.path.exists(temp_video_dir):
            shutil.rmtree(temp_video_dir)
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python html_to_video_uncompressed.py <html_path> <output_path> [duration]")
        print("\nOptimized for smooth gradients and highest quality output")
        print("\nExamples:")
        print("  python scripts/html_to_video_uncompressed.py 'www/podcast-intro-screen.html' 'intro_hq.mp4' 8")
        print("  python scripts/html_to_video_uncompressed.py 'www/podcast-outro-screen.html' 'outro_hq.mp4' 10")
        sys.exit(1)
    
    html_path = sys.argv[1]
    output_path = sys.argv[2]
    duration = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    # Ensure output has .mp4 extension
    if not output_path.endswith('.mp4'):
        output_path += '.mp4'
    
    success = create_hq_video_from_html(
        html_path=html_path,
        output_path=output_path,
        duration=duration
    )
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()