# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
37degrees - TikTok video generator for Polish youth promoting classic literature through AI-generated visual content. Creates 25 scenic illustrations per book for vertical videos (1080x1920).

## Essential Commands

### Quick Start
```bash
# Setup
uv pip install -r requirements.txt

# Basic Operations
python main.py list                            # List all books
python main.py generate 17                     # Full pipeline for book #17
python main.py video 17                        # Video from existing images
python main.py ai 17 --generator mock          # Test without GPU

# Batch Operations  
python main.py generate classics               # Process entire collection
```

### Research & Agent System
```bash
/37d-research "Book Title"                      # Run specialized research agents
python main.py research 17 --provider perplexity
```

### TODOIT Documentation
Use: `docs/TODOIT_CLI_GUIDE.md`, `docs/TODOIT_MCP_TOOLS.md`, `docs/TODOIT_API.md`

## Architecture

### Core Structure
```
books/NNNN_name/          # Book directories
├── book.yaml            # Configuration
├── generated/           # 25 AI images
├── prompts/            # Scene prompts  
└── docs/findings/      # Research output

src/
├── cli/                # Commands (ai, video, research)
├── generators/         # AI generators (InvokeAI, ComfyUI, Mock)
└── research/          # Providers (Perplexity, Google, Mock)
```

### Key Patterns
- **Plugin Architecture**: Auto-discovery of generators via registry
- **Provider Pattern**: Pluggable research APIs
- **37d Agents**: Auto-discovered from `.claude/agents/37d-*.md`
- **MCP Integration**: TODOIT for task management, Playwright for automation

### Configuration
- Main: `config/settings.yaml`
- Override: `.env` file or `--set` flag
- Collections: `collections/classics.yaml`

## Development Workflow

### Adding Books
1. Create `books/NNNN_bookname/` directory
2. Configure `book.yaml`
3. Run `python main.py generate NNNN`

### Testing
```bash
python main.py ai 17 --generator mock          # Mock AI generation
python main.py research 17 --provider mock     # Mock research
```

### Important Scripts
- `scripts/todoit-dwn-img.sh` - Batch image downloads
- `scripts/export-37d-system.sh` - Export agent system  
- `scripts/run_research_batch.sh` - Batch research

## Polish Project Specifics
- Content in Polish for youth audience
- 24-hour time format
- SSH for GitHub (not HTTPS)
- No real credentials in commits
- UTC vs local time awareness

## No Formal Testing/Linting
Project uses mock generators for testing. Follow existing code style.