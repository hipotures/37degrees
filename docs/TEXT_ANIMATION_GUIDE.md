# Text Animation Guide

This guide covers the text animation system in 37degrees, which provides dynamic text effects for video slides.

## Overview

The text animation system (`src/text_animator.py`) enables sophisticated text animations including:
- Multiple entrance animations
- Exit animations
- Configurable timing and easing
- Per-slide type customization

## Configuration

Configure animations in your book's `book.yaml`:

```yaml
# Global animation settings
template_text_animation:
  entrance: "fade"          # Default entrance animation
  exit: "fade_out"         # Default exit animation
  entrance_duration: 0.5   # Duration in seconds
  exit_duration: 0.3       # Duration in seconds
  
# Per-slide type overrides
slide_animations:
  hook:
    entrance: "slide_up"
    entrance_duration: 0.7
  quote:
    entrance: "typewriter"
    entrance_duration: 1.0
  cta:
    entrance: "zoom"
    exit: "zoom_out"
```

## Available Animations

### Entrance Animations

1. **fade** - Gradual opacity increase
   ```yaml
   entrance: "fade"
   entrance_duration: 0.5
   ```

2. **slide_up** - Slide in from bottom
   ```yaml
   entrance: "slide_up"
   entrance_duration: 0.6
   ```

3. **slide_down** - Slide in from top
   ```yaml
   entrance: "slide_down"
   entrance_duration: 0.6
   ```

4. **slide_left** - Slide in from right
   ```yaml
   entrance: "slide_left"
   entrance_duration: 0.6
   ```

5. **slide_right** - Slide in from left
   ```yaml
   entrance: "slide_right"
   entrance_duration: 0.6
   ```

6. **zoom** - Scale up from center
   ```yaml
   entrance: "zoom"
   entrance_duration: 0.5
   ```

7. **bounce** - Bounce in with overshoot
   ```yaml
   entrance: "bounce"
   entrance_duration: 0.8
   ```

8. **typewriter** - Letter-by-letter reveal
   ```yaml
   entrance: "typewriter"
   entrance_duration: 1.5  # Total duration for all letters
   ```

### Exit Animations

1. **fade_out** - Gradual opacity decrease
   ```yaml
   exit: "fade_out"
   exit_duration: 0.3
   ```

2. **slide_up** - Slide out upward
   ```yaml
   exit: "slide_up"
   exit_duration: 0.4
   ```

3. **slide_down** - Slide out downward
   ```yaml
   exit: "slide_down"
   exit_duration: 0.4
   ```

4. **zoom_out** - Scale down to center
   ```yaml
   exit: "zoom_out"
   exit_duration: 0.3
   ```

### Special Effects

- **pulse** - CTA button pulsing (currently disabled)
  - Would create a rhythmic scaling effect
  - Ideal for call-to-action slides

## Text Timing Configuration

Control when text appears and disappears:

```yaml
template_text_timing:
  fade_in_start: 0.5      # When to start fading in (seconds)
  fade_in_duration: 0.3   # How long the fade in takes
  fade_out_start: 3.0     # When to start fading out
  fade_out_duration: 0.3  # How long the fade out takes
```

## Usage Examples

### Basic Setup

```python
from src.text_animator import TextAnimator

# Create animator with config
animator = TextAnimator(animation_config)

# Animate text on a clip
animated_clip = animator.animate_text(
    text_clip,
    entrance="slide_up",
    exit="fade_out",
    entrance_duration=0.6,
    exit_duration=0.3
)
```

### Per-Slide Type Configuration

```yaml
# Different animations for different slide types
slide_animations:
  hook:
    entrance: "bounce"      # Eye-catching for hooks
    entrance_duration: 0.8
    
  intro:
    entrance: "fade"        # Gentle for introductions
    entrance_duration: 0.5
    
  quote:
    entrance: "typewriter"  # Dramatic for quotes
    entrance_duration: 2.0
    
  fact:
    entrance: "slide_left"  # Dynamic for facts
    entrance_duration: 0.6
    
  question:
    entrance: "zoom"        # Attention-grabbing
    entrance_duration: 0.5
    
  comparison:
    entrance: "slide_up"    # Clean and simple
    entrance_duration: 0.6
    
  conclusion:
    entrance: "fade"        # Smooth conclusion
    exit: "fade_out"
    exit_duration: 0.5
    
  cta:
    entrance: "bounce"      # Energetic call-to-action
    exit: "zoom_out"
```

## Integration with Slide Renderer

The slide renderer automatically applies animations based on:
1. Global animation settings
2. Per-slide type overrides
3. Individual slide overrides

Priority: Slide specific > Slide type > Global default

## Performance Tips

1. **Typewriter effect** is CPU intensive - use sparingly
2. **Bounce animations** work best with short text
3. **Fade animations** are most performant
4. Keep entrance durations under 1 second for better pacing

## Customization

### Creating Custom Animations

To add a new animation, extend the `TextAnimator` class:

```python
def apply_custom_animation(self, clip, duration):
    def custom_effect(t):
        # Your animation logic here
        return transform_at_time_t
    
    return clip.transform(custom_effect, duration)
```

### Easing Functions

The system uses various easing functions:
- Linear (typewriter)
- Ease-out cubic (slides)
- Ease-out back (bounce)
- Ease-in-out (zoom)

## Best Practices

1. **Match animation to content**
   - Energetic animations for hooks and CTAs
   - Subtle animations for quotes and facts
   
2. **Consider reading speed**
   - Longer text needs longer display time
   - Typewriter effect needs more duration
   
3. **Maintain consistency**
   - Use similar animations within a video
   - Don't mix too many animation styles
   
4. **Test on target platform**
   - Preview on mobile devices
   - Ensure text remains readable during animation

## Troubleshooting

### Animation not showing
- Check that animation name is spelled correctly
- Verify duration is greater than 0
- Ensure text clip has proper duration

### Choppy animations
- Reduce video resolution during preview
- Use simpler animations (fade, slide)
- Check system resources

### Text cut off during animation
- Adjust margins in text overlay config
- Use slide animations instead of zoom
- Check safe zone compliance

## Future Enhancements

Planned additions:
- Wave animation for text
- Character-by-character effects
- Custom easing curves
- Animation presets for genres
- Particle effects for CTAs