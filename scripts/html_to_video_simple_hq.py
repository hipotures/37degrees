#!/usr/bin/env python3
"""
High Quality HTML → Video (frame capture + high fidelity encode)

Why this approach:
- Playwright's built-in video capture produces heavily compressed WebM; re-encoding cannot recover detail.
- We capture high-resolution PNG frames at a fixed FPS, then encode with FFmpeg using
  slow preset, low CRF, debanding, and Lanczos scaling for crisp visuals and smooth gradients.
"""

import os
import sys
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


def create_simple_hq_video_from_html(
    html_path,
    output_path,
    duration=10,
    width=1024,
    height=1536,
    fps=30,
    dpr=2,
    encoder="libx264",
    tenbit=False,
    crf=None,
    bitrate=None,
    keep_frames=False,
    frames_dir_override: str | None = None,
    frames_only: bool = False,
):
    """
    Capture high-res PNG frames of the HTML at a fixed FPS and encode to MP4.

    - width/height: target video resolution (CSS pixels).
    - dpr: device pixel ratio for oversampling (2 recommended).
    - fps: frames per second to capture.
    """

    frames_dir = Path(frames_dir_override) if frames_dir_override else Path("temp_frames_hq")
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    print("🎬 Creating HIGH QUALITY video from HTML (frame capture)...")
    print(f"   Source: {html_path}")
    print(f"   Output: {output_path}")
    print(f"   Duration: {duration}s @ {fps}fps")
    print(f"   Viewport: {width}x{height} (DPR {dpr} → capture {width*dpr}x{height*dpr})")
    print(f"   Encoder: {encoder}{' (10-bit)' if tenbit else ''}")

    total_frames = int(duration * fps)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--force-color-profile=srgb',
                '--enable-gpu-rasterization',
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
                page.goto(html_path, wait_until="networkidle", timeout=60000)
            else:
                print(f"📄 Loading local file: {html_path}")
                if not os.path.exists(html_path):
                    raise FileNotFoundError(f"HTML file not found: {html_path}")
                page.goto(f"file://{os.path.abspath(html_path)}", wait_until="domcontentloaded")

            # Ensure fonts/animations initialized
            print("⏳ Waiting for page to stabilize...")
            page.wait_for_load_state("networkidle", timeout=30000)
            page.wait_for_timeout(1500)

            # Capture frames
            print(f"🎥 Capturing {total_frames} frames...")
            for i in range(total_frames):
                frame_path = frames_dir / f"frame_{i:06d}.png"
                page.screenshot(
                    path=str(frame_path),
                    clip={"x": 0, "y": 0, "width": width, "height": height},
                    animations="allow",
                )
                # Advance time between frames
                page.wait_for_timeout(int(1000 / fps))

            print("✅ Frame capture completed")

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
            # 10-bit reduces banding; gradfun usually unnecessary and may be bypassed
            vf = f"scale={width}:{height}:flags=lanczos,format=yuv420p10le"
        else:
            vf = f"scale={width}:{height}:flags=lanczos,format=yuv420p,gradfun=20"

        # Defaults
        use_encoder = encoder
        ffargs = ['ffmpeg', '-y', '-framerate', str(fps), '-i', str(frames_dir / 'frame_%06d.png')]

        if use_encoder in ("h264_nvenc", "hevc_nvenc"):
            # NVENC path (fast, high quality with VBR/CQ)
            pix_fmt = 'p010le' if tenbit and use_encoder == 'hevc_nvenc' else 'yuv420p'
            if tenbit and use_encoder == 'h264_nvenc':
                print("⚠️ h264_nvenc 10-bit is not widely supported. Switching to hevc_nvenc for 10-bit.")
                use_encoder = 'hevc_nvenc'
                pix_fmt = 'p010le'

            cq = '18' if crf is None else str(crf)
            # Sensible bitrate defaults for vertical 1080x1920 UI content
            target_bitrate = str(bitrate) if bitrate else ('25M' if use_encoder == 'h264_nvenc' else '20M')
            maxrate = '1.5x'
            if target_bitrate.endswith('M'):
                # derive maxrate and bufsize from target bitrate
                try:
                    tb = float(target_bitrate[:-1])
                    maxrate_val = f"{int(tb*2)}M"
                    bufsize_val = f"{int(tb*4)}M"
                except Exception:
                    maxrate_val = target_bitrate
                    bufsize_val = target_bitrate
            else:
                maxrate_val = target_bitrate
                bufsize_val = target_bitrate

            ffargs += [
                '-vf', vf,
                '-c:v', use_encoder,
                '-preset', 'p5',           # quality/speed tradeoff
                '-rc', 'vbr',
                '-cq', cq,
                '-b:v', target_bitrate,
                '-maxrate', maxrate_val,
                '-bufsize', bufsize_val,
                '-pix_fmt', pix_fmt,
                '-movflags', '+faststart',
                output_path,
            ]
        else:
            # CPU x264 path (very high quality)
            if tenbit:
                ffargs += [
                    '-vf', vf,
                    '-c:v', 'libx264',
                    '-preset', 'slow',
                    '-crf', str(crf if crf is not None else 18),
                    '-profile:v', 'high10',
                    '-pix_fmt', 'yuv420p10le',
                    '-movflags', '+faststart',
                    output_path,
                ]
            else:
                ffargs += [
                    '-vf', vf,
                    '-c:v', 'libx264',
                    '-preset', 'slow',
                    '-crf', str(crf if crf is not None else 14),
                    '-profile:v', 'high',
                    '-level:v', '4.2',
                    '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart',
                    output_path,
                ]

        result = subprocess.run(ffargs, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Encoding failed: {result.stderr}")
            return False

        # Cleanup
        if not keep_frames:
            shutil.rmtree(frames_dir)

        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"🎉 High quality video created: {output_path}")
        print(f"📊 File size: {file_size:.1f} MB")
        return True

    except Exception as e:
        print(f"❌ Encoding failed: {e}")
        if frames_dir.exists() and not keep_frames:
            shutil.rmtree(frames_dir)
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python html_to_video_simple_hq.py <html_path> <output_path> [duration] [fps] [width] [height] [dpr] [--nvenc|--encoder=hevc_nvenc|h264_nvenc|libx264] [--tenbit] [--crf=N] [--bitrate=25M] [--keep-frames] [--frames-dir=DIR] [--frames-only]")
        print("\nCaptures high-res frames and encodes with high-fidelity settings (slow preset, low CRF, debanding). Optional NVENC and 10-bit support.")
        print("\nExamples:")
        print("  python scripts/html_to_video_simple_hq.py 'www/podcast-intro-screen.html' 'intro_hq.mp4' 8 30 1024 1536 2 --crf=14")
        print("  python scripts/html_to_video_simple_hq.py 'www/podcast-outro-screen.html' 'outro_hq.mp4' 10 60 1024 1536 2 --nvenc --encoder=hevc_nvenc --tenbit --keep-frames --frames-dir=books/0006_don_quixote/intro_frames")
        print("  python scripts/html_to_video_simple_hq.py 'www/podcast-intro-screen.html' 'ignored.mp4' 8 30 1024 1536 2 --frames-only --frames-dir=books/0006_don_quixote/intro_frames")
        sys.exit(1)
    
    html_path = sys.argv[1]
    output_path = sys.argv[2]
    duration = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    fps = int(sys.argv[4]) if len(sys.argv) > 4 else 30
    width = int(sys.argv[5]) if len(sys.argv) > 5 else 1080
    height = int(sys.argv[6]) if len(sys.argv) > 6 else 1920
    dpr = int(sys.argv[7]) if len(sys.argv) > 7 else 2

    # Parse optional flags
    extra = _parse_extra_flags(sys.argv[8:]) if len(sys.argv) > 8 else {}
    encoder = 'libx264'
    tenbit = False
    crf = None
    bitrate = None
    keep_frames = False
    frames_dir_override = None
    frames_only = False

    if 'nvenc' in extra and extra['nvenc'] is True:
        encoder = 'hevc_nvenc'  # default NVENC choice (better 10-bit support)
    if 'encoder' in extra:
        encoder = str(extra['encoder'])
    if 'tenbit' in extra:
        tenbit = True
    if 'keep-frames' in extra:
        keep_frames = True
    if 'frames-dir' in extra:
        frames_dir_override = str(extra['frames-dir'])
    if 'frames-only' in extra:
        frames_only = True
    if 'crf' in extra:
        try:
            crf = int(extra['crf'])
        except Exception:
            pass
    if 'bitrate' in extra:
        bitrate = str(extra['bitrate'])
    
    # Ensure output has .mp4 extension
    if not output_path.endswith('.mp4'):
        output_path += '.mp4'
    
    success = create_simple_hq_video_from_html(
        html_path=html_path,
        output_path=output_path,
        duration=duration,
        width=width,
        height=height,
        fps=fps,
        dpr=dpr,
        encoder=encoder,
        tenbit=tenbit,
        crf=crf,
        bitrate=bitrate,
        keep_frames=keep_frames,
        frames_dir_override=frames_dir_override,
        frames_only=frames_only,
    )
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
