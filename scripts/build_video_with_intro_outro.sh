#!/usr/bin/env bash
set -euo pipefail

# Build a video with intro/outro frames + main PNG slideshow (FFmpeg pipeline)
#
# Usage:
#   scripts/build_video_with_intro_outro.sh BOOK_DIR OUTPUT_MP4
#
# Env overrides (optional):
#   INTRO_HTML=www/podcast-intro-screen.html
#   INTRO_SEC=8
#   OUTRO_HTML=www/podcast-outro-screen.html
#   OUTRO_SEC=10
#   FPS=30
#   WIDTH=1024
#   HEIGHT=1536
#   DPR=2
#   ENCODER=libx264   # or hevc_nvenc / h264_nvenc
#   TENBIT=0          # 1 to enable 10-bit (best with hevc_nvenc)
#   CRF=14            # CQ for NVENC, CRF for libx264
#   BITRATE=20M       # Optional for NVENC
#   FADE=2.5

BOOK_DIR=${1:-}
OUTPUT=${2:-}

if [[ -z "${BOOK_DIR}" || -z "${OUTPUT}" ]]; then
  echo "Usage: scripts/build_video_with_intro_outro.sh BOOK_DIR OUTPUT_MP4" >&2
  exit 1
fi

INTRO_HTML=${INTRO_HTML:-www/podcast-intro-screen.html}
INTRO_SEC=${INTRO_SEC:-8}
OUTRO_HTML=${OUTRO_HTML:-www/podcast-outro-screen.html}
OUTRO_SEC=${OUTRO_SEC:-10}
FPS=${FPS:-30}
WIDTH=${WIDTH:-1024}
HEIGHT=${HEIGHT:-1536}
DPR=${DPR:-2}
ENCODER=${ENCODER:-libx264}
TENBIT=${TENBIT:-0}
CRF=${CRF:-14}
BITRATE=${BITRATE:-}
FADE=${FADE:-2.5}

project_root=$(cd "$(dirname "$0")/.." && pwd)

INTRO_DIR="$BOOK_DIR/intro_frames"
OUTRO_DIR="$BOOK_DIR/outro_frames"
IMAGES_DIR="$BOOK_DIR/images"
AUDIO_DIR="$BOOK_DIR/audio"

if [[ ! -d "$IMAGES_DIR" ]]; then
  echo "Images directory not found: $IMAGES_DIR" >&2
  exit 1
fi

# Pick first audio file (.m4a or .wav)
shopt -s nullglob
audio_candidates=("$AUDIO_DIR"/*.m4a "$AUDIO_DIR"/*.wav)
shopt -u nullglob
if (( ${#audio_candidates[@]} == 0 )); then
  echo "No audio file found in: $AUDIO_DIR (expected .m4a or .wav)" >&2
  exit 1
fi
AUDIO_FILE="${audio_candidates[0]}"

echo "[1/3] Generating intro frames → $INTRO_DIR"
python "$project_root/scripts/html_to_video_simple_hq.py" \
  "$INTRO_HTML" ignored.mp4 "$INTRO_SEC" "$FPS" "$WIDTH" "$HEIGHT" "$DPR" \
  --frames-only --frames-dir="$INTRO_DIR"

echo "[2/3] Generating outro frames → $OUTRO_DIR"
python "$project_root/scripts/html_to_video_simple_hq.py" \
  "$OUTRO_HTML" ignored.mp4 "$OUTRO_SEC" "$FPS" "$WIDTH" "$HEIGHT" "$DPR" \
  --frames-only --frames-dir="$OUTRO_DIR"

echo "[3/3] Composing final video → $OUTPUT"
compose_cmd=(
  python "$project_root/scripts/compose_with_ffmpeg.py" "$IMAGES_DIR" "$OUTPUT" \
    --audio "$AUDIO_FILE" \
    --intro-frames "$INTRO_DIR" --intro-fps "$FPS" \
    --outro-frames "$OUTRO_DIR" --outro-fps "$FPS" \
    --fade "$FADE" --fps "$FPS" --width "$WIDTH" --height "$HEIGHT" \
    --encoder "$ENCODER" --crf "$CRF"
)

if [[ "$TENBIT" == "1" ]]; then
  compose_cmd+=(--tenbit)
fi
if [[ -n "${BITRATE}" ]]; then
  compose_cmd+=(--bitrate "$BITRATE")
fi

"${compose_cmd[@]}"

echo "✅ Done: $OUTPUT"

