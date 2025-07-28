# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

37degrees is a TikTok video generator for book reviews targeting Polish youth (12-25 years old). The project creates 8-slide vertical videos (1080x1920) with stylized, non-photorealistic illustrations and text overlays for each classic book.

## Development Environment

- **Package manager**: Use `uv` instead of pip
  - Install dependencies: `uv pip install -r requirements.txt`
  - Add new package: `uv pip install package_name`
  - Activate virtual environment: `source .venv/bin/activate` (if needed)
- **Python version**: 3.12+ required
- **Configuration**: Project uses centralized config in `config/settings.yaml`
  - Copy `.env.example` to `.env` for local settings
  - Override settings with `--set key=value`
  - Use custom config with `--config file.yaml`

## Common Commands

### Testing and Development
```bash
# No formal test suite - test with mock generator
python main.py ai 17 --generator mock

# Test video generation without AI
python main.py video 17  # Requires existing images in generated/

# Test research generation
python main.py research 17 --provider mock

# Debug mode
python main.py --set development.debug=true ai 17
```

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

# Generate AI images with specific generator
python main.py ai 17 --generator mock  # For testing
python main.py ai 17 --generator comfyui  # Alternative generator

# Generate AI images for entire collection
python main.py ai classics

# Generate everything (prompts + AI + video) for book #17
python main.py generate 17

# Regenerate prompts only (e.g., after editing book.yaml)
python main.py prompts 17
python main.py prompts little_prince

# Generate AI-powered research content
python main.py research 17 --provider perplexity  # Perplexity AI
python main.py research 17 --provider google      # Google Search
python main.py research classics --provider mock  # Testing

# Generate static HTML site
python main.py site              # Complete site
python main.py site 17           # Single book page
python main.py site classics     # Collection pages

# Configuration overrides
python main.py --set video.fps=60 video 17
python main.py --set development.debug=true --no-banner ai 17

# Use custom configuration file
python main.py --config production.yaml video 17
```

### Advanced Scene Generation (37degrees Commands)
```bash
# Generate new scene descriptions using custom commands
/37d-gen-scenes-step1 "Book Title" "Author" [generator_type]

# Examples:
/37d-gen-scenes-step1 "Little Prince" "Saint-Exupéry" narrative
/37d-gen-scenes-step1 "Treasure Island" "Stevenson" flexible
/37d-gen-scenes-step1 "Wuthering Heights" "Emily Brontë" emotional
/37d-gen-scenes-step1 "1984" "Orwell"  # defaults to 'podcast'

# Apply visual styles to scenes
/37d-apply-style-step2 "Book Title" "Author" [style_name]
```

### Utility Scripts
```bash
# Build prompts for scenes (standalone)
python src/prompt_builder.py books/NNNN_book_name/book.yaml
```

## High-Level Architecture

### Core Pipeline Flow
1. **Book Configuration** → 2. **Scene Generation** → 3. **AI Image Generation** → 4. **Video Composition**

### Key Architectural Components

1. **Plugin Architecture** (`src/generators/`)
   - `BaseImageGenerator` abstract class defines interface
   - Registry pattern for dynamic generator discovery
   - Generators: InvokeAI (primary), ComfyUI, Mock (testing)
   - New generators can be added by inheriting from base class

2. **Scene Generation System** (v2.0+)
   - **Two-step process**: Scene descriptions → Style application
   - **Generator types**: narrative, flexible, podcast, atmospheric, emotional
   - **Scene files**: `books/*/prompts/scenes/[type]/scene_XX.json`
   - **Style library**: 37 graphic styles in `config/prompt/graphics-styles/`
   - **Templates**: Scene generators in `config/prompt/scene-generator/`

3. **Configuration System** (`src/config.py`)
   - Centralized settings loaded from `config/settings.yaml`
   - Environment variables override via `.env`
   - Runtime overrides with `--set` flag
   - Path resolution and variable substitution

4. **CLI Command Architecture** (`src/cli/`)
   - Each major feature has dedicated module
   - Commands use click framework with shared context
   - Batch operations support via collection system

5. **Video Generation Pipeline**
   - `OptimizedVideoGenerator` for parallel frame rendering
   - `SlideRenderer` handles Ken Burns effects and transitions
   - `TextAnimator` provides entrance/exit animations
   - Multiple text overlay methods (outline, shadow, box, etc.)
   - FFmpeg with NVENC GPU acceleration

6. **Research Integration** (`src/research/`)
   - Provider pattern for extensibility
   - Perplexity AI and Google Search implementations
   - Automatic Polish review.md generation
   - Response caching to minimize API calls

7. **Static Site Generation** (`src/site_generator/`)
   - Generates interactive HTML for book exploration
   - Timeline visualizations and collection organization
   - Templates in `shared_assets/templates/`

### Data Flow
```
book.yaml → Scene Generator → JSON scenes → Style Application → AI Prompts
                                                                     ↓
HTML Site ← Video File ← Frame Rendering ← AI Images ← AI Generator
```

### Key Design Patterns
- **Registry Pattern**: Dynamic generator discovery
- **Abstract Factory**: Image generator creation
- **Template Method**: Scene generation process
- **Strategy Pattern**: Text overlay methods
- **Provider Pattern**: Research API abstraction

## Important Context

- Target audience: Polish teenagers on TikTok
- Account name: @37stopni (37 degrees - "fever of reading")
- Series focus: World Classics adapted for young readers
- Each video: ~28 seconds, 8 slides, vertical format
- Emphasis on emotional, direct messaging with contemporary references
- Safe zone compliance for TikTok UI elements
- Art style: Non-photorealistic, childlike illustrations
- SDXL optimal resolution: 832x1248 (avoid artifacts)
- Final video: 1080x1920 at 30fps