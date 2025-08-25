#!/bin/bash
ffmpeg -y -i books/0006_don_quixote/audio/0006_don_quixote.m4a -t 10 -c copy test_audio_10s.m4a