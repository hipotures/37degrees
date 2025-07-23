# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

37degrees is a TikTok video generator for book reviews targeting Polish youth (10-20 years old). The project creates 8-slide vertical videos (1080x1920) with stylized, non-photorealistic illustrations and text overlays for each classic book.

## Development Environment

- **Package manager**: Use `uv` instead of pip
  - Install dependencies: `uv pip install -r requirements.txt`
  - Add new package: `uv pip add package_name`

## Common Commands

### Running the Application
```bash
# Generate video for a specific book
python main.py books/little_prince/book.yaml

# Generate scenes with local AI (ComfyUI/InvokeAI)
python src/comfyui_generator.py

# Build prompts for AI generation
python src/prompt_builder.py

# Create video from generated scenes
cd books/little_prince && python create_video.py
```

### Testing and Development
```bash
# Test text overlay methods
python src/text_overlay.py

# Migrate old book structure (if needed)
python migrate_structure.py
```

## Architecture

### Core Components

1. **Book Configuration** (`books/*/book.yaml`)
   - Contains book metadata, art style, text overlay settings, and slide definitions
   - Each slide has scene descriptions for AI generation
   - Text overlay configuration supports multiple methods (outline, shadow, box, gradient, glow)

2. **Prompt Generation** (`src/prompt_builder.py`)
   - Converts book YAML to AI-ready prompts
   - Outputs structured YAML prompts for scene generation
   - Emphasizes non-photorealistic, childlike illustration style

3. **AI Integration**
   - `src/comfyui_generator.py` - ComfyUI API integration
   - `invoke_models_guide.md` - InvokeAI model recommendations
   - Supports both local generation tools

4. **Video Creation**
   - `src/video_generator.py` - Main video generation logic
   - `src/text_overlay.py` - Text rendering with multiple visibility methods
   - Uses ffmpeg for final video encoding

### Directory Structure

- `books/[book_name]/` - Self-contained book directories with:
  - `book.yaml` - Configuration
  - `scenes/` or `scenes_v2/` - Generated illustrations
  - `prompts/` - AI generation prompts
  - `frames/` - Video frames (gitignored)
  
- `shared_assets/` - Common resources (fonts, templates, backgrounds)
- `src/` - Core application code

### Key Design Decisions

1. **Art Style**: Minimalist children's book illustrations with naive art approach
   - Flat colors, simple shapes, no photorealistic rendering
   - Upper third of image reserved for text overlay

2. **Text Visibility**: Multiple methods configurable per book
   - Default: outline method with black border
   - Alternatives: shadow, semi-transparent box, gradient, glow

3. **AI Model Selection**:
   - DreamShaper XL for fantasy/universal use
   - Pony Diffusion XL for younger audience
   - Different models for different genres (see invoke_models_guide.md)

## Important Context

- Target audience: Polish teenagers on TikTok
- Account name: @37stopni (37 degrees - "fever of reading")
- Series focus: World Classics adapted for young readers
- Each video: ~28 seconds, 8 slides, vertical format
- Emphasis on emotional, direct messaging with contemporary references