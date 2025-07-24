# CLAUDE.md Verification Report

This report compares the CLAUDE.md documentation against the actual project structure and features.

## 1. Commands Comparison

### ❌ Commands in CLAUDE.md that are INCORRECT or OUTDATED:

**CLAUDE.md shows:**
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

**ACTUAL commands in main.py:**
```bash
# Generate video (by ID or name)
python main.py video 17
python main.py video little_prince

# Generate AI images
python main.py ai 17
python main.py ai little_prince

# Generate prompts
python main.py prompts 17
python main.py prompts little_prince

# Generate both AI images and video
python main.py generate 17
python main.py generate little_prince

# List commands
python main.py list
python main.py list classics
python main.py collections
```

### Issues:
1. **Wrong video command syntax**: CLAUDE.md shows passing a YAML file path, but main.py expects book ID/name
2. **Missing new commands**: CLAUDE.md doesn't mention the `ai`, `generate`, `prompts`, `list`, or `collections` commands
3. **create_video.py location**: It's in `scripts/` not in book directories
4. **Direct script execution**: CLAUDE.md suggests running scripts directly, but main.py provides a unified CLI

## 2. Architecture Description

### ✅ CORRECT Components:
- Book Configuration structure (book.yaml)
- Prompt Generation (src/prompt_builder.py exists)
- AI Integration files exist
- Video Creation components exist
- Text overlay functionality exists

### ❌ MISSING or INCORRECT:
1. **CLI structure not mentioned**: The `src/cli/` directory with modular command handlers
2. **Multiple AI generators**: The docs mention ComfyUI and InvokeAI but don't mention the variety:
   - `invokeai_generator.py`
   - `invokeai_direct_generator.py`
   - `invokeai_websocket_generator.py`
   - `simple_invokeai_generator.py`
   - `comfyui_generator.py`
3. **New features not documented**:
   - `emoji_utils.py` - Emoji rendering support
   - `text_animator.py` - Text animation features
   - `slide_renderer.py` - Slide rendering
   - `optimized_video_generator.py` - Optimized video generation
   - Multiple text overlay variants

## 3. Directory Structure

### ✅ CORRECT:
- Basic book directory structure
- `shared_assets/` structure
- `src/` exists

### ❌ INCORRECT or OUTDATED:
1. **scenes/ vs generated/**: CLAUDE.md mentions "scenes/ or scenes_v2/" but actual books use "generated/"
2. **frames/ directory**: Mentioned as gitignored, but present in book 0017
3. **Missing directories**:
   - `scripts/` - Contains utility scripts
   - `collections/` - Contains collection definitions
   - `output/` - Contains generated videos
   - `docs/` - Project documentation
4. **Book numbering**: Books are prefixed with numbers (e.g., `0016_lalka`, `0017_little_prince`)

## 4. File Paths and Locations

### ❌ INCORRECT:
1. **create_video.py**: Located in `scripts/` not in individual book directories
2. **migrate_structure.py**: Located in `scripts/` not in root
3. **test_text_overlay.py**: Not found, but `text_overlay.py` exists in `src/`

## 5. Missing Context

### Not mentioned in CLAUDE.md:
1. **Collections system**: The project has a collections feature for grouping books
2. **Book numbering scheme**: Books use a 4-digit prefix (0001, 0002, etc.)
3. **Output directory**: Generated videos go to `output/`
4. **Multiple test scripts** in `scripts/`
5. **HTML generation features**: Templates for web pages
6. **Audio support**: Books have audio directories with theme music
7. **Emoji rendering**: New feature with dedicated utils

## Summary

The CLAUDE.md file appears to be **significantly outdated** and doesn't reflect the current state of the project. Key issues:

1. **Command syntax is completely wrong** - the project now uses a subcommand-based CLI
2. **Missing major features** - collections, numbered books, new generators
3. **Incorrect file locations** - many paths are wrong
4. **Outdated directory structure** - doesn't reflect actual organization

The project has evolved significantly beyond what's documented in CLAUDE.md, with a more sophisticated CLI interface, better organization, and additional features not mentioned in the documentation.