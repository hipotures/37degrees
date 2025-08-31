#!/usr/bin/env python3
"""
Improved HTML to Video with better rendering quality and animation handling.

Key improvements:
- Higher DPR (2) for better gradient rendering 
- Proportional animation slowdown preserving sequence
- Better rendering flags for quality
- Option to use video recording instead of screenshots
"""

import os
import sys
import time
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
import subprocess
from typing import Dict
import tempfile
import uuid

def _parse_extra_flags(argv_tail: list) -> Dict[str, str | bool]:
    opts: Dict[str, str | bool] = {}
    for arg in argv_tail:
        if arg.startswith("--") and "=" in arg:
            k, v = arg[2:].split("=", 1)
            opts[k.strip()] = v.strip()
        elif arg.startswith("--"):
            opts[arg[2:].strip()] = True
    return opts


def create_video_with_recording(
    html_path,
    output_path,
    duration=10,
    width=1080,
    height=1920,
    fps=30,
    dpr=2,  # Default to 2 for better quality
    frames_dir_override=None,
    frames_only=False,
):
    """
    Use Playwright's video recording to capture animations at natural speed.
    """
    print("🎬 Creating video using RECORDING method...")
    print(f"   Source: {html_path}")
    print(f"   Output: {output_path}")
    print(f"   Duration: {duration}s @ {fps}fps")
    print(f"   Resolution: {width}x{height} (DPR {dpr})")
    
    # Create temp directory for video
    temp_dir = Path(tempfile.mkdtemp(prefix="playwright_video_"))
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--force-color-profile=srgb',
                '--enable-gpu-rasterization',
                '--enable-accelerated-2d-canvas',
                '--enable-features=VaapiVideoDecoder',
                '--use-angle=gl',
                '--enable-unsafe-swiftshader',
                '--disable-web-security',
                '--disable-low-res-tiling',
                '--high-dpi-support=1',
                f'--force-device-scale-factor={dpr}',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
            ],
        )
        
        context = browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=dpr,
            record_video_dir=str(temp_dir),
            record_video_size={"width": width, "height": height},
        )
        
        page = context.new_page()
        
        try:
            # Load HTML
            html_path_str = str(html_path)
            if html_path_str.startswith('http'):
                print(f"📡 Loading URL: {html_path_str}")
                page.goto(html_path_str, wait_until="domcontentloaded", timeout=60000)
            else:
                print(f"📄 Loading local file: {html_path_str}")
                if not os.path.exists(html_path_str):
                    raise FileNotFoundError(f"HTML file not found: {html_path_str}")
                page.goto(f"file://{os.path.abspath(html_path_str)}", wait_until="domcontentloaded")
            
            # Wait for full duration to capture all animations
            print(f"⏳ Recording for {duration} seconds...")
            page.wait_for_timeout(int(duration * 1000))
            
        finally:
            # Close to save video
            context.close()
            browser.close()
    
    # Find the recorded video
    video_files = list(temp_dir.glob("*.webm"))
    if not video_files:
        print("❌ No video file was recorded")
        shutil.rmtree(temp_dir)
        return False
    
    recorded_video = video_files[0]
    print(f"📹 Video recorded: {recorded_video}")
    
    # If frames_only, extract frames from video
    if frames_only:
        frames_dir = Path(frames_dir_override) if frames_dir_override else Path(f"temp_frames_{uuid.uuid4().hex[:8]}")
        frames_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            print(f"🎞️ Extracting frames to: {frames_dir}")
            cmd = [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "info",
                "-i", str(recorded_video),
                "-r", str(fps),
                str(frames_dir / "frame_%06d.png")
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ Frames extracted to: {frames_dir}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Frame extraction failed: {e}")
            return False
        finally:
            shutil.rmtree(temp_dir)
        
        return True
    
    # Otherwise convert to desired video format
    try:
        print("🔄 Converting video to final format...")
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "info",
            "-i", str(recorded_video),
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "14",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(output_path)
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Video converted successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg conversion failed: {e}")
        return False
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
    
    print(f"🎉 Video created successfully: {output_path}")
    return True


def create_video_with_proportional_slowdown(
    html_path,
    output_path,
    duration=10,
    width=1080,
    height=1920,
    fps=30,
    dpr=2,
    encoder="libx264",
    crf=14,
    keep_frames=False,
    frames_dir_override=None,
    frames_only=False,
):
    """
    Capture with proportional animation slowdown that preserves sequence timing.
    
    Original animations: 0.3s, 0.8s, 1.2s, 1.8s, 2.0s, 2.2s, 2.5s
    With 10x slowdown: 3s, 8s, 12s, 18s, 20s, 22s, 25s (preserves relative timing)
    """
    
    frames_dir = Path(frames_dir_override) if frames_dir_override else Path(f"temp_frames_{uuid.uuid4().hex[:8]}")
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)
    
    print("🎬 Creating video with PROPORTIONAL SLOWDOWN...")
    print(f"   Source: {html_path}")
    print(f"   Output: {output_path}")
    print(f"   Duration: {duration}s @ {fps}fps")
    print(f"   Resolution: {width}x{height} (DPR {dpr})")
    
    total_frames = int(duration * fps)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--force-color-profile=srgb',
                '--enable-gpu-rasterization',
                '--enable-accelerated-2d-canvas',
                '--enable-features=VaapiVideoDecoder',
                '--use-angle=gl',
                '--enable-unsafe-swiftshader',
                '--disable-web-security',
                '--disable-low-res-tiling',
                '--high-dpi-support=1',
                f'--force-device-scale-factor={dpr}',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
            ],
        )
        
        context = browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=dpr,
        )
        
        page = context.new_page()
        
        try:
            # Load HTML
            html_path_str = str(html_path)
            if html_path_str.startswith('http'):
                print(f"📡 Loading URL: {html_path_str}")
                page.goto(html_path_str, wait_until="domcontentloaded", timeout=60000)
            else:
                print(f"📄 Loading local file: {html_path_str}")
                if not os.path.exists(html_path_str):
                    raise FileNotFoundError(f"HTML file not found: {html_path_str}")
                page.goto(f"file://{os.path.abspath(html_path_str)}", wait_until="domcontentloaded")
            
            # Apply proportional slowdown (20x to allow capture at half speed)
            # This preserves the sequence and relative timing
            page.add_style_tag(content="""
                *, *::before, *::after {
                    animation-duration: calc(var(--original-duration, 1s) * 20) !important;
                    animation-delay: calc(var(--original-delay, 0s) * 20) !important;
                }
                
                /* Specific overrides for known animations with their original timings */
                .logo-section { --original-delay: 0.3s; }  /* Will become 6s */
                .divider { --original-delay: 0.8s; }       /* Will become 16s */
                .book-section { --original-delay: 1.2s; }  /* Will become 24s */
                .book-author::before, .book-author::after { --original-delay: 1.8s; } /* 36s */
                .episode-number { --original-delay: 2s; }  /* Will become 40s */
                .corner-decoration { --original-delay: 2.2s; } /* Will become 44s */
                .logo-glow { --original-delay: 2.5s; }     /* Will become 50s */
            """)
            
            print("🎥 Capturing frames with proportional slowdown...")
            
            for i in range(total_frames):
                frame_path = frames_dir / f"frame_{i:06d}.png"
                page.screenshot(
                    path=str(frame_path),
                    clip={"x": 0, "y": 0, "width": width, "height": height},
                    animations="allow",
                )
                
                # Small delay between captures
                page.wait_for_timeout(50)
                
                if i % 10 == 0 or i == total_frames - 1:
                    progress = (i + 1) / total_frames * 100
                    print(f"   Frame {i+1}/{total_frames} ({progress:.1f}%)")
            
            print("✅ Frame capture completed")
            
        finally:
            context.close()
            browser.close()
    
    if frames_only:
        print("🖼️ Frames generated only (no encoding)")
        return True
    
    # Encode frames to video
    try:
        print("🔄 Encoding frames to video...")
        
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "info",
            "-framerate", str(fps),
            "-i", str(frames_dir / "frame_%06d.png"),
            "-c:v", encoder,
            "-preset", "slow",
            "-crf", str(crf),
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(output_path)
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Video encoding completed successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg encoding failed: {e}")
        return False
    finally:
        if not keep_frames and frames_dir.exists():
            print("🧹 Cleaning up temporary frames...")
            shutil.rmtree(frames_dir)
    
    print(f"🎉 Video created successfully: {output_path}")
    return True


