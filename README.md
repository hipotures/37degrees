# 37degrees - TikTok Video Generator for Book Reviews

Automated video generator for creating engaging TikTok book reviews targeting Polish youth (12-25 years old). Creates 8-slide vertical videos with AI-generated illustrations and text overlays for classic literature.

**Version 2.1.0** - Now with 37d intelligent agent system, plugin architecture, AI research integration, static site generation, and extensible systems!

## 📖 Overview

37degrees generates short-form video content for the @37stopni TikTok account, featuring:
- **8 slides per book** with specific hooks, quotes, and CTAs
- **AI-generated illustrations** in a childlike, non-photorealistic style
- **Text overlays** with multiple visibility methods
- **Automated video creation** with Ken Burns effects and transitions
- **37d intelligent agent system** for comprehensive book research
- **AI-powered research** for generating fascinating book facts
- **Static HTML site** with interactive book exploration
- **Plugin architecture** for extensible image generators

## 🚀 Quick Start

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
python main.py ai 17 --generator mock
python main.py ai 17 --generator comfyui

# Generate AI images for entire collection
python main.py ai classics

# Generate everything (prompts + AI + video) for book #17
python main.py generate 17

# Regenerate prompts only (e.g., after editing book.yaml)
python main.py prompts 17
python main.py prompts little_prince

# Generate AI-powered research content
python main.py research 17 --provider perplexity
python main.py research classics --provider mock

# Run 37d intelligent agent research (requires Claude Code)
# See .claude/agents/ for agent system documentation
/37d-research "Book Title"

