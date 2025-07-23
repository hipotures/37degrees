# 37degrees - TikTok Video Generator for Book Reviews

🔥 **37 stopni - gorączka czytania!** 

Automated video generator for creating engaging TikTok book reviews targeting Polish youth (10-20 years old). Creates 8-slide vertical videos with AI-generated illustrations and text overlays for classic literature.

## 📖 Overview

37degrees generates short-form video content for the @37stopni TikTok account, featuring:
- **8 slides per book** with specific hooks, quotes, and CTAs
- **AI-generated illustrations** in a childlike, non-photorealistic style
- **Text overlays** with multiple visibility methods
- **Automated video creation** with Ken Burns effects and transitions

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

# Generate AI images for entire collection
python main.py ai classics
```

## 📁 Project Structure

```
37degrees/
├── main.py              # Main entry point with intuitive CLI
├── src/                 # Core application code
│   ├── cli/            # CLI modules (collections, list, video, ai)
│   ├── video_generator.py         # Video creation with effects
│   ├── simple_invokeai_generator.py # AI image generation
│   ├── prompt_builder.py          # Convert scenes to AI prompts
│   └── text_overlay.py            # Text rendering methods
├── books/               # Book configurations and assets
│   └── NNNN_[book_name]/ # Books numbered by ID (e.g., 0017_little_prince)
│       ├── book.yaml    # Book configuration
│       ├── generated/   # AI-generated images
│       └── prompts/     # Generated AI prompts
├── collections/         # Book collections/series
│   └── classics.yaml    # Main collection of 37 classic books
├── scripts/            # Helper and test scripts
├── shared_assets/      # Fonts, backgrounds, etc.
└── docs/              # Documentation
```

## ⚡ Features

### AI Image Generation
- Uses InvokeAI with SDXL models
- Optimized resolution (832x1248) to avoid artifacts
- Style presets: Illustration, Sketch, etc.
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

- Python 3.8+
- InvokeAI running on http://localhost:9090
- NVIDIA GPU with NVENC support (optional)
- FFmpeg with NVENC (for GPU encoding)

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/yourusername/37degrees.git
cd 37degrees

# Install dependencies with uv
uv pip install -r requirements.txt

# Or with pip
pip install -r requirements.txt
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

### Additional Options
- **Only render video** (skip image generation): `python main.py video 17 --only-render`
- **Use custom template**: `python main.py video 17 --template my_template`
- **Generate specific book from collection**: `python main.py video classics 17`

## 📚 Documentation

- [InvokeAI Models Guide](docs/invoke_models_guide.md) - Recommended models for different genres
- [SDXL Resolutions](docs/sdxl_resolutions.md) - Optimal resolutions for SDXL
- [Project Structure](docs/STRUCTURE.md) - Detailed project organization
- [Setup ComfyUI](docs/setup_comfyui.md) - Alternative AI backend

## 🤝 Contributing

This project uses [Claude Code](https://claude.ai/code) for development assistance.

## 📄 License

Private project for @37stopni TikTok account.