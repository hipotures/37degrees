# Slide Renderer Guide

This guide covers the advanced slide rendering system in 37degrees, which handles the creation of individual video slides with effects and overlays.

## Overview

The slide renderer (`src/slide_renderer.py`) is responsible for:
- Rendering slides with Ken Burns effect
- Adding progress indicators and slide counters
- Applying text overlays with animations
- Managing fonts with fallback support
- Handling different rendering methods per slide type

## Architecture

```
SlideRenderer
├── Frame rendering with Ken Burns
├── Text overlay integration
├── Text animation integration
├── Progress indicator rendering
├── Font management system
└── Template-based styling
```

## Configuration

Configure the slide renderer through book.yaml:

```yaml
# Ken Burns effect settings
ken_burns:
  zoom_factor: 1.15        # How much to zoom (1.0 = no zoom)
  zoom_direction: "in"     # "in" or "out"
  pan_direction: "random"  # "left", "right", "up", "down", or "random"

# Progress indicator
show_slide_counter: true   # Show "1/8" style counter
slide_counter_position: "bottom_right"
slide_counter_style:
  font_size: 36
  color: "#FFFFFF"
  opacity: 0.7
  margin: 20

# Font configuration with fallbacks
fonts:
  primary: "Lato-Bold.ttf"
  fallback:
    - "NotoSans-Bold.ttf"
    - "DejaVuSans-Bold.ttf"
```

## Ken Burns Effect

The Ken Burns effect adds subtle motion to static images:

### Configuration Options

```yaml
ken_burns:
  zoom_factor: 1.15        # 15% zoom
  zoom_direction: "in"     # Zoom in over time
  pan_direction: "right"   # Pan to the right
```

### Zoom Directions
- **"in"** - Start wide, zoom in
- **"out"** - Start close, zoom out

### Pan Directions
- **"left"** - Pan from right to left
- **"right"** - Pan from left to right  
- **"up"** - Pan from bottom to top
- **"down"** - Pan from top to bottom
- **"random"** - Random direction per slide

### Safe Zone Considerations

The renderer ensures text and important content stay within TikTok's safe zones:
- Top safe zone: 120px (for text)
- Bottom safe zone: 150px (for TikTok UI)
- Side margins: 80px each

## Rendering Methods

Different slide types can use different rendering approaches:

### 1. Standard Rendering
Most slides use the standard rendering pipeline:
```python
renderer.render_slide(slide_data, config)
```

### 2. Hook Slides
Special handling for attention-grabbing hooks:
- Larger zoom factor possible
- More dramatic pan movements
- Higher contrast text overlays

### 3. Quote Slides
Optimized for readability:
- Minimal Ken Burns movement
- Centered text positioning
- Extra padding around text

### 4. CTA Slides
Call-to-action optimization:
- Static or pulsing effects
- High contrast colors
- Clear visual hierarchy

## Progress Indicators

### Slide Counter
Shows current position in video (e.g., "3/8"):

```yaml
show_slide_counter: true
slide_counter_position: "bottom_right"  # or "bottom_left", "top_right", "top_left"
slide_counter_style:
  font_size: 36
  color: "#FFFFFF"
  opacity: 0.7
  background: true         # Add semi-transparent background
  background_color: "#000000"
  background_opacity: 0.5
  padding: 10
```

### Progress Bar (Future)
Planned visual progress bar:
```yaml
show_progress_bar: true
progress_bar_style:
  position: "bottom"
  height: 4
  color: "#FFFFFF"
  background_color: "#000000"
  opacity: 0.8
```

## Font Management

The renderer includes sophisticated font handling:

### Font Fallback Chain
```yaml
fonts:
  primary: "CustomFont.ttf"
  fallback:
    - "NotoSans-Bold.ttf"     # Good Unicode support
    - "NotoSansEmoji.ttf"     # Emoji support
    - "DejaVuSans-Bold.ttf"   # System fallback
```

### Font Loading
1. Searches in `shared_assets/fonts/`
2. Falls back to system fonts
3. Uses default if all fail

### Unicode Support
- Automatic font selection for special characters
- Polish diacritics support (ą, ć, ę, ł, ń, ó, ś, ź, ż)
- Emoji rendering via separate system

## Performance Optimization

The renderer includes several optimizations:

1. **Frame Caching**
   - Reuses base frames when possible
   - Caches font objects

2. **Parallel Processing**
   - Used in `OptimizedVideoGenerator`
   - Multi-core frame rendering

3. **Memory Management**
   - Releases frames after processing
   - Efficient image operations

## Integration Example

```python
from src.slide_renderer import SlideRenderer

# Initialize renderer
renderer = SlideRenderer(config)

# Render a single slide
slide_clip = renderer.render_slide(
    slide_index=0,
    slide_data={
        'type': 'hook',
        'text': 'Czy wiesz, że książki mogą zmienić życie?',
        'scene': {...}
    },
    image_path='generated/scene_01.png',
    duration=3.5,
    book_config=book_config
)
```

## Customization

### Custom Render Methods

Add slide-type specific rendering:

```python
class CustomSlideRenderer(SlideRenderer):
    def render_slide(self, slide_index, slide_data, ...):
        if slide_data['type'] == 'custom':
            return self.render_custom_slide(...)
        return super().render_slide(...)
    
    def render_custom_slide(self, ...):
        # Custom rendering logic
        pass
```

### Effect Combinations

Combine multiple effects:
```yaml
effects:
  ken_burns:
    zoom_factor: 1.1
  vignette:
    strength: 0.3
  color_overlay:
    color: "#0000FF"
    opacity: 0.1
```

## Best Practices

1. **Ken Burns Subtlety**
   - Keep zoom factor between 1.05-1.20
   - Use slow, smooth movements
   - Match movement to content mood

2. **Text Readability**
   - Ensure sufficient contrast
   - Keep text in safe zones
   - Test on mobile screens

3. **Performance**
   - Pre-generate frames for complex effects
   - Use appropriate image resolutions
   - Monitor memory usage

4. **Consistency**
   - Maintain visual style across slides
   - Use consistent timing
   - Follow template guidelines

## Troubleshooting

### Text Cut Off
- Check safe zone margins
- Reduce font size
- Adjust text positioning

### Choppy Animation
- Reduce frame rate for preview
- Simplify effects
- Check system resources

### Memory Issues
- Process slides in batches
- Reduce image resolution
- Clear frame cache periodically

## Future Enhancements

Planned features:
- Advanced transition effects
- Particle systems for CTAs
- Dynamic color grading
- AI-powered composition adjustment
- Real-time preview system