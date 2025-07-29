# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

37degrees is a TikTok video generator for book reviews targeting Polish youth (12-25 years old). The project generates 25 scenic AI illustrations per book with stylized, non-photorealistic style for creating engaging TikTok content about classic literature.

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

### 37d Intelligent Agent System
```bash
# Main research workflow using 8 specialized agents
/37d-research "Book Title"

# Export complete agent system for sharing/backup
./scripts/export-37d-system.sh

# Agent specializations (auto-discovered from .claude/agents/):
# - 37d-facts-hunter: Historical facts, biographical details (8-14 tasks)
# - 37d-culture-impact: Cultural adaptations, films, TikTok trends (6-10 tasks)  
# - 37d-symbol-analyst: Literary symbolism analysis (4-8 tasks)
# - 37d-polish-specialist: Polish translations, education context (7-12 tasks)
# - 37d-youth-connector: Gen Z relevance, study hacks (4-8 tasks)
# - 37d-source-validator: Research integrity verification (0-0 tasks)
# - 37d-bibliography-manager: Citation compilation (0-0 tasks)
# - 37d-deep-research: Gap analysis, contradiction resolution (0-5 tasks)
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
   - **Style library**: 34 graphic styles in `config/prompt/graphics-styles/`
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

5. **Collections System** (`collections/`)
   - `classics.yaml` contains 37 books in "Klasyka Światowa" collection
   - Each book has order, path, and thematic tags
   - Series metadata with hashtags, target audience, description
   - Batch operations: `python main.py ai classics`, `python main.py video classics`

6. **Video Generation Pipeline**
   - `OptimizedVideoGenerator` for parallel frame rendering
   - `SlideRenderer` handles Ken Burns effects and transitions
   - `TextAnimator` provides entrance/exit animations
   - Multiple text overlay methods (outline, shadow, box, etc.)
   - FFmpeg with NVENC GPU acceleration

7. **Research Integration** (`src/research/`)
   - Provider pattern for extensibility
   - Perplexity AI and Google Search implementations
   - Automatic Polish review.md generation
   - Response caching to minimize API calls

8. **Static Site Generation** (`src/site_generator/`)
   - Generates interactive HTML for book exploration
   - Timeline visualizations and collection organization
   - Templates in `shared_assets/templates/`

9. **37d Intelligent Agent System** (`.claude/agents/`)
   - **8 specialized research agents** working in coordinated sequence
   - **Dynamic agent discovery** - extensible architecture via file-based configuration
   - **Task quantity control** - configurable min/max tasks per agent type
   - **Multi-stage workflow**: TODO generation → Agent execution → Quality control
   - **Gap analysis system** - deep-research agent fills information gaps
   - **Hook integration** - automatic search result saving via 37d-save-search.py
   - **Export system** - complete agent system backup/sharing capability

### Data Flow
```
book.yaml → Scene Generator → JSON scenes → Style Application → AI Prompts
                                                                     ↓
HTML Site ← Video File ← Frame Rendering ← AI Images ← AI Generator

# 37d Agent Research Flow (Optional):
/37d-research → Agent Discovery → TODO Generation → Sequential Execution
                                                             ↓
book/docs/findings/ ← Quality Control ← Bibliography ← Research Results
```

### Key Design Patterns
- **Registry Pattern**: Dynamic generator discovery
- **Abstract Factory**: Image generator creation
- **Template Method**: Scene generation process
- **Strategy Pattern**: Text overlay methods
- **Provider Pattern**: Research API abstraction

## Important Context

### Core Project Context
- Target audience: Polish teenagers on TikTok
- Account name: @37stopni (37 degrees - "fever of reading")
- Series focus: World Classics adapted for young readers
- Format: 25 scenes per book, vertical 1080x1920, various video lengths
- Emphasis on emotional, direct messaging with contemporary references
- Safe zone compliance for TikTok UI elements
- Art style: Non-photorealistic, childlike illustrations
- Technical specs: 1080x1920 at 30fps, SDXL optimal at 832x1248

### 37d Agent System Context
- **Extensible architecture**: New agents auto-discovered from `.claude/agents/37d-*.md`
- **YAML frontmatter configuration**: `todo_list`, `min_tasks`, `max_tasks`, `execution_order`
- **Agent workflow**: Agents with `todo_list: False` create tasks dynamically
- **Parallel execution**: Agents grouped by `execution_order`, groups run sequentially, agents within groups run in parallel
- **Research output**: All findings saved to `books/NNNN_book/docs/findings/`
- **Quality control**: Source validation and bibliography compilation built-in
- **Hook integration**: Search results automatically saved via Claude Code hooks

### Development Integration
- **Dual architecture**: Core Python CLI + Optional Claude Code agent system
- **No formal test suite**: Use `--generator mock` for testing without GPU
- **Book numbering**: Books follow `NNNN_book_name` pattern (e.g., `0017_little_prince`)
- **Configuration hierarchy**: `settings.yaml` → `.env` → `--set` overrides

## Important Development Guidelines

### Code Creation Principles
- Do what has been asked; nothing more, nothing less
- NEVER create files unless they're absolutely necessary for achieving your goal
- ALWAYS prefer editing an existing file to creating a new one
- NEVER proactively create documentation files (*.md) or README files unless explicitly requested

### Polish Project Specifics
- Always use Polish language for Polish-specific content and research
- Use 24-hour time format for all timestamps  
- Never commit real user data, logins, URLs, or personal information - use examples like userexample001, www.example001.com
- When working with dates/SQL, always consider UTC vs. local time - ask or test if unclear
- Before implementing plans, check for uncommitted changes and ask about committing to GitHub
- For console data presentation (tables, etc.), use the `rich` library
- When adding GitHub integration, use SSH instead of HTTPS (GitHub defaults to `main` branch)
- NEVER run code with the `textual` library as mouse handling breaks terminal in Claude Code