# Emoji Rendering Guide

## Overview

This guide explains how to properly use emojis in text overlays for the 37degrees TikTok video generator. The implementation uses the Pilmoji library to render color emojis correctly on video frames.

## Reference

Based on the excellent guide: https://jdhao.github.io/2022/04/03/add_color_emoji_to_image_in_python/

## How It Works

### 1. Emoji Support Configuration

Emojis are enabled by default in the template configuration:

```yaml
text_settings:
  enable_color_emojis: true  # Enable color emoji rendering
```

### 2. Text with Emojis

You can use emojis directly in your text fields in `book.yaml`:

```yaml
slides:
  - type: "hook"
    text: "Milioner, który stracił wszystko dla dziewczyny, która go nie chce. Simping level: MAX 💔"
  
  - type: "cta"
    text: "Największa polska powieść o toxic love! 📚"
```

### 3. Implementation Details

The system uses **Pilmoji** library which:
- Automatically detects emojis in text
- Downloads emoji images as needed (cached locally)
- Composites them seamlessly with regular text
- Supports all standard Unicode emojis

### 4. Text Layer Rendering

When rendering text with emojis:
1. Text is rendered on a transparent RGBA layer
2. Pilmoji handles both text and emoji rendering
3. Outline effects are applied to both text and emojis
4. The layer is then composited over the background

### 5. Supported Emoji Sources

Pilmoji can use emojis from:
- **Twemoji** (Twitter's emoji set) - default
- **Noto Color Emoji** (Google)
- **Apple Color Emoji** (if available)

### 6. Best Practices

1. **Use Standard Unicode Emojis**: Stick to widely supported emojis
2. **Test Rendering**: Always preview your videos to ensure emojis appear correctly
3. **Consider Contrast**: Emojis should be visible against your backgrounds
4. **Don't Overuse**: 1-2 emojis per slide maximum for readability

### 7. Troubleshooting

If emojis don't render correctly:

1. **Check Configuration**: Ensure `enable_color_emojis: true` in template
2. **Network Access**: First run requires internet to download emoji images
3. **Font Support**: System needs fonts with good Unicode coverage (Noto Sans, DejaVu)

### 8. Disabling Emojis

To disable color emojis and remove them from text:

```yaml
text_settings:
  enable_color_emojis: false  # Emojis will be stripped from text
```

## Technical Implementation

The emoji rendering is handled in `src/slide_renderer.py`:

```python
if has_emojis(text) and use_emoji_overlay:
    from pilmoji import Pilmoji
    drawer = Pilmoji(image)
    # Renders text with color emojis
    drawer.text((x, y), line, font=font, fill=color)
```

## Performance Considerations

- First emoji usage downloads images (one-time delay)
- Cached emojis render quickly in subsequent uses
- No significant performance impact on video generation

## Future Enhancements

- Custom emoji sets support
- Emoji size scaling options
- Animated emoji support (if needed)