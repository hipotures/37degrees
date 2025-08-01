# Prompt Generation Guide

This document describes the prompt generation system in 37degrees v2.0.0+.

## Overview

The prompt generation system transforms book configurations (`book.yaml`) into AI-ready scene descriptions that can be used with various image generators (InvokeAI, ComfyUI, etc.).

## System Architecture

### Core Components

1. **Prompt Builder** (`src/prompt_builder.py`)
   - Main entry point for prompt generation
   - Converts book YAML to structured prompts
   - Supports multiple output formats

2. **Scene Generators** (`config/prompt/scene-generator/`)
   - **narrative-prompt-generator.md** - Story-focused scenes following plot
   - **flexible-prompt-generator.md** - Creative interpretation of book themes
   - **podcast-image-prompt-generator.md** - Ambient podcast visuals
   - **atmospheric-moments-generator.md** - Weather and mood focused
   - **emotional-journey-generator.md** - Emotional arc visualization
   - **automatic-style-selector.md** - Style selection helper

3. **Graphic Styles** (`config/prompt/graphics-styles/`)
   - 37 predefined visual styles in JSON format
   - Each style includes detailed rendering instructions
   - Styles range from pencil sketches to 3D renders

## Prompt Generation Process

### Step 1: Scene Generation

Scene generation is done using the 37degrees custom command system:

#### Using Claude Code Commands:

```bash
# Generate scenes using the /37d-s1-gen-scenes command
# Syntax: /37d-s1-gen-scenes "Book Title" "Author" [generator_type]

# Examples:
/37d-s1-gen-scenes "Little Prince" "Saint-Exupéry" narrative
/37d-s1-gen-scenes "Treasure Island" "Stevenson" flexible
/37d-s1-gen-scenes "Wuthering Heights" "Emily Brontë" emotional

# If generator type is omitted, defaults to 'podcast'
/37d-s1-gen-scenes "1984" "Orwell"
```

This creates scene descriptions in:
- `books/NNNN_book_name/prompts/scenes/[type]/scene_XX.json`

Where `[type]` can be:
- `narrative` - Story-driven scenes following plot
- `flexible` - Creative interpretations of themes
- `podcast` - Ambient visuals (default)
- `atmospheric` - Weather and mood focused
- `emotional` - Emotional journey visualization

#### Manual Generation:

```bash
# Legacy method using main.py (generates old format)
python main.py prompts 17

# Or use the standalone tool
python src/prompt_builder.py books/0017_little_prince/book.yaml
```

### Step 2: Style Application

Apply graphic styles to scene descriptions using the 37degrees command system:

1. First generate scenes: `/37d-s1-gen-scenes "Book" "Author" [type]`
2. Then apply styles: `/37d-s2-apply-style "Book" "Author" [style_name]`

The command will:
- Find existing scene files in the correct directory
- Apply the chosen visual style from the graphics-styles library
- Generate complete AI-ready prompts

### Scene Description Structure

Each scene JSON file contains:

```json
{
  "scene_number": 1,
  "timestamp": "0:00-0:03",
  "description": "Detailed scene description...",
  "focus_elements": ["element1", "element2"],
  "mood": "contemplative",
  "composition": {
    "type": "wide_shot",
    "perspective": "eye_level"
  }
}
```

## Generator Types

### 1. Narrative Generator
- Follows book plot closely
- 25 scenes mapping to key story moments
- Best for: Classic literature adaptations

### 2. Flexible Generator
- Creative interpretation of themes
- Symbolic and metaphorical imagery
- Best for: Abstract or philosophical works

### 3. Podcast Image Generator
- Stand-alone ambient visuals
- Not tied to specific plot points
- Best for: Background visuals during narration

### 4. Atmospheric Moments Generator
- Focus on weather, lighting, time of day
- Environmental storytelling
- Best for: Mood-driven narratives

### 5. Emotional Journey Generator
- Visualizes emotional arc
- Body language and environmental cues
- Best for: Character-driven stories

## Style Selection

Use `automatic-style-selector.md` to choose appropriate styles:

### Most Versatile Styles
- **pencil-sketch-style** - Universal, intimate
- **watercolor-style** - Emotional, timeless
- **line-art-style** - Clean, adaptable
- **oil-painting-style** - Rich, classic

### By Genre
- **Fantasy**: mythological-epic-style, concept-art-fantasy-style
- **Mystery**: noir-pulp-fiction-style, hatching-crosshatch-style
- **Children's**: children-book-illustration-style, 3d-clay-render-style
- **Historical**: victorian-book-illustration-style, oil-painting-style

### By Era
- **Victorian**: victorian-book-illustration-style, hatching-crosshatch-style
- **Modern**: anime-style, flat-design-style, glitch-art-style
- **Timeless**: pencil-sketch-style, watercolor-style

## Configuration

### book.yaml Settings

Key settings affecting prompt generation:

```yaml
# Art style configuration
template_art_style: "Illustration"  # Or "-" for custom
custom_art_style:
  primary_style: "childlike watercolor illustrations"
  # ... detailed style settings

# Technical specs affect prompt optimization
technical_specs:
  resolution: "832x1248"  # SDXL optimal resolution
```

### Command Line Options

```bash
# Generate prompts with specific style
python main.py prompts 17 --style watercolor

# Regenerate after editing book.yaml
python main.py prompts little_prince --force
```

## Best Practices

1. **Choose Generator Based on Content**
   - Narrative for plot-driven books
   - Flexible for thematic exploration
   - Podcast for ambient backgrounds

2. **Match Style to Book Era/Mood**
   - Use automatic-style-selector.md
   - Test 2-3 scenes before committing
   - Consider thumbnail visibility

3. **Consistency Across Scenes**
   - Maintain style throughout 25 scenes
   - Use same generator type
   - Keep color palette consistent

4. **Avoid Common Issues**
   - No text/letters in images
   - Reserve upper third for text overlay
   - Ensure safe zones for social media

## Integration with AI Generators

Generated prompts work with:

1. **InvokeAI** (primary)
   - Uses style presets
   - Optimal SDXL settings
   - Batch generation support

2. **ComfyUI**
   - Custom workflows
   - Advanced control
   - Manual process

3. **Mock Generator**
   - Testing and development
   - Instant results
   - No GPU required

## File Organization

```
books/NNNN_book_name/
├── book.yaml
└── prompts/
    ├── scenes/              # New format (v2.0+)
    │   ├── narrative/       # Story-following scenes
    │   │   ├── scene_01.json
    │   │   └── ... (25 files)
    │   ├── flexible/        # Creative interpretation
    │   │   ├── scene_01.json
    │   │   └── ... (25 files)
    │   ├── podcast/         # Ambient backgrounds
    │   │   ├── scene_01.json
    │   │   └── ... (25 files)
    │   ├── atmospheric/     # Weather/mood focus
    │   │   ├── scene_01.json
    │   │   └── ... (25 files)
    │   └── emotional-journey/ # Emotional arc
    │       ├── scene_01.json
    │       └── ... (25 files)
    └── legacy/              # Old format prompts
        ├── scene_01_prompt.yaml
        └── ...
```

## Troubleshooting

### Prompts Not Generating
- Check book.yaml syntax
- Ensure book ID is 4 digits
- Verify slide definitions exist

### Style Mismatch
- Review automatic-style-selector.md
- Test with different styles
- Check AI model compatibility

### Inconsistent Results
- Use same random seed
- Maintain prompt structure
- Keep style parameters constant

## Future Enhancements

- Multi-language prompt support
- Dynamic style mixing
- Context-aware scene transitions
- Character consistency tracking