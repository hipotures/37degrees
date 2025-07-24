# YAML Structure Documentation

This document describes all YAML configuration files used in the 37degrees project.

## 1. Book Configuration (`book.yaml`)

Each book must have a `book.yaml` file with the following structure:

### Complete Structure

```yaml
# Book metadata
book_info:
  title: "Book Title"                    # Book title in Polish
  author: "Author Name"                  # Author's name
  year: 1943                            # Publication year
  genre: "Genre"                        # Genre in Polish
  reading_time: "2-3 godziny"           # Estimated reading time

# Technical specifications
technical_specs:
  resolution: "832x1248"                # AI generation resolution (SDXL optimal)
  output_resolution: "1080x1920"        # Final video resolution (9:16)
  aspect_ratio: "2:3"                   # Generation aspect ratio
  format: "vertical"                    # Video format
  fps: 30                               # Frames per second
  duration_per_slide: 3.5               # Seconds per slide

# AI generation settings
ai_generation:
  model_key: "uuid-here"                # Model UUID from InvokeAI
  model_name: "Model Name"              # Human-readable model name
  steps: 30                             # Generation steps
  cfg_scale: 7.5                        # Classifier-free guidance scale
  sampler: "euler_a"                    # Sampling method

# Style configuration
template_art_style: "Illustration"      # InvokeAI style preset or "-" for custom
custom_art_style:                       # Custom style (used if template_art_style is "-")
  primary_style: "style description"
  complexity: "complexity level"
  line_work: "line style"
  shapes: "shape description"
  color_technique: "coloring method"
  color_palette:
    base: ["color1", "color2"]
    accents: ["color3", "color4"]
    mood: "color mood"
  overall_feeling: "atmosphere"
  magic_style: "effects description"
  background_approach: "background style"
  avoid: "what to avoid"
  emphasize: "what to emphasize"

# Text overlay configuration
text_overlay:
  method: "outline"                     # outline, shadow, box, gradient, glow
  
  # Method-specific settings
  outline:
    color: "black"
    width: 3
  
  font:
    family: "Arial"
    size: 48
    color: "white"
    weight: "bold"
    line_height: 1.4
    alignment: "center"

# Optional: Override template settings
template_text_overlay:
  enable_color_emojis: true             # Enable emoji support
  font_name: "Lato-Bold.ttf"
  font_size: 100
  text_color: "#FFFFFF"
  method: "outline"
  outline_width: 8
  outline_color: "#000000"

# Optional: Text timing
template_text_timing:
  fade_in_start: 0.5
  fade_in_duration: 0.3
  fade_out_start: 3.0
  fade_out_duration: 0.3

# Optional: Text animation
template_text_animation:
  entrance: "fade"
  exit: "fade_out"
  entrance_duration: 0.5
  exit_duration: 0.3

# Optional: Audio settings
audio:
  theme_music: "audio/theme.mp3"
  volume: 0.3                           # Volume override (0.0-1.0)

# Slides definition
slides:
  - type: "hook"                        # Slide type
    text: "Hook text here"              # Text to display
    scene:                              # Scene description for AI
      elements:
        - "element 1"
        - "element 2"
      composition: "how elements are arranged"
      style: "specific style notes"
      mood: "emotional tone"
      notes: "additional instructions"
      
  - type: "intro"
    text: "Introduction text"
    scene:
      # ... scene details
      
  # ... more slides (typically 8 total)
```

### Slide Types

Standard slide types used in videos:
- `hook` - Attention-grabbing opening
- `intro` - Book introduction
- `quote` - Memorable quote
- `fact` - Interesting fact
- `question` - Thought-provoking question
- `comparison` - Modern comparison
- `conclusion` - Summary
- `cta` - Call to action

## 2. Collection Configuration (`collections/*.yaml`)

Collections group books into series:

```yaml
# Collection metadata (optional)
collection_info:
  name: "Klasyka Światowa"
  description: "37 najważniejszych książek światowej literatury"
  theme: "Książki, które musisz znać"

# Books in the collection
books:
  - order: 1                            # Display order
    path: books/0017_little_prince/book.yaml
    tags:                               # Optional tags
      - filozofia
      - baśń
      - klasyka XX wieku
      
  - order: 2
    path: books/0021_nineteen_eighty_four/book.yaml
    tags:
      - dystopia
      - polityka
      - klasyka XX wieku
      
  # ... more books
```

## 3. Template Configuration (`shared_assets/templates/*.yaml`)

Templates provide default settings for books:

```yaml
# Template information
template_info:
  name: "Classics Template"
  version: "1.0"
  description: "Template for classic literature"

# Default technical specs
technical_specs:
  resolution: "832x1248"
  output_resolution: "1080x1920"
  fps: 30
  duration_per_slide: 3.5

# Default AI settings
ai_generation:
  model_key: "default-model-uuid"
  steps: 30
  cfg_scale: 7.5
  sampler: "euler_a"

# Default text overlay
text_overlay:
  enable_color_emojis: false
  font_name: "Lato-Bold.ttf"
  font_size: 100
  text_color: "#FFFFFF"
  method: "outline"
  outline_width: 8
  outline_color: "#000000"
  position: "top"
  margin_top: 120
  margin_left: 80
  margin_right: 80
  line_spacing: 1.2
  max_width: 920

# Default text timing
text_timing:
  fade_in_start: 0.5
  fade_in_duration: 0.3
  fade_out_start: 3.0
  fade_out_duration: 0.3

# Default animations
text_animation:
  entrance: "fade"
  exit: "fade_out"
  entrance_duration: 0.5
  exit_duration: 0.3

# Animation settings per slide type
slide_animations:
  hook:
    entrance: "slide_up"
    entrance_duration: 0.7
  quote:
    entrance: "typewriter"
    entrance_duration: 1.5
  cta:
    entrance: "bounce"
    exit: "zoom_out"

# Audio settings
audio:
  theme_music: "shared_assets/audio/default_theme.mp3"
  fade_in: 1.0
  fade_out: 1.0
  volume: 0.5
```

## 4. Prompt Configuration (`books/*/prompts/*.yaml`)

Auto-generated by `prompt_builder.py`:

```yaml
prompt:
  positive: "Full positive prompt for AI generation"
  negative: "Negative prompt (what to avoid)"
  
scene_info:
  slide_type: "hook"
  slide_index: 0
  description: "Original scene description from book.yaml"
  
generation_params:
  width: 832
  height: 1248
  model: "Dreamshaper XL v2 Turbo"
  steps: 30
  cfg_scale: 7.5
  sampler: "euler_a"
```

## Usage Notes

1. **Inheritance**: Books can override any template setting
2. **Required fields**: Only `book_info` and `slides` are required in book.yaml
3. **Style presets**: Use InvokeAI presets or define custom styles
4. **Collections**: Books can appear in multiple collections
5. **Templates**: Provide consistent defaults across books

## Validation

To ensure YAML validity:
- Use proper indentation (2 spaces)
- Quote strings with special characters
- Use lists for multiple items
- Comment optional sections