# Generate static HTML site
python main.py site              # Complete site
python main.py site 17           # Single book page
python main.py site classics     # Collection pages
```

## 📁 Project Structure

```
37degrees/
├── main.py              # Main entry point with intuitive CLI
├── config/              # Configuration files
│   ├── settings.yaml    # Main configuration
│   └── generators.yaml  # Image generator settings
├── src/                 # Core application code
│   ├── cli/            # CLI modules (collections, list, video, ai, research, site)
│   ├── generators/     # Plugin-based image generators
│   │   ├── base.py     # Abstract base class
│   │   ├── registry.py # Generator registry system
│   │   ├── invokeai.py # InvokeAI implementation
│   │   ├── comfyui.py  # ComfyUI implementation
│   │   └── mock.py     # Mock generator for testing
│   ├── research/       # AI-powered research providers
│   │   ├── base.py     # Abstract research provider
│   │   ├── perplexity_api.py # Perplexity AI integration
│   │   ├── google_search.py  # Google Search integration
│   │   └── review_generator.py # Generate review.md files
│   ├── site_generator/ # Static HTML site generation
│   │   ├── book_page.py      # Individual book pages
│   │   ├── index_page.py     # Main index with collections
│   │   └── site_builder.py   # Site generation orchestrator
│   ├── config.py       # Configuration management
│   ├── video_generator.py         # Video creation with effects
│   ├── prompt_builder.py          # Convert scenes to AI prompts
│   └── text_overlay.py            # Text rendering methods
├── books/               # Book configurations and assets
│   └── NNNN_[book_name]/ # Books numbered by ID (e.g., 0017_little_prince)
│       ├── book.yaml    # Book configuration
│       ├── docs/        # Book documentation and research
│       │   ├── review.md         # Fascinating facts and discoveries
│       │   ├── book_page.html    # Interactive HTML presentation
│       │   └── README.md         # Documentation guide
│       ├── generated/   # AI-generated images
│       └── prompts/     # Generated AI prompts
├── collections/         # Book collections/series
│   └── classics.yaml    # Main collection of 37 classic books
├── scripts/            # Helper and test scripts
│   ├── create_docs_structure.py  # Auto-create docs directories
│   └── ...
├── shared_assets/      # Fonts, backgrounds, templates
│   └── templates/      # HTML page templates
├── .claude/           # Claude Code integration
│   ├── agents/        # 37d intelligent research agents
│   │   ├── 37d-facts-hunter.md     # Historical facts and trivia
│   │   ├── 37d-culture-impact.md   # Cultural adaptations tracking
│   │   ├── 37d-symbol-analyst.md   # Literary symbolism analysis
│   │   ├── 37d-polish-specialist.md # Polish reception research
│   │   ├── 37d-youth-connector.md  # Gen Z relevance bridge
│   │   ├── 37d-source-validator.md # Research integrity guardian
│   │   ├── 37d-bibliography-manager.md # Citations compiler
│   │   └── 37d-deep-research.md    # Gap analysis specialist
│   ├── commands/      # Slash commands for Claude Code
│   │   └── 37d-research.md         # Main research workflow
│   └── hooks/         # Search result automation
│       ├── 37d-save-search.py      # Auto-save search results
│       └── 37d-save-search.sh      # Shell hook wrapper
└── docs/              # Project documentation
```

## ⚡ Features

### 37d Intelligent Agent System
- **8 Specialized Research Agents** working in coordinated sequence
- **Dynamic Agent Discovery** - Extensible architecture for adding new agents
- **Task Quantity Control** - Configurable min/max tasks per agent type
- **Conditional Workflow** - Agents adapt based on configuration and book context
- **Gap Analysis** - Advanced deep-research agent fills information gaps
- **Quality Control** - Source validation and bibliography management
- **Claude Code Integration** - Uses Claude Code subagents with slash commands
- **Export System** - `scripts/export-37d-system.sh` for easy sharing

#### Agent Specializations:
- **37d-facts-hunter** (8-14 tasks): Historical facts, biographical details, trivia
- **37d-culture-impact** (6-10 tasks): Films, adaptations, TikTok trends, memes
- **37d-symbol-analyst** (4-8 tasks): Literary symbolism, cross-cultural interpretations
- **37d-polish-specialist** (7-12 tasks): Polish translations, education, cultural reception
- **37d-youth-connector** (4-8 tasks): Gen Z relevance, study hacks, modern connections
- **37d-source-validator** (0-0 tasks): Research integrity, fact verification
- **37d-bibliography-manager** (0-0 tasks): Citation compilation, academic formatting
- **37d-deep-research** (0-5 tasks): Gap analysis, contradiction resolution

### AI Image Generation
- **Plugin Architecture**: Easily add new image generators
- **Built-in Generators**:
  - InvokeAI (primary) - Local SDXL models
  - ComfyUI - Workflow-based generation
  - Mock - Testing without GPU
- Optimized resolution (832x1248) to avoid artifacts
- Style presets: Illustration, Sketch, etc.
- Automatic retry with exponential backoff
- Automatic upscaling to 1080x1920 for video

### Text Overlay Methods
- **Outline**: Black border around white text (default)
- **Shadow**: Drop shadow effect
- **Box**: Semi-transparent background
- **Gradient**: Darkening gradient at top
- **Glow**: Soft glow effect

### Video Creation
- Ken Burns effect (subtle zoom)
- Smooth transitions between slides
- TikTok Safe Zone compliance
- GPU-accelerated encoding (NVENC)
- Rich progress bars and status updates

### Configuration System
- Centralized configuration in `config/settings.yaml`
- Environment variable support with `.env` files
- CLI overrides: `--set video.fps=60`
- Custom config files: `--config my_settings.yaml`

### Interactive HTML Pages
- Professional book presentations with Charts.js visualizations
- Interactive timelines and character explorers
- Responsive design with Tailwind CSS
- Template-based generation for consistency

## 📝 Book Configuration

Each book has a `book.yaml` file defining:

```yaml
book_info:
  title: "Mały Książę"
  author: "Antoine de Saint-Exupéry"

technical_specs:
  resolution: "832x1248"      # AI generation resolution
  output_resolution: "1080x1920"  # Final video resolution

template_art_style: "Illustration"  # Or "Sketch", "" for custom

slides:
  - type: "hook"
    text: "Czy wiesz, że najważniejsze jest niewidoczne dla oczu?"
    scene:
      elements:
        - "large human eye floating in space"
        - "multiple small stars"
      composition: "eye in center, stars scattered around"
```

## 🔧 Requirements

### Core System
- Python 3.8+
- One of the following image generators:
  - InvokeAI running on http://localhost:9090 (recommended)
  - ComfyUI running on http://localhost:8188
  - No generator needed for mock/testing mode
- NVIDIA GPU with NVENC support (optional, for video encoding)
- FFmpeg with NVENC (for GPU encoding)

### 37d Agent System (Optional)
- **Claude Code** - Install from https://claude.ai/code
- Agents automatically discovered from `.claude/agents/37d-*.md`
- Research workflow activated via `/37d-research "Book Title"` slash command
- Hooks configuration for automatic search result saving

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/yourusername/37degrees.git
cd 37degrees

# Install dependencies with uv
uv pip install -r requirements.txt

# Or with pip
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your settings (optional)

# Optional: Set up 37d Agent System
# 1. Install Claude Code from https://claude.ai/code
# 2. Agents are already in .claude/agents/ directory
# 3. Use /37d-research "Book Title" in Claude Code
# 4. Export agent system: ./scripts/export-37d-system.sh
```

## 🎬 Workflow

### Single Book
1. **Find book ID**: `python main.py list`
2. **Generate AI images**: `python main.py ai 17`
3. **Create video**: `python main.py video 17`
4. **Upload to TikTok** with hashtags: #37stopni #klasyka #booktok

### Entire Collection
1. **View collections**: `python main.py collections`
2. **Review books**: `python main.py list classics`
3. **Generate AI images**: `python main.py ai classics`
4. **Create videos**: `python main.py video classics`
5. **Find videos in**: `output/` (named as `book_NNNN_YYYYMMDD_HHMMSS.mp4`)

### 37d Agent Research (Optional)
1. **Install Claude Code**: Download from https://claude.ai/code
2. **Navigate to project**: Open 37degrees directory in Claude Code
3. **Run research**: `/37d-research "Book Title"`
4. **Monitor progress**: Check `books/NNNN_book/docs/findings/` for results
5. **Export system**: `./scripts/export-37d-system.sh` to backup agents

The 37d agent system generates comprehensive research including:
- Historical facts and biographical details
- Cultural impact analysis (films, adaptations, social media)
- Literary symbolism and cross-cultural interpretations
- Polish reception and educational context
- Gen Z relevance and modern connections
- Source validation and bibliography compilation

Results are saved in `books/NNNN_book/docs/findings/` with one file per agent.

### Additional Options
- **Only render video** (skip image generation): `python main.py video 17 --only-render`
- **Use custom template**: `python main.py video 17 --template my_template`
- **Generate specific book from collection**: `python main.py video classics 17`
- **Use different generator**: `python main.py ai 17 --generator comfyui`
- **Override settings**: `python main.py --set video.fps=60 video 17`
- **Use custom config**: `python main.py --config production.yaml ai 17`

### Book Structure

Each book requires the following directory structure:
```
books/NNNN_book_name/           # Book folder (e.g., 0017_little_prince)
├── book.yaml                   # Book configuration (required)
├── prompts/                    # AI prompts (auto-generated)
├── generated/                  # AI-generated images (auto-created)
├── frames/                     # Video frames (auto-created, gitignored)
└── docs/                       # Optional documentation
    ├── README.md              # Documentation guide
    ├── review.md              # Book research and facts
    └── book_page.html         # Interactive presentation

## 📚 Documentation

### 37d Agent System
- [Agent System Overview](.claude/agents/) - Complete documentation of research agents
- [Export System](scripts/export-37d-system.sh) - Backup and share agent system
- [Workflow Documentation](docs/agents/WORKFLOW.md) - Agent execution patterns
- [Book Structure](docs/agents/STRUCTURE-BOOK.md) - Directory organization for research

### Configuration
- [Configuration System](docs/CONFIGURATION.md) - Settings, environment variables, and overrides
- [Plugin Architecture](docs/PLUGIN_ARCHITECTURE.md) - Creating custom image generators
- [YAML Structures](docs/YAML_STRUCTURES.md) - All YAML file formats (book.yaml, collections, templates)
- [Book Structure](docs/BOOK_STRUCTURE.md) - Organization of book directories
- [Project Structure](docs/STRUCTURE.md) - Overall project organization

### Features
- [Emoji Support Guide](docs/EMOJI_SUPPORT_GUIDE.md) - Color emoji rendering in videos
- [Text Animation Guide](docs/TEXT_ANIMATION_GUIDE.md) - Dynamic text effects
- [Slide Renderer Guide](docs/SLIDE_RENDERER_GUIDE.md) - Advanced slide rendering system
- [HTML Page Generation Guide](docs/HTML_PAGE_GENERATION_GUIDE.md) - Creating interactive book pages

### AI Generation
- [InvokeAI Models Guide](docs/invoke_models_guide.md) - Recommended models for different genres
- [SDXL Resolutions](docs/sdxl_resolutions.md) - Optimal resolutions for SDXL
- [Setup ComfyUI](docs/setup_comfyui.md) - Alternative AI backend

## 🤝 Contributing

This project uses [Claude Code](https://claude.ai/code) for development assistance.

## 📄 License

MIT License