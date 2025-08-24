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
        print(f"DEBUG: INTRO using {args.intro_frames}, found {len(frames)} frames")
        if frames:
            return ImageSequenceClip(frames, fps=args.intro_fps)
    if args.intro_still:
        if os.path.exists(args.intro_still):
            return ImageClip(args.intro_still, duration=args.intro_still_duration)
    return None


def build_outro_clip(args) -> Optional[VideoClip]:
    if args.outro_frames:
        frames = list_pngs_sorted(args.outro_frames)
        print(f"DEBUG: OUTRO using {args.outro_frames}, found {len(frames)} frames")
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

        # Start after intro + 5s pause, no overlap
        pause_after_intro = 5.0  # 5 second pause after intro
        start_time = intro_duration + pause_after_intro + i * start_interval
        c = c.with_start(start_time)
        
        # Position scenes: center horizontally + 50px down (for phone UI)
        # Scene size: 1024x1536, Target: 1080x1920
        x_offset = (1080 - 1024) // 2  # 28px from left (center horizontally)
        y_offset = 50  # 50px from top (avoid phone status bar)
        c = c.with_position((x_offset, y_offset))
        
        main_clips.append(c)

    clips: List[VideoClip] = []
    if intro:
        intro = intro.with_start(0)
        print(f"DEBUG: Adding intro at t={intro.start}")
        # Remove crossfade for intro - it should play completely separate
        clips.append(intro)
        
        # Add 5s pause after intro (freeze LAST frame)
        pause_after_intro = 5.0
        intro_last_frame = intro.to_ImageClip(t=intro_duration-0.1, duration=pause_after_intro)
        intro_last_frame = intro_last_frame.with_start(intro_duration)
        clips.append(intro_last_frame)

    clips.extend(main_clips)

    # No freeze frame - outro starts right after main content
    # (freeze code removed as fade makes last frame black)

    if outro:
        # Place outro after main content + 2s freeze, no overlap
        pause_after_intro = 5.0
        pause_after_main = 0.0  # No pause - outro starts right after main content
        main_total = (n * clip_duration) - (n - 1) * fade if n > 0 else 0.0
        outro_start = intro_duration + pause_after_intro + main_total + pause_after_main
        
        print(f"DEBUG: intro_duration={intro_duration:.2f}, pause_after_intro={pause_after_intro}, main_total={main_total:.2f}, pause_after_main={pause_after_main}")
        print(f"DEBUG: outro_start={outro_start:.2f}")
        
        outro = outro.with_start(outro_start)
        print(f"DEBUG: Adding outro at t={outro.start}")
        # Remove crossfade for outro - it should play completely separate
        clips.append(outro)
        
        # Add 5s pause after outro (freeze LAST frame)
        pause_after_outro = 5.0
        outro_last_frame = outro.to_ImageClip(t=outro_duration-0.1, duration=pause_after_outro)
        outro_last_frame = outro_last_frame.with_start(outro_start + outro_duration)
        clips.append(outro_last_frame)

    # Composite - force 1080x1920 size (TikTok format)
    size = (1080, 1920)
    video = CompositeVideoClip(clips, size=size, bg_color=(0, 0, 0))

    # Fix MoviePy precision error - extend audio with silence instead of cutting
    from moviepy import AudioClip, concatenate_audioclips
    # Add 1 second of silence to avoid precision issues
    silence = AudioClip(lambda t: [0, 0], duration=1.0)  # stereo silence
    extended_audio = concatenate_audioclips([audio, silence])
    
    # Audio starts after intro + pause (use same variables as clip positioning)
    pause_after_intro = 5.0  
    pause_after_main = 0.0   # No pause - outro starts right after main content 
    pause_after_outro = 5.0  # 5s pause after outro
    
    # Audio starts when main scenes start (after intro + pause)
    from moviepy import CompositeAudioClip
    audio_start_time = intro_duration + pause_after_intro
    # Create composite with delayed audio
    delayed_audio = CompositeAudioClip([extended_audio.with_start(audio_start_time)])
    video = video.with_audio(delayed_audio)
    final_duration = intro_duration + pause_after_intro + audio_duration + pause_after_main + outro_duration + pause_after_outro
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