def main():
    if len(sys.argv) < 3:
        print("Usage: python html_to_video_improved.py <html_path> <output_path> [duration] [fps] [width] [height] [dpr] [options...]")
        print("Options:")
        print("  --method=recording|slowdown  (default: recording)")
        print("  --frames-only                 (generate frames without encoding)")
        print("  --frames-dir=path            (custom frames directory)")
        print("  --keep-frames                (don't delete frames after encoding)")
        print("  --encoder=libx264            (video encoder)")
        print("  --crf=14                     (quality, lower=better)")
        print("\nExamples:")
        print("  python html_to_video_improved.py intro.html video.mp4")
        print("  python html_to_video_improved.py intro.html video.mp4 3 30 1080 1920 2 --method=recording")
        print("  python html_to_video_improved.py intro.html frames/ 3 30 --frames-only --method=slowdown")
        sys.exit(1)
    
    html_path = sys.argv[1]
    output_path = sys.argv[2]
    duration = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
    fps = int(sys.argv[4]) if len(sys.argv) > 4 else 30
    width = int(sys.argv[5]) if len(sys.argv) > 5 else 1080
    height = int(sys.argv[6]) if len(sys.argv) > 6 else 1920
    dpr = int(sys.argv[7]) if len(sys.argv) > 7 else 2
    
    # Parse additional flags
    extra_flags = _parse_extra_flags(sys.argv[8:])
    method = extra_flags.get("method", "recording")
    
    if method == "recording":
        success = create_video_with_recording(
            html_path=html_path,
            output_path=output_path,
            duration=duration,
            width=width,
            height=height,
            fps=fps,
            dpr=dpr,
            frames_dir_override=extra_flags.get("frames-dir"),
            frames_only=extra_flags.get("frames-only", False),
        )
    else:  # slowdown
        success = create_video_with_proportional_slowdown(
            html_path=html_path,
            output_path=output_path,
            duration=duration,
            fps=fps,
            width=width,
            height=height,
            dpr=dpr,
            encoder=extra_flags.get("encoder", "libx264"),
            crf=int(extra_flags.get("crf", 14)),
            keep_frames=extra_flags.get("keep-frames", False),
            frames_dir_override=extra_flags.get("frames-dir"),
            frames_only=extra_flags.get("frames-only", False),
        )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()