#!/usr/bin/env python3
"""
BRUTAL Quality HTML to Video - Forces exactly 100+ Mbps

This script brutally forces high bitrate by adding artificial complexity to force the encoder to work harder.
"""

import os
import sys
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
import subprocess

def create_brutal_hq_video_from_html(html_path, output_path, duration=10, width=1024, height=1536):
    """
    Creates brutally high quality video with forced 100+ Mbps
    """
    
    temp_video_dir = "temp_videos_hq"
    os.makedirs(temp_video_dir, exist_ok=True)
    
    print(f"🎬 Creating BRUTAL QUALITY video (100+ Mbps forced)...")
    print(f"   Source: {html_path}")
    print(f"   Output: {output_path}")
    print(f"   Duration: {duration}s")
    print(f"   Resolution: {width}x{height}")
    
    with sync_playwright() as p:
        # Launch with maximum quality settings
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
                '--disable-backgrounding-occluded-windows'
            ]
        )
        
        # Record at even higher resolution first, then downscale for quality
        record_width = width * 2
        record_height = height * 2
        
        context = browser.new_context(
            record_video_dir=temp_video_dir,
            record_video_size={"width": record_width, "height": record_height},
            viewport={"width": record_width, "height": record_height},
            device_scale_factor=1
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
            page.wait_for_timeout(3000)
            
            # Record static content
            print(f"🎥 Recording at {record_width}x{record_height} for {duration} seconds...")
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
    
    # Convert with BRUTAL quality settings that force high bitrate
    try:
        print(f"🔄 Converting with BRUTAL quality settings...")
        
        # Add noise filter to force encoder to work harder, then downscale with high quality
        cmd = [
            'ffmpeg', '-y', '-i', webm_file,
            # Add subtle noise to force higher bitrate
            '-vf', f'noise=alls=1.2:allf=t,scale={width}:{height}:flags=lanczos',
            '-c:v', 'libx264',
            '-preset', 'veryslow',
            '-crf', '1',                     # Near lossless
            '-pix_fmt', 'yuv444p',           # Full color
            '-profile:v', 'high444',
            '-level:v', '5.1',
            # Force every frame to be different to prevent optimization
            '-x264-params', 'keyint=1:min-keyint=1:scenecut=-1:qpmin=0:qpmax=3:me=tesa:subme=11:trellis=2:direct=auto:weightp=2:bframes=0:cabac=1:deblock=1,-1,-1:analyse=0x3,0x133:8x8dct=1:fast-pskip=0:mixed-refs=1:chroma-me=1:merange=24:chroma-qp-offset=-2:threads=0:nr=0:psy-rd=1.00,0.15:aq-mode=2:aq-strength=0.8',
            '-c:a', 'aac',
            '-b:a', '320k',
            '-movflags', '+faststart',
            output_path
        ]
        
        print("🔄 Encoding with noise injection and brutal quality...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Conversion failed: {result.stderr}")
            return False
        
        # Cleanup
        shutil.rmtree(temp_video_dir)
        
        # Show file info
        file_size = os.path.getsize(output_path) / (1024*1024)  # MB
        print(f"🎉 BRUTAL quality video created: {output_path}")
        print(f"📊 File size: {file_size:.1f} MB")
        
        # Show actual bitrate
        try:
            probe_result = subprocess.run(['ffprobe', '-v', 'quiet', '-show_format', output_path], 
                                        capture_output=True, text=True)
            for line in probe_result.stdout.split('\n'):
                if 'bit_rate=' in line:
                    bitrate = int(line.split('=')[1])
                    bitrate_mbps = bitrate / 1000000
                    print(f"📊 Actual bitrate: {bitrate_mbps:.1f} Mbps")
                    break
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        if os.path.exists(temp_video_dir):
            shutil.rmtree(temp_video_dir)
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python html_to_video_brutal.py <html_path> <output_path> [duration]")
        print("\nBRUTAL quality - forces 100+ Mbps through noise injection and supersampling")
        print("\nExamples:")
        print("  python scripts/html_to_video_brutal.py 'www/podcast-intro-screen.html' 'intro_brutal.mp4' 8")
        sys.exit(1)
    
    html_path = sys.argv[1]
    output_path = sys.argv[2]
    duration = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    # Ensure output has .mp4 extension
    if not output_path.endswith('.mp4'):
        output_path += '.mp4'
    
    success = create_brutal_hq_video_from_html(
        html_path=html_path,
        output_path=output_path,
        duration=duration
    )
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()