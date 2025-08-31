#!/usr/bin/env python3
"""
HTML to Video with Real-time Animation Capture

This script captures animations by allowing real time to pass between frames,
ensuring CSS animations and JavaScript effects are properly recorded.

Key difference from html_to_video_simple_hq.py:
- Uses actual time delays between frames to capture animations
- Maintains high PNG quality while preserving animation timing
"""

import os
import sys
import time
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
import subprocess
from typing import Dict

def _parse_extra_flags(argv_tail: list) -> Dict[str, str | bool]:
    opts: Dict[str, str | bool] = {}
    for arg in argv_tail:
        if arg.startswith("--") and "=" in arg:
            k, v = arg[2:].split("=", 1)
            opts[k.strip()] = v.strip()
        elif arg.startswith("--"):
            opts[arg[2:].strip()] = True
    return opts


def create_animated_video_from_html(
    html_path,
    output_path,
    duration=10,
    width=720,
    height=1080,
    fps=30,
    dpr=1,  # Reduce DPR for speed
    encoder="libx264",
    tenbit=False,
    crf=None,
    bitrate=None,
    keep_frames=False,
    frames_dir_override: str | None = None,
    frames_only: bool = False,
):
    """
    Capture high-res PNG frames with real animation timing and encode to MP4.

    - width/height: target video resolution (CSS pixels).
    - dpr: device pixel ratio for oversampling (2 recommended).
    - fps: frames per second to capture with real timing.
    """

    frames_dir = Path(frames_dir_override) if frames_dir_override else Path("temp_frames_animated")
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    print("🎬 Creating ANIMATED HIGH QUALITY video from HTML...")
    print(f"   Source: {html_path}")
    print(f"   Output: {output_path}")
    print(f"   Duration: {duration}s @ {fps}fps (real-time animation)")
    print(f"   Viewport: {width}x{height} (DPR {dpr} → capture {width*dpr}x{height*dpr})")
    print(f"   Encoder: {encoder}{' (10-bit)' if tenbit else ''}")

    total_frames = int(duration * fps)
    frame_interval = 1.0 / fps  # Real seconds between frames

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
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
            ],
        )

        context = browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=dpr,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari"
            ),
        )

        page = context.new_page()

        try:
            # Load HTML
            if html_path.startswith('http'):
                print(f"📡 Loading URL: {html_path}")
                page.goto(html_path, wait_until="domcontentloaded", timeout=60000)
            else:
                print(f"📄 Loading local file: {html_path}")
                if not os.path.exists(html_path):
                    raise FileNotFoundError(f"HTML file not found: {html_path}")
                page.goto(f"file://{os.path.abspath(html_path)}", wait_until="domcontentloaded")

            # Slow down all CSS animations to make them capturable
            page.add_style_tag(content="""
                *, *::before, *::after {
                    animation-duration: 20s !important;
                    animation-delay: 2s !important;
                    animation-timing-function: linear !important;
                }
            """)
            
            # Start capturing immediately - don't wait for animations to finish!
            print("🚀 Starting capture immediately after DOM load (with slowed animations)...")

            # Record start time for real-time capture
            start_time = time.time()
            
            # Capture frames with auto-stop when identical
            print(f"🎥 Capturing up to {total_frames} frames (auto-stop when animation ends)...")
            last_frame_hash = None
            identical_count = 0
            
            for i in range(total_frames):
                frame_path = frames_dir / f"frame_{i:06d}.png"
                page.screenshot(
                    path=str(frame_path),
                    clip={"x": 0, "y": 0, "width": width, "height": height},
                    animations="allow",
                )
                
                # Check if frame is identical to previous (simple file size check)
                if i > 5:  # Start checking after first few frames
                    current_size = frame_path.stat().st_size
                    if last_frame_hash and abs(current_size - last_frame_hash) < 1000:  # Within 1KB
                        identical_count += 1
                        if identical_count >= 3:  # 3 identical frames in a row
                            print(f"   Animation ended at frame {i-2} - stopping capture")
                            # Remove last 3 identical frames
                            for j in range(3):
                                (frames_dir / f"frame_{i-j:06d}.png").unlink(missing_ok=True)
                            break
                    else:
                        identical_count = 0
                        last_frame_hash = current_size
                
                # Minimal wait between frames
                page.wait_for_timeout(50)  # Just 50ms
                
                # Progress indicator
                if i % 10 == 0 or i == total_frames - 1:
                    elapsed = time.time() - start_time
                    progress = (i + 1) / total_frames * 100
                    print(f"   Frame {i+1}/{total_frames} ({progress:.1f}%) - {elapsed:.1f}s elapsed")

            print("✅ Frame capture completed with real-time animation")

        except Exception as e:
            print(f"❌ Error during capture: {e}")
            try:
                context.close()
            finally:
                browser.close()
            if frames_dir.exists():
                shutil.rmtree(frames_dir)
            return False
        finally:
            context.close()
            browser.close()

    # Optionally: only generate frames
    if frames_only:
        print("🖼️ Frames generated only (no encoding) as requested.")
        return True

    # Encode frames to high-quality MP4
    try:
        print("🔄 Encoding frames to MP4 (high-fidelity)...")

        # Build filter chain
        if tenbit:
            pix_fmt = "yuv420p10le"
            profile = "main10"
        else:
            pix_fmt = "yuv420p"
            profile = "main"

        # Enhanced filter for best quality
        vf_chain = [
            f"scale={width}:{height}:flags=lanczos+accurate_rnd+full_chroma_int",
            "format=yuv444p" if not tenbit else "format=yuv444p10le",
            f"format={pix_fmt}",
            "bwdif=mode=send_frame:parity=auto:deint=interlaced"
        ]

        # FFmpeg encoding command
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "info",
            "-framerate", str(fps),
            "-i", str(frames_dir / "frame_%06d.png"),
            "-vf", ",".join(vf_chain),
            "-c:v", encoder,
        ]

        # Encoder-specific settings
        if encoder == "libx264":
            preset_crf = crf if crf is not None else 14
            cmd.extend(["-preset", "slower", "-crf", str(preset_crf), "-profile:v", profile])
        elif encoder in ["hevc_nvenc", "h264_nvenc"]:
            preset_cq = crf if crf is not None else 14
            cmd.extend(["-preset", "p7", "-cq", str(preset_cq), "-profile:v", profile])
            if bitrate:
                cmd.extend(["-b:v", bitrate])

        # Output settings
        cmd.extend([
            "-movflags", "+faststart",
            "-pix_fmt", pix_fmt,
            str(output_path)
        ])

        print(f"🔧 FFmpeg command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Video encoding completed successfully")
        else:
            print(f"❌ FFmpeg encoding failed: {result.stderr}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg encoding failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during encoding: {e}")
        return False
    finally:
        # Cleanup frames unless requested to keep
        if not keep_frames and frames_dir.exists():
            print("🧹 Cleaning up temporary frames...")
            shutil.rmtree(frames_dir)

    print(f"🎉 Animation video created successfully: {output_path}")
    return True


