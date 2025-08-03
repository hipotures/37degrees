# 37 Degrees - Project Structure

## Overview

The project has been reorganized to better support multimedia content for each book. Each book now has its own directory containing all related assets.

**Version 2.0.0 Update**: Added plugin architecture for image generators and centralized configuration system.

## Directory Structure

```
37degrees/
├── books/                      # All book content
│   └── NNNN_[book_name]/      # Individual book directory (e.g., 0017_little_prince)
│       ├── book.yaml          # Book metadata and slides
│       ├── docs/              # Documentation and research
│       │   ├── findings/      # All *findings.md files
│       │   │   ├── 37d-facts-hunter_findings.md
│       │   │   ├── 37d-symbol-analyst_findings.md
│       │   │   └── ...
│       │   ├── todo/          # All TODO_*.md files (agent TODOs and master TODO)
│       │   │   ├── TODO_master.md
│       │   │   ├── TODO_37d-facts-hunter.md
│       │   │   ├── TODO_37d-symbol-analyst.md
│       │   │   └── ...
│       ├── search_history/      # Centralized search data from all agents
│       │   ├── search_WebSearch_20250729_143025_12345.json
│       │   ├── search_WebFetch_20250729_143142_67890.json
│       │   └── searches_index.txt
│       │   ├── review.md      # Fascinating facts and discoveries
│       │   ├── book_page.html # Interactive HTML presentation
│       │   └── README.md      # Documentation guide
│       ├── generated/         # AI-generated images
│       ├── prompts/           # Generated AI prompts
│       │   ├── scenes/        # Scene descriptions (v2.0+)
│       │   │   ├── narrative/ # Story-focused scenes
│       │   │   ├── flexible/  # Flexible creative scenes
│       │   │   ├── podcast/   # Podcast-style scenes
│       │   │   ├── atmospheric/ # Atmospheric moment scenes
│       │   │   └── emotional/ # Emotional journey scenes
│       │   ├── genimage/      # Final AI-ready prompts (scene + style merged)
│       │   ├── narrative/     # Legacy narrative prompts
│       │   ├── epic/          # Legacy epic prompts
│       │   └── modern/        # Legacy modern prompts
│       ├── cover.jpg/png      # Book cover image
│       ├── background.jpg/png # Custom background (optional)
│       ├── audio/             # Book-specific audio
│       │   ├── theme.mp3      # Main theme music
│       │   └── narration.mp3  # Voice narration (future)
│       └── assets/            # Additional assets
│           ├── quotes/        # Quote images
│           └── characters/    # Character art
│
├── shared_assets/             # Shared resources
│   ├── fonts/                 # Common fonts
│   ├── music/                 # Shared background music
│   ├── templates/             # HTML and video templates
│   │   ├── book_page_template.html
│   │   └── book_page_data_example.json
│   └── backgrounds/           # Shared AI-generated backgrounds
│
├── collections/               # Series definitions
│   └── classics.yaml          # Classic books series (37 books)
│
├── scripts/                   # Helper scripts
│   ├── create_docs_structure.py # Auto-create docs directories
│   └── ...
│
├── docs/                      # Project documentation
│   ├── CONFIGURATION.md      # Configuration system guide
│   ├── PLUGIN_ARCHITECTURE.md # Image generator plugins
│   ├── PROMPT_GENERATION_GUIDE.md # Prompt generation system
│   ├── HTML_PAGE_GENERATION_GUIDE.md
│   ├── BOOK_STRUCTURE.md
│   └── ...
│
├── config/                    # Configuration files
│   ├── settings.yaml         # Main configuration
│   ├── generators.yaml       # Image generator settings
│   └── prompt/               # Prompt generation configs
│       ├── graphics-styles/  # Visual style definitions (YAML)
│       ├── scene-generator/  # Scene generation templates
│       │   ├── scene-description-template.yaml
│       │   ├── narrative-prompt-generator.md
│       │   ├── flexible-prompt-generator.md
│       │   ├── podcast-image-prompt-generator.md
│       │   ├── atmospheric-moments-generator.md
│       │   ├── emotional-journey-generator.md
│       │   └── automatic-style-selector.md
│       └── scene-description-template.yaml
│
├── output/                    # Generated videos
│
└── src/                       # Source code
    ├── cli/                   # CLI command modules
    ├── generators/            # Image generator plugins
    │   ├── base.py          # Abstract base class
    │   ├── registry.py      # Plugin registry
    │   ├── invokeai.py      # InvokeAI implementation
    │   ├── comfyui.py       # ComfyUI implementation
    │   └── mock.py          # Mock generator for testing
    ├── config.py             # Configuration management
    └── ...                    # Other modules
```

## Benefits of New Structure

1. **Self-contained books**: Each book has all its assets in one place
2. **Easy asset management**: Add cover, background, music directly to book folder
3. **Series flexibility**: Same book can appear in multiple series
4. **Better scalability**: Adding new books is straightforward
5. **Asset discovery**: Code automatically finds book-specific assets

## Adding a New Book

1. Create a new book directory structure:
   ```
   books/NNNN_book_name/
   ├── book.yaml          # Book configuration (copy from another book and modify)
   ├── prompts/           # Will be auto-generated
   ├── generated/         # Will be auto-created when generating images
   └── docs/              # Optional documentation
       └── review.md      # Fascinating facts about the book
   ```

2. Copy and modify `book.yaml` from an existing book

3. Add the book to a collection file (e.g., `collections/classics.yaml`)
   - Use templates from `shared_assets/templates/` for HTML page
   - See [HTML Page Generation Guide](HTML_PAGE_GENERATION_GUIDE.md)

4. Add optional assets:
   - `cover.jpg` or `cover.png` - Book cover
   - `background.jpg` or `background.png` - Custom background
   - `audio/theme.mp3` - Book-specific music
   - Any other assets in the `assets/` folder

5. Add the book to a series (e.g., in `collections/classics.yaml`)

## Asset Priority

The system looks for assets in this order:

1. **Book-specific** (in book folder)
2. **Shared assets** (in shared_assets/)
3. **Generated/default** (created on demand)

For example, backgrounds:
- First checks: `books/[book_name]/background.jpg`
- Then checks: `shared_assets/backgrounds/[prompt_hash].png`
- Finally: Generates new background based on prompt

## Migration from Old Structure

A migration script `migrate_structure.py` was used to convert from the old structure:
- Old: `books/[a-z]/[a-z]/book_name.yaml`
- New: `books/book_name/book.yaml`

The old structure is backed up in `books_backup/` and can be removed once everything is verified to work correctly.