#!/usr/bin/env python3
"""
Compose video from PNGs using MoviePy with the same transition model
as scripts/create_video_with_transitions.py, plus optional intro/outro.

Features
- Main stills slideshow with crossfades spread across audio duration.
- Optional intro/outro as frame sequences (ImageSequenceClip) OR single stills.
- Audio starts AFTER intro and ends BEFORE outro (no overlap).

Usage example
  python scripts/compose_with_moviepy_transitions.py \
    --images-dir books/0006_don_quixote/images \
    --audio books/0006_don_quixote/audio/0006_don_quixote.m4a \
    --intro-frames books/0006_don_quixote/intro_frames --intro-fps 30 \
    --outro-frames books/0006_don_quixote/outro_frames --outro-fps 30 \
    --fade 2.5 --fps 30 --output output/dq_moviepy_final.mp4

Alternative (stills):
  --intro-still path.png --intro-still-duration 3
  --outro-still path.png --outro-still-duration 3
"""

import argparse
import glob
import os
from typing import List, Optional

from moviepy import *
from moviepy.video.fx import FadeIn, FadeOut, CrossFadeIn, CrossFadeOut


def list_pngs_sorted(directory: str) -> List[str]:
    return sorted(glob.glob(os.path.join(directory, "*.png")))


def build_intro_clip(args) -> Optional[VideoClip]:
    if args.intro_frames:
        frames = list_pngs_sorted(args.intro_frames)
        if frames:
            return ImageSequenceClip(frames, fps=args.intro_fps)
    if args.intro_still:
        if os.path.exists(args.intro_still):
            return ImageClip(args.intro_still, duration=args.intro_still_duration)
    return None


def build_outro_clip(args) -> Optional[VideoClip]:
    if args.outro_frames:
        frames = list_pngs_sorted(args.outro_frames)
        if frames:
            return ImageSequenceClip(frames, fps=args.outro_fps)
    if args.outro_still:
        if os.path.exists(args.outro_still):
            return ImageClip(args.outro_still, duration=args.outro_still_duration)
    return None


def main():
    ap = argparse.ArgumentParser(description="Compose PNG slideshow with MoviePy transitions, plus intro/outro")
    ap.add_argument("--images-dir", required=True, help="Directory with main slideshow PNGs")
    ap.add_argument("--output", required=True, help="Output video path")
    ap.add_argument("--audio", required=True, help="Audio file (audio spans ONLY main slideshow)")
    ap.add_argument("--fps", type=int, default=30, help="Output FPS")
    ap.add_argument("--fade", type=float, default=2.5, help="Crossfade duration (seconds)")

    # Intro/outro as frame sequences
    ap.add_argument("--intro-frames", default=None, help="Directory with intro PNG frames (sequence)")
    ap.add_argument("--intro-fps", type=int, default=30)
    ap.add_argument("--outro-frames", default=None, help="Directory with outro PNG frames (sequence)")
    ap.add_argument("--outro-fps", type=int, default=30)

    # Intro/outro as stills
    ap.add_argument("--intro-still", default=None, help="Single PNG as intro")
    ap.add_argument("--intro-still-duration", type=float, default=3.0)
    ap.add_argument("--outro-still", default=None, help="Single PNG as outro")
    ap.add_argument("--outro-still-duration", type=float, default=3.0)

    # Encoding
    ap.add_argument("--crf", type=int, default=14, help="x264 CRF (lower = better)")
    ap.add_argument("--preset", default="slow", help="x264 preset")
    args = ap.parse_args()

    # Load main assets
    main_images = list_pngs_sorted(args.images_dir)
    if not main_images:
        raise SystemExit(f"No PNG images found in {args.images_dir}")

    audio = AudioFileClip(args.audio)
    audio_duration = audio.duration

    # Build intro/outro
    intro = build_intro_clip(args)
    outro = build_outro_clip(args)
    intro_duration = intro.duration if intro else 0.0
    outro_duration = outro.duration if outro else 0.0

    # Allocate MAIN timeline to match audio duration exactly
    n = len(main_images)
    fade = args.fade if n > 1 else 0.0
    clip_duration = (audio_duration + fade * (n - 1)) / n if n > 0 else 0.0
    start_interval = max(0.0, clip_duration - fade)

    # Build main timeline clips (same logic as create_video_with_transitions.py)
    main_clips: List[VideoClip] = []
    for i, img in enumerate(main_images):
        c = ImageClip(img, duration=clip_duration)
        if i == 0:
            if fade > 0:
                c = c.with_effects([FadeIn(fade)])
                if n > 1:
                    c = c.with_effects([CrossFadeOut(fade)])
        elif i == n - 1:
            if fade > 0:
                c = c.with_effects([CrossFadeIn(fade), FadeOut(fade)])
        else:
            if fade > 0:
                c = c.with_effects([CrossFadeIn(fade), CrossFadeOut(fade)])

        # Start: intro_duration minus initial overlap (like your script's i*start_interval)
        start_time = (intro_duration - (fade if fade > 0 else 0.0)) + i * start_interval
        c = c.with_start(start_time)
        main_clips.append(c)

    clips: List[VideoClip] = []
    if intro:
        intro = intro.with_start(0)
        if fade > 0:
            intro = intro.with_effects([CrossFadeOut(fade)])
        clips.append(intro)

    clips.extend(main_clips)

    if outro:
        # Place outro to overlap the end of main by fade seconds
        main_total = (n * clip_duration) - (n - 1) * fade if n > 0 else 0.0
        outro_start = max(0.0, intro_duration + main_total - fade)
        outro = outro.with_start(outro_start)
        if fade > 0:
            outro = outro.with_effects([CrossFadeIn(fade)])
        clips.append(outro)

    # Composite
    size = clips[0].size
    video = CompositeVideoClip(clips, size=size)

    # Align audio to MAIN only: start after intro, end before outro
    video = video.with_audio(audio.with_start(intro_duration))
    final_duration = intro_duration + audio_duration + outro_duration
    video = video.with_duration(final_duration)

    # Encode
    ffmpeg_params = ["-crf", str(args.crf), "-movflags", "+faststart"]
    print("Rendering (MoviePy, transitions like your script)...")
    video.write_videofile(
        args.output,
        fps=args.fps,
        codec="libx264",
        audio_codec="aac",
        preset=args.preset,
        ffmpeg_params=ffmpeg_params,
    )


if __name__ == "__main__":
    main()