def main():
    if len(sys.argv) < 3:
        print("Usage: python html_to_video_30fps.py <html_path> <output_path> [duration] [fps] [width] [height] [dpr] [options...]")
        print("Example: python html_to_video_30fps.py intro.html video.mp4 10 30 1024 1536 2 --encoder=libx264 --crf=14")
        print("Options: --frames-only --frames-dir=path --keep-frames --encoder=libx264 --crf=14 --bitrate=20M --tenbit")
        sys.exit(1)

    html_path = sys.argv[1]
    output_path = sys.argv[2]
    duration = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0
    fps = int(sys.argv[4]) if len(sys.argv) > 4 else 30
    width = int(sys.argv[5]) if len(sys.argv) > 5 else 1024
    height = int(sys.argv[6]) if len(sys.argv) > 6 else 1536
    dpr = int(sys.argv[7]) if len(sys.argv) > 7 else 2

    # Parse additional flags
    extra_flags = _parse_extra_flags(sys.argv[8:])

    success = create_animated_video_from_html(
        html_path=html_path,
        output_path=output_path,
        duration=duration,
        fps=fps,
        width=width,
        height=height,
        dpr=dpr,
        encoder=extra_flags.get("encoder", "libx264"),
        tenbit=extra_flags.get("tenbit", False),
        crf=int(extra_flags["crf"]) if "crf" in extra_flags else None,
        bitrate=extra_flags.get("bitrate"),
        keep_frames=extra_flags.get("keep-frames", False),
        frames_dir_override=extra_flags.get("frames-dir"),
        frames_only=extra_flags.get("frames-only", False),
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()