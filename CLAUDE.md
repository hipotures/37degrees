# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

37degrees is a TikTok video generator for book reviews targeting Polish youth (10-20 years old). The project creates 8-slide vertical videos (1080x1920) with stylized, non-photorealistic illustrations and text overlays for each classic book.

## Development Environment

- **Package manager**: Use `uv` instead of pip
  - Install dependencies: `uv pip install -r requirements.txt`
  - Add new package: `uv pip add package_name`

## Common Commands

### Main CLI Commands
```bash
# List all collections
python main.py collections

# List books in a collection
python main.py list classics

# List all books in the project
python main.py list

# Generate video for book #17
python main.py video 17

# Generate video by book name
python main.py video little_prince

# Generate videos for entire collection
python main.py video classics

# Generate AI images for book #17
python main.py ai 17

# Generate AI images for entire collection
python main.py ai classics

# Generate everything (prompts + AI + video) for book #17
python main.py generate 17

# Regenerate prompts only (e.g., after editing book.yaml)
python main.py prompts 17
python main.py prompts little_prince
```

### Utility Scripts
```bash
# Migrate old book structure (if needed)
python scripts/migrate_structure.py

# Create documentation structure for books
python scripts/create_docs_structure.py

# Apply text overlays to existing images
python scripts/apply_text_overlays.py

# Test optimized video generation
python scripts/test_optimized_gen.py

# Build prompts for scenes (standalone)
python src/prompt_builder.py books/NNNN_book_name/book.yaml
```

## Architecture

### Core Components

1. **Book Configuration** (`books/NNNN_book_name/book.yaml`)
   - Books are numbered with 4-digit IDs (e.g., 0017_little_prince)
   - Contains book metadata, art style, text overlay settings, and slide definitions
   - Each slide has scene descriptions for AI generation
   - Text overlay configuration supports multiple methods (outline, shadow, box, gradient, glow)
   - Supports emoji rendering with `enable_color_emojis` setting
   - Configurable text timing with fade in/out effects
   - Per-book audio volume override

2. **CLI System** (`src/cli/`)
   - `collections_cmd.py` - Collection management
   - `list_books.py` - Book listing functionality
   - `video.py` - Video generation commands
   - `ai.py` - AI image generation commands
   - `utils.py` - CLI utility functions

3. **Prompt Generation** (`src/prompt_builder.py`)
   - Converts book YAML to AI-ready prompts
   - Outputs structured YAML prompts for scene generation
   - Emphasizes non-photorealistic, childlike illustration style

4. **AI Integration**
   - `src/simple_invokeai_generator.py` - Simple InvokeAI integration (primary generator)
   - `src/comfyui_generator.py` - ComfyUI API integration (manual use)
   - `src/style_preset_loader.py` - InvokeAI style preset management
   - `src/prompt_builder.py` - Standalone prompt generation tool

5. **Video Creation**
   - `src/video_generator.py` - Main video generation logic
   - `src/optimized_video_generator.py` - Parallel frame rendering
   - `src/slide_renderer.py` - Advanced slide rendering with templates
   - `src/text_animator.py` - Text animation effects
   - `src/text_overlay.py` - Basic text rendering
   - `src/text_overlay_emoji.py` - Enhanced text with color emoji support
   - `src/emoji_utils.py` - Emoji to text replacement utilities
   - Uses ffmpeg for final video encoding with NVENC GPU acceleration

6. **Collections System** (`collections/`)
   - YAML files defining book collections
   - `classics.yaml` - Main collection of 37 classic books
   - Supports batch operations on entire collections

### Directory Structure

- `books/NNNN_[book_name]/` - Self-contained book directories with:
  - `book.yaml` - Configuration
  - `generated/` - AI-generated illustrations
  - `prompts/` - AI generation prompts
  - `frames/` - Video frames (gitignored)
  - `docs/` - Book documentation and research
    - `README.md` - Documentation guide
    - `review.md` - Fascinating facts and discoveries
    - `book_page.html` - Interactive HTML presentation
  
- `collections/` - Book collections/series definitions
- `shared_assets/` - Common resources (fonts, templates, backgrounds)
  - `fonts/` - Font files for text rendering
  - `templates/` - HTML page templates
  - `backgrounds/` - Background images
- `src/` - Core application code
- `scripts/` - Utility and test scripts
- `docs/` - Project documentation
- `output/` - Generated videos (gitignored)

### Key Design Decisions

1. **Art Style**: Minimalist children's book illustrations with naive art approach
   - Flat colors, simple shapes, no photorealistic rendering
   - Upper third of image reserved for text overlay
   - SDXL resolution: 832x1248 (to avoid artifacts)
   - Final video resolution: 1080x1920

2. **Text Visibility**: Multiple methods configurable per book
   - Default: outline method with black border
   - Alternatives: shadow, semi-transparent box, gradient, glow
   - Configurable outline width and color
   - Color emoji support with Pilmoji

3. **Text Animation**: Rich animation system
   - Entrance animations: slide_up, slide_down, slide_left, slide_right, fade, zoom, bounce, typewriter
   - Exit animations: fade_out, slide_up, slide_down, zoom_out
   - Configurable timing and fade effects

4. **AI Model Selection**:
   - DreamShaper XL for fantasy/universal use
   - Pony Diffusion XL for younger audience
   - Different models for different genres (see docs/invoke_models_guide.md)

## Important Context

- Target audience: Polish teenagers on TikTok
- Account name: @37stopni (37 degrees - "fever of reading")
- Series focus: World Classics adapted for young readers
- Each video: ~28 seconds, 8 slides, vertical format
- Emphasis on emotional, direct messaging with contemporary references
- Safe zone compliance for TikTok UI elements