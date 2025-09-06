# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
37degrees (@37stopni - "gorączka czytania") is a TikTok video generator for Polish youth promoting classic literature through AI-generated visual content. The system creates 25 scenic illustrations per book and generates vertical videos (1080x1920) optimized for TikTok.

## Core Commands

### Development Environment
- **Python**: 3.12+ required, uses `uv` package manager
- **Setup**: `uv pip install -r requirements.txt`
- **Config**: Uses `config/settings.yaml` with environment variable overrides via `.env`
- **Testing**: No formal test framework - use mock generators for testing (`--generator mock`, `--provider mock`)
- **No linting/formatting**: Project doesn't use formal linting tools - follow existing code style

### Main CLI Commands
Używaj dokumentacji docs/TODOIT_CLI_GUIDE.md docs/TODOIT_MCP_TOOLS.md docs/TODOIT_API.md dla TODOIT
 

```bash
# Book Management
python main.py collections                      # List all collections
python main.py list classics                    # List books in collection
python main.py list                            # List all books

# Content Generation  
python main.py ai 17 --generator invokeai      # Generate AI images
python main.py video 17                        # Generate video from images
python main.py generate 17                     # Generate AI + video
python main.py research 17 --provider perplexity # Generate research content
python main.py site 17                         # Generate static site

# Batch Operations
python main.py ai classics                     # Process entire collection
python main.py generate classics              # Generate all content for collection
```

### Advanced Commands
```bash
# Configuration overrides
python main.py --set video.fps=60 video 17
python main.py --config production.yaml video 17

# 37d Agent System (Research)
/37d-research "Book Title"                     # Run 8 specialized research agents
./scripts/export-37d-system.sh               # Export complete agent system

# Automation Scripts
./scripts/todoit-dwn-img.sh                   # Batch image download via TODOIT
./scripts/run_research_batch.sh               # Batch research processing
./scripts/prepare-book-folders.sh             # Initialize book directory structure
```

## Architecture Overview

### Project Structure
```
37degrees/
├── main.py                    # CLI entry point
├── src/                      # Core source code
│   ├── cli/                 # Command modules (ai, video, research, etc.)
│   ├── generators/          # AI image generators (InvokeAI, ComfyUI, Mock)
│   ├── research/           # Research providers (Perplexity, Google, Mock)
│   └── site_generator/     # Static site generation
├── books/NNNN_name/        # Book directories with configs and generated content
│   ├── book.yaml          # Book configuration
│   ├── generated/         # 25 AI-generated scene images
│   ├── prompts/           # AI prompts for scenes
│   └── docs/              # Research findings and reviews
├── collections/           # Book groupings (classics.yaml)
├── config/               # Global settings and prompt templates
├── output/               # Generated videos
└── site/                 # Generated static website
```

### Key Components

#### 1. Plugin Architecture (`src/generators/`)
- **BaseImageGenerator**: Abstract interface for AI generators
- **Registry Pattern**: Dynamic generator discovery
- **Implementations**: InvokeAI (primary), ComfyUI, Mock (testing)

#### 2. Research System (`src/research/`)
- **Provider Pattern**: Extensible API integration
- **Implementations**: Perplexity AI, Google Search, Mock
- **37d Agent System**: 8 specialized research agents with auto-discovery

#### 3. Video Pipeline
- **OptimizedVideoGenerator**: GPU-accelerated rendering with NVENC
- **SlideRenderer**: Ken Burns effects and smooth transitions
- **TextAnimator**: Multi-method text overlay with emoji support

#### 4. Content Generation Flow
```
book.yaml → Scene Generation → AI Prompts → Image Generation → Video Rendering
                                                          ↓
Static Site ← Research Content ← 37d Agents ← Bibliography ← Source Validation
```

## 37d Research Agent System

### Agent Discovery and Execution
- **Auto-discovery**: Agents found in `.claude/agents/37d-*.md`
- **YAML frontmatter**: `min_tasks`, `max_tasks`, `execution_order`
- **Parallel execution**: Agents grouped by `execution_order`, executed in parallel within groups
- **Output**: Research findings saved to `books/NNNN_book/docs/findings/`

### MCP Tools Integration
- **TODOIT MCP**: Task management with properties, list and item operations
- **Playwright MCP**: Browser automation for ChatGPT image downloads
- **37d Commands**: Specialized workflow agents in `.claude/commands/37d-*.md`

### Available Agents (8 core)
- **37d-facts-hunter**: Historical facts, biographical details (8-14 tasks)
- **37d-culture-impact**: Cultural adaptations, TikTok trends (6-10 tasks)
- **37d-symbol-analyst**: Literary symbolism analysis (4-8 tasks)
- **37d-polish-specialist**: Polish translations, educational context (7-12 tasks)
- **37d-youth-connector**: Gen Z relevance, learning hacks (4-8 tasks)
- **37d-source-validator**: Research integrity verification (0-0 tasks)
- **37d-bibliography-manager**: Citation compilation (0-0 tasks)
- **37d-deep-research**: Gap analysis, contradiction resolution (0-5 tasks)

## Configuration

### Key Settings (`config/settings.yaml`)
- **Video**: 1080x1920 @ 30fps, GPU encoding with NVENC
- **Generators**: InvokeAI default, ComfyUI/Mock alternatives
- **Research**: Perplexity API primary, Google Search backup
- **Text**: Outline method with color emoji support

### Environment Variables (`.env`)
```
PERPLEXITY_API_KEY=your_key
GOOGLE_API_KEY=your_key
GOOGLE_CX=your_cx
DEFAULT_GENERATOR=invokeai
VIDEO_FPS=30
DEBUG=false
```

## Testing and Development

### Mock Testing
```bash
python main.py ai 17 --generator mock         # Test without AI generation
python main.py research 17 --provider mock    # Test research without API calls
python main.py --set development.debug=true video 17  # Debug mode
```

### Book Structure
Each book requires:
- `book.yaml`: Title, author, year, description, themes
- Prompt templates for 25 scenes
- Generated images in `generated/` directory
- Research documentation in `docs/`

### Collections System
- `collections/classics.yaml`: 37 world literature classics
- Thematic grouping with tags and metadata
- Batch processing support for entire collections

## Development Guidelines

### Code Patterns
- **Registry Pattern**: Dynamic component discovery
- **Provider Pattern**: Pluggable service implementations  
- **Template Method**: Standardized generation workflows
- **Strategy Pattern**: Multiple text overlay methods

### Polish Project Specifics
- Content primarily in Polish for Polish youth audience
- 24-hour time format for timestamps
- SSH preferred over HTTPS for GitHub
- No real credentials in commits (use examples)
- Consider UTC vs local time for date operations

### Performance Considerations
- GPU acceleration available via NVENC FFmpeg
- Parallel processing for batch operations
- Caching for API responses (15min TTL)
- Concurrent file operations where possible

## Common Workflows

### Adding New Book
1. Create `books/NNNN_bookname/` directory
2. Configure `book.yaml` with metadata
3. Generate prompts: `python main.py prompts NNNN`
4. Generate content: `python main.py generate NNNN`

### Adding to Collection
1. Edit `collections/classics.yaml`
2. Add book path and metadata
3. Process: `python main.py generate classics`

### Custom Generator
1. Inherit from `BaseImageGenerator` in `src/generators/`
2. Implement required methods
3. Auto-discovered by registry system

### Automation Workflows
1. **Image Download**: Use `scripts/todoit-dwn-img.sh` to batch download ChatGPT images
2. **Research Batch**: Use `scripts/run_research_batch.sh` for multiple book research
3. **Structure Setup**: Use `scripts/prepare-book-folders.sh` to create book directories

## Key Files and Directories

### Essential Scripts (`scripts/`)
- **todoit-dwn-img.sh**: TODOIT-based batch image downloading
- **export-37d-system.sh**: Export complete agent system for backup
- **prepare-book-folders.sh**: Book directory structure initialization
- **run_research_batch.sh**: Batch research processing automation

### Configuration Locations
- **`.claude/agents/`**: Agent definitions for 37d research system
- **`.claude/commands/`**: Workflow command definitions (37d-c*.md)
- **`config/settings.yaml`**: Main application configuration
- **`collections/classics.yaml`**: Book collection definitions

### Generated Content Structure
- **`books/NNNN_name/generated/`**: 25 scene images per book
- **`books/NNNN_name/docs/`**: Research findings and documentation
- **`output/`**: Generated video files
- **`site/`**: Static website generated from book content

The system emphasizes modularity, Polish localization, and TikTok optimization for engaging educational content about world literature.
