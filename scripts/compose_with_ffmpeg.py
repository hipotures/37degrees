#!/usr/bin/env python3
"""
Compose video from PNGs with optional intro/outro frame sequences (FFmpeg).

Why FFmpeg version?
- Much faster than MoviePy (multi-threaded, no Python frame pipeline).
- Precise crossfades via filter_complex (xfade).

Behavior
- Main slideshow from still PNGs (each as a looped segment) with crossfades.
- Optional intro/outro as frame sequences (read at given FPS) crossfaded in/out.
- Aligns to audio duration if provided; otherwise uses --total-duration.
"""

import argparse
import glob
import os
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional


def list_pngs_sorted(directory: str) -> List[str]:
    return sorted(glob.glob(os.path.join(directory, "*.png")))


def count_sequence_frames(directory: str, pattern: str) -> int:
    # If pattern includes %d, try to glob a broad pattern
    if "%" in pattern:
        # Broad guess: replace %0Nd with *.png
        p = pattern
        p = p.replace("%06d", "*.png").replace("%05d", "*.png").replace("%04d", "*.png").replace("%03d", "*.png").replace("%02d", "*.png").replace("%d", "*.png")
        frames = sorted(glob.glob(os.path.join(directory, p)))
    else:
        frames = sorted(glob.glob(os.path.join(directory, pattern)))
    return len(frames)


def main():
    ap = argparse.ArgumentParser(description="Compose PNG slideshow with optional intro/outro frames (FFmpeg)")
    ap.add_argument("images_dir", help="Directory with main slideshow PNGs (stills)")
    ap.add_argument("output", help="Output video path (e.g., output/ffmpeg_compose.mp4)")
    ap.add_argument("--audio", help="Optional audio file to align total duration", default=None)
    ap.add_argument("--total-duration", type=float, default=None, help="Total duration in seconds if no audio")
    ap.add_argument("--fps", type=int, default=30, help="Output FPS")
    ap.add_argument("--fade", type=float, default=2.5, help="Crossfade duration (seconds)")
    ap.add_argument("--intro-frames", default=None, help="Directory with intro PNG frames sequence")
    ap.add_argument("--intro-fps", type=int, default=30, help="FPS for intro frames")
    ap.add_argument("--intro-pattern", default="frame_%06d.png", help="Pattern for intro frames (printf pattern)")
    ap.add_argument("--outro-frames", default=None, help="Directory with outro PNG frames sequence")
    ap.add_argument("--outro-fps", type=int, default=30, help="FPS for outro frames")
    ap.add_argument("--outro-pattern", default="frame_%06d.png", help="Pattern for outro frames (printf pattern)")
    ap.add_argument("--width", type=int, default=1024)
    ap.add_argument("--height", type=int, default=1536)
    ap.add_argument("--encoder", default="libx264", choices=["libx264", "h264_nvenc", "hevc_nvenc"], help="Video encoder")
    ap.add_argument("--tenbit", action="store_true", help="Use 10-bit where supported (libx264 high10 or HEVC)")
    ap.add_argument("--crf", type=int, default=14, help="CRF for libx264 or CQ for NVENC")
    ap.add_argument("--bitrate", default=None, help="Target bitrate (e.g., 20M) for NVENC")
    args = ap.parse_args()

    main_images = list_pngs_sorted(args.images_dir)
    if not main_images:
        raise SystemExit(f"No PNG images found in {args.images_dir}")

    # Detect durations
    intro_dur = 0.0
    outro_dur = 0.0

    intro_inputs = []
    outro_inputs = []
    input_args: List[str] = []
    norm_labels: List[Tuple[str, float]] = []  # (label, duration)
    pre_filters: List[str] = []

    input_index = 0

    # Intro sequence input
    if args.intro_frames:
        frames_cnt = count_sequence_frames(args.intro_frames, args.intro_pattern)
        if frames_cnt > 0:
            intro_dur = frames_cnt / float(args.intro_fps)
            input_args += [
                "-framerate",
                str(args.intro_fps),
                "-i",
                os.path.join(args.intro_frames, args.intro_pattern),
            ]
            pre_filters.append(f"[{input_index}:v]scale={args.width}:{args.height}:flags=lanczos[v{input_index}]")
            norm_labels.append((f"v{input_index}", intro_dur))
            input_index += 1

    # Main stills as looped inputs with per-image duration
    # We will compute D after we know total/main durations
    # For now collect their indices
    main_indices = []
    for img in main_images:
        input_args += ["-loop", "1", "-t", "1", "-i", img]  # placeholder -t, will fix durations via tpad later
        pre_filters.append(f"[{input_index}:v]scale={args.width}:{args.height}:flags=lanczos[v{input_index}]")
        main_indices.append(input_index)
        input_index += 1

    if args.outro_frames:
        frames_cnt = count_sequence_frames(args.outro_frames, args.outro_pattern)
        if frames_cnt > 0:
            outro_dur = frames_cnt / float(args.outro_fps)
            input_args += [
                "-framerate",
                str(args.outro_fps),
                "-i",
                os.path.join(args.outro_frames, args.outro_pattern),
            ]
            pre_filters.append(f"[{input_index}:v]scale={args.width}:{args.height}:flags=lanczos[v{input_index}]")
            norm_labels.append((f"v{input_index}", outro_dur))
            outro_index = input_index
            input_index += 1
        else:
            outro_index = None
    else:
        outro_index = None

    # Audio input
    audio_index = None
    if args.audio:
        input_args += ["-i", args.audio]
        audio_index = input_index
        input_index += 1

    # Compute durations
    if args.audio:
        # Probe audio duration via ffprobe for accuracy
        try:
            res = subprocess.run([
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", args.audio
            ], capture_output=True, text=True, check=True)
            audio_duration = float(res.stdout.strip())
            total_duration = intro_dur + audio_duration + outro_dur
        except Exception:
            total_duration = None
    else:
        total_duration = args.total_duration

    if total_duration is None:
        # Fallback: 3s per image + crossfades
        total_duration = len(main_images) * 3.0 + intro_dur + outro_dur

    # Main target equals audio length when audio present; otherwise computed from total
    if args.audio and total_duration is not None:
        main_target = max(0.1, total_duration - intro_dur - outro_dur)
    else:
        main_target = max(0.1, total_duration - intro_dur - outro_dur)

    n = len(main_images)
    F = args.fade if n > 1 else 0.0
    D = (main_target + F * (n - 1)) / n if n > 0 else 0.0

    # Fix looped stills duration using tpad to exact D (since -t 1 is placeholder)
    # For each main input, extend to D seconds
    for idx in main_indices:
        pre_filters.append(f"[v{idx}]tpad=stop_duration={D}[vm{idx}]")

    # Build list of normalized labels with durations in order: intro (if any), mains, outro (if any)
    ordered_labels: List[Tuple[str, float]] = []
    # intro
    if norm_labels and norm_labels[0][0].startswith("v0"):
        ordered_labels.append(norm_labels[0])
    # mains
    for idx in main_indices:
        ordered_labels.append((f"vm{idx}", D))
    # outro
    if outro_index is not None:
        ordered_labels.append((f"v{outro_index}", outro_dur))

    # Chain xfade across all ordered segments
    filter_cmds: List[str] = []
    filter_cmds.extend(pre_filters)

    if not ordered_labels:
        raise SystemExit("Nothing to compose")

    current_label, current_dur = ordered_labels[0]
    for i in range(1, len(ordered_labels)):
        next_label, next_dur = ordered_labels[i]
        out_label = f"vx{i}"
        # offset is when to start transition on the first input stream
        offset = max(0.0, current_dur - F)
        filter_cmds.append(f"[{current_label}][{next_label}]xfade=transition=fade:duration={F}:offset={offset}[{out_label}]")
        current_label = out_label
        current_dur = current_dur + next_dur - F

    final_v = current_label

    # Build audio filter if present: delay audio to start after intro
    maps: List[str] = []
    if audio_index is not None:
        adelay_ms = int(intro_dur * 1000)
        # Delay audio so it starts after intro; no padding so it ends before outro
        filter_cmds.append(f"[{audio_index}:a]adelay={adelay_ms}|{adelay_ms}[aud]")
        maps = ["-map", f"[{final_v}]", "-map", "[aud]"]
    else:
        maps = ["-map", f"[{final_v}]"]

    # Build full ffmpeg command (after finalizing filter graph)
    filter_graph = ";".join(filter_cmds)
    cmd: List[str] = ["ffmpeg", "-y"] + input_args + ["-filter_complex", filter_graph] + maps

    # Encoder settings
    if args.encoder in ("h264_nvenc", "hevc_nvenc"):
        pix_fmt = "p010le" if args.tenbit and args.encoder == "hevc_nvenc" else "yuv420p"
        if args.tenbit and args.encoder == "h264_nvenc":
            # Switch to HEVC for reliable 10-bit
            args.encoder = "hevc_nvenc"
            pix_fmt = "p010le"
        cq = str(args.crf)
        target_bitrate = args.bitrate if args.bitrate else ("20M" if args.encoder == "hevc_nvenc" else "25M")
        # derive buffer sizes
        try:
            tb = float(target_bitrate.rstrip('M'))
            maxrate_val = f"{int(tb*2)}M"
            bufsize_val = f"{int(tb*4)}M"
        except Exception:
            maxrate_val = target_bitrate
            bufsize_val = target_bitrate

        cmd += [
            "-r", str(args.fps),
            "-c:v", args.encoder,
            "-preset", "p5",
            "-rc", "vbr",
            "-cq", cq,
            "-b:v", target_bitrate,
            "-maxrate", maxrate_val,
            "-bufsize", bufsize_val,
            "-pix_fmt", pix_fmt,
            "-movflags", "+faststart",
            args.output,
        ]
    else:
        # libx264
        if args.tenbit:
            cmd += [
                "-r", str(args.fps),
                "-c:v", "libx264",
                "-preset", "slow",
                "-crf", str(args.crf if args.crf is not None else 18),
                "-profile:v", "high10",
                "-pix_fmt", "yuv420p10le",
                "-movflags", "+faststart",
                args.output,
            ]
        else:
            cmd += [
                "-r", str(args.fps),
                "-c:v", "libx264",
                "-preset", "slow",
                "-crf", str(args.crf if args.crf is not None else 14),
                "-profile:v", "high",
                "-level:v", "4.2",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                args.output,
            ]

    print("Running FFmpeg compose...\n", " ".join(cmd))
    res = subprocess.run(cmd)
    if res.returncode != 0:
        raise SystemExit(res.returncode)


if __name__ == "__main__":
    main()
