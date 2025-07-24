# Emoji Support Guide

This guide explains the emoji support system in 37degrees, which enables color emoji rendering in video text overlays.

## Overview

The emoji system provides two main approaches:
1. **Text replacement** - Replace emojis with text equivalents for compatibility
2. **Color emoji rendering** - Render actual color emojis using the Pilmoji library

## Configuration

Enable color emoji support in your book's `book.yaml`:

```yaml
template_text_overlay:
  enable_color_emojis: true  # Enable Pilmoji color emoji rendering
  # ... other text overlay settings
```

## Components

### 1. Emoji Utils (`src/emoji_utils.py`)

Provides utilities for emoji detection and text replacement:

```python
from src.emoji_utils import replace_emojis_with_text, remove_emojis

# Replace emojis with Polish text equivalents
text = "Kocham książki! ❤️📚"
replaced = replace_emojis_with_text(text)
# Output: "Kocham książki! [serce][książki]"

# Remove all emojis
text_no_emoji = remove_emojis(text)
# Output: "Kocham książki! "
```

#### Supported Emoji Replacements

The system includes Polish youth-friendly replacements for common emojis:

- ❤️ → [serce]
- 😍 → [zakochane oczy]
- 😂 → [śmiech]
- 🔥 → [ogień]
- 📚 → [książki]
- ⭐ → [gwiazda]
- 💔 → [złamane serce]
- 😭 → [płacz]
- 🤔 → [myślenie]
- 😱 → [szok]
- 👑 → [korona]
- 🌍 → [świat]
- ✨ → [blask]
- 💫 → [magia]
- 🎭 → [teatr]
- 🗡️ → [miecz]
- 🏰 → [zamek]
- 🌹 → [róża]
- 🌊 → [fale]
- 🌙 → [księżyc]
- ☀️ → [słońce]
- 💎 → [diament]
- 🦁 → [lew]
- 👻 → [duch]
- 🎪 → [cyrk]

### 2. Enhanced Text Overlay (`src/text_overlay_emoji.py`)

Enhanced version of text overlay that supports color emoji rendering:

```python
from src.text_overlay_emoji import TextOverlay

# Create overlay with emoji support
overlay = TextOverlay(config)
image_with_text = overlay.add_text_to_image(image, "Najlepsza książka! ❤️📚")
```

Features:
- Automatic fallback to text replacement if Pilmoji fails
- Maintains all existing text overlay methods (outline, shadow, box, etc.)
- Preserves text positioning and styling

### 3. Integration with Video Generator

The video generator automatically uses the emoji-enabled text overlay when `enable_color_emojis: true` is set in the book configuration.

## How It Works

1. **Detection**: The system detects Unicode emoji characters in text
2. **Rendering**: 
   - If color emojis enabled: Uses Pilmoji to render actual emoji graphics
   - If disabled or fails: Falls back to text replacement
3. **Styling**: Applies the same text overlay method (outline, shadow, etc.) to the final result

## Font Requirements

For best results with emoji rendering:
- Use fonts with good Unicode support
- The system includes fallback fonts for missing glyphs
- Pilmoji handles emoji rendering separately from the main font

## Performance Considerations

- Color emoji rendering is slightly slower than text-only
- First-time emoji rendering may download emoji assets
- Caching improves performance for repeated renders

## Troubleshooting

### Emojis not rendering
1. Check that `enable_color_emojis: true` is set
2. Ensure Pilmoji is installed: `pip install pilmoji`
3. Check internet connection (for emoji asset download)

### Emojis appearing as boxes
- The fallback text replacement will be used automatically
- Check console output for any Pilmoji errors

### Text positioning issues
- Emoji heights may differ from regular text
- Adjust `line_spacing` in text overlay config if needed

## Example Configuration

```yaml
template_text_overlay:
  enable_color_emojis: true
  font_name: "Lato-Bold.ttf"
  font_size: 100
  text_color: "#FFFFFF"
  method: "outline"
  outline_width: 8
  outline_color: "#000000"
  position: "top"
  margin_top: 120
  line_spacing: 1.2
```

## Best Practices

1. **Test your emojis** - Not all emojis render well at all sizes
2. **Consider your audience** - Use emojis that resonate with Polish youth
3. **Don't overuse** - 1-2 emojis per slide maximum
4. **Fallback text** - Ensure emoji replacements make sense in context
5. **Preview first** - Always preview videos before publishing

## Future Enhancements

Planned improvements:
- Custom emoji sets for specific book themes
- Animated emoji support
- Better emoji-to-text mappings
- Emoji size scaling options