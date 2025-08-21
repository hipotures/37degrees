#!/usr/bin/env python3
"""
Compose video from PNGs with optional intro/outro frame sequences (MoviePy).

Features
- Main slideshow from still PNGs with crossfades, aligned to audio or total duration.
- Optional intro/outro as frame sequences (e.g., frames generated from HTML).
- High-quality H.264 output with CRF control.

Notes
- MoviePy rendering is CPU-bound and single-threaded; use the FFmpeg variant for speed.
"""

import argparse
import glob
import os
from typing import List, Optional, Tuple

from moviepy import *
from moviepy.video.fx import FadeIn, FadeOut, CrossFadeIn, CrossFadeOut


def list_pngs_sorted(directory: str, pattern: Optional[str] = None) -> List[str]:
    if pattern:
        return sorted(glob.glob(os.path.join(directory, pattern)))
    return sorted(glob.glob(os.path.join(directory, "*.png")))


def main():
    ap = argparse.ArgumentParser(description="Compose PNG slideshow with optional intro/outro frames (MoviePy)")
    ap.add_argument("images_dir", help="Directory with main slideshow PNGs (stills)")
    ap.add_argument("output", help="Output video path (e.g., output/moviepy_compose.mp4)")
    ap.add_argument("--audio", help="Optional audio file to align total duration", default=None)
    ap.add_argument("--total-duration", type=float, default=None, help="Total duration in seconds if no audio")
    ap.add_argument("--fps", type=int, default=30, help="Output FPS")
    ap.add_argument("--fade", type=float, default=2.5, help="Crossfade duration (seconds)")
    ap.add_argument("--intro-frames", default=None, help="Directory with intro PNG frames (sequence)")
    ap.add_argument("--intro-fps", type=int, default=30, help="FPS for intro frames")
    ap.add_argument("--intro-pattern", default="frame_%06d.png", help="Pattern for intro frames (ignored by MoviePy; uses glob)")
    ap.add_argument("--outro-frames", default=None, help="Directory with outro PNG frames (sequence)")
    ap.add_argument("--outro-fps", type=int, default=30, help="FPS for outro frames")
    ap.add_argument("--outro-pattern", default="frame_%06d.png", help="Pattern for outro frames (ignored by MoviePy; uses glob)")
    ap.add_argument("--crf", type=int, default=14, help="x264 CRF (lower = better)")
    ap.add_argument("--preset", default="slow", help="x264 preset (slow/medium/fast)")
    args = ap.parse_args()

    # Gather main images
    main_images = list_pngs_sorted(args.images_dir)
    if not main_images:
        raise SystemExit(f"No PNG images found in {args.images_dir}")

    # Intro/outro clips
    intro_clip = None
    outro_clip = None
    intro_duration = 0.0
    outro_duration = 0.0

    if args.intro_frames:
        intro_frames = list_pngs_sorted(args.intro_frames)
        if intro_frames:
            intro_clip = ImageSequenceClip(intro_frames, fps=args.intro_fps)
            intro_duration = intro_clip.duration

    if args.outro_frames:
        outro_frames = list_pngs_sorted(args.outro_frames)
        if outro_frames:
            outro_clip = ImageSequenceClip(outro_frames, fps=args.outro_fps)
            outro_duration = outro_clip.duration

    # Determine total/main durations
    audio = None
    total_duration = None
    if args.audio:
        audio = AudioFileClip(args.audio)
        # Total = intro + audio + outro; main section matches audio length
        total_duration = intro_duration + audio.duration + outro_duration
    elif args.total_duration:
        total_duration = float(args.total_duration)
    else:
        # Fallback: 3s per image + crossfades
        total_duration = len(main_images) * 3.0

    main_target = max(0.1, total_duration - intro_duration - outro_duration)

    n = len(main_images)
    fade = args.fade if n > 1 else 0.0
    if n > 0:
        clip_duration = (main_target + fade * (n - 1)) / n
    else:
        clip_duration = 0
    start_interval = max(0.0, clip_duration - fade)

    # Build main clips
    clips = []
    for i, img_path in enumerate(main_images):
        c = ImageClip(img_path, duration=clip_duration)
        if i == 0:
            if fade > 0:
                c = c.with_effects([FadeIn(fade), CrossFadeOut(fade)]) if n > 1 else c.with_effects([FadeIn(fade)])
        elif i == n - 1:
            c = c.with_effects([CrossFadeIn(fade), FadeOut(fade)]) if fade > 0 else c
        else:
            c = c.with_effects([CrossFadeIn(fade), CrossFadeOut(fade)]) if fade > 0 else c

        # Start after intro, with crossfade overlap
        start_time = max(0.0, intro_duration - fade) + i * start_interval
        c = c.with_start(start_time)
        clips.append(c)

    # Intro/outro fade handling
    if intro_clip:
        # Fade out to overlap
        intro_clip = intro_clip.with_effects([CrossFadeOut(fade)]) if fade > 0 else intro_clip
        intro_clip = intro_clip.with_start(0)
        clips.insert(0, intro_clip)

    if outro_clip:
        # Place outro to overlap with end of main
        main_total = (n * clip_duration) - (n - 1) * fade if n > 0 else 0.0
        outro_start = max(0.0, intro_duration + main_total - fade)
        outro_clip = outro_clip.with_effects([CrossFadeIn(fade)]) if fade > 0 else outro_clip
        outro_clip = outro_clip.with_start(outro_start)
        clips.append(outro_clip)

    # Composite
    if not clips:
        raise SystemExit("No clips to compose")

    size = clips[0].size
    video = CompositeVideoClip(clips, size=size)

    if audio:
        # Offset audio to start after intro; end naturally before outro
        video = video.with_audio(audio.with_start(intro_duration))
        # Ensure final duration includes intro + main(audio length) + outro
        video = video.with_duration(total_duration)
    else:
        # Ensure final duration includes intro+main+outro with overlaps considered
        final_duration = 0.0
        for c in clips:
            final_duration = max(final_duration, c.start + c.duration)
        video = video.with_duration(final_duration)

    # Render
    print("Rendering (MoviePy)...")
    ffmpeg_params = ["-crf", str(args.crf), "-movflags", "+faststart"]
    video.write_videofile(
        args.output,
        fps=args.fps,
        codec="libx264",
        audio_codec="aac" if audio else None,
        preset=args.preset,
        ffmpeg_params=ffmpeg_params,
    )


if __name__ == "__main__":
    main()
