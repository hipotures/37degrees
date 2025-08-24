#!/bin/bash

# Generate intro frames if they don't exist
if [ ! -d "books/0006_don_quixote/intro_frames" ] || [ -z "$(ls -A books/0006_don_quixote/intro_frames 2>/dev/null)" ]; then
    echo "Generating intro frames..."
    python scripts/html_to_video_30fps.py books/0006_don_quixote/assets/podcast-intro-screen.html test_intro.mp4 3 30 1080 1920 1 --frames-only --frames-dir=books/0006_don_quixote/intro_frames
fi

# Generate outro frames if they don't exist  
if [ ! -d "books/0006_don_quixote/outro_frames" ] || [ -z "$(ls -A books/0006_don_quixote/outro_frames 2>/dev/null)" ]; then
    echo "Generating outro frames..."
    python scripts/html_to_video_30fps.py www/podcast-outro-screen.html test_outro.mp4 3 30 1080 1920 1 --frames-only --frames-dir=books/0006_don_quixote/outro_frames
fi

# Generate 10s test audio if it doesn't exist
if [ ! -f "test_audio_10s.m4a" ]; then
    echo "Generating 10s test audio..."
    ffmpeg -y -i books/0006_don_quixote/audio/0006_don_quixote.m4a -t 10 -c copy test_audio_10s.m4a
fi

# Generate video with intro, outro, and scenes
echo "Generating final video..."
python scripts/compose_with_moviepy_transitions.py --images-dir test_2_scenes --audio test_audio_10s.m4a --intro-frames books/0006_don_quixote/intro_frames --intro-fps 30 --outro-frames books/0006_don_quixote/outro_frames --outro-fps 30 --fade 2.5 --fps 30 --output output/test_fixed_pauses.mp4