# Automatic Style Selector for Scene-to-Image Generation

## Purpose
This file helps select appropriate visual styles based on book themes, era, and mood. To be used in Step 2 when applying styles to scene descriptions.

## Quick Reference Guide

### 🎯 Most Versatile Styles (work for many genres):
- **pencil-sketch-style** - intimate, raw, universal
- **watercolor-style** - emotional, atmospheric, timeless
- **line-art-style** - clean, clear, adaptable
- **oil-painting-style** - rich, dramatic, classic

### 🎨 Specialized Styles (for specific effects):
- **3d-clay-render-style** - whimsical, tactile, modern
- **anime-style** - expressive, dynamic, stylized
- **noir-pulp-fiction-style** - dramatic shadows, high contrast
- **glitch-art-style** - digital chaos, modern anxiety

## Style Selection Guide

### By Mood/Theme:

#### Light & Whimsical:
- **children-book-illustration-style** - playful narratives, fairy tales
- **watercolor-style** - lyrical, nostalgic, gentle stories
- **3d-clay-render-style** - cute, tactile, modern children's books
- **soft-glow-gradient-3d-style** - dreamy, magical realism
- **doodle-sketch-style** - casual, humorous, light-hearted

#### Dark & Dramatic:
- **noir-pulp-fiction-style** - crime, mystery, urban darkness
- **woodcut-linocut-style** - stark contrasts, dramatic narratives
- **expressionist-style** - psychological tension, inner turmoil
- **hatching-crosshatch-style** - gothic, detailed darkness
- **stipple-pointillism-style** - intricate shadows, patience

#### Epic & Grand:
- **oil-painting-style** - historical epics, grand narratives
- **mythological-epic-style** - fantasy, legends, heroic tales
- **concept-art-fantasy-style** - world-building, adventure
- **art-nouveau-style** - elegant, decorative, romantic epics

#### Modern & Contemporary:
- **comic-book-style** - action, contemporary adventure
- **anime-style** - modern fantasy, emotional drama
- **flat-design-style** - minimalist contemporary fiction
- **glitch-art-style** - digital age anxiety, cyberpunk
- **isometric-blue-line-urban-style** - urban planning, architecture stories

#### Artistic & Experimental:
- **surrealist-dreamlike-style** - magical realism, dreams
- **geometric-abstract-style** - modernist literature
- **textured-collage-style** - fragmented narratives
- **risograph-print-style** - indie, alternative stories
- **constructivist-propaganda-style** - political, revolutionary

### By Era:

#### Ancient/Classical:
- **mythological-epic-style** - Greek/Roman settings
- **woodcut-linocut-style** - medieval feel

#### Victorian (1837-1901):
- **victorian-book-illustration-style** - period authentic
- **hatching-crosshatch-style** - traditional engraving look
- **pencil-sketch-style** - naturalist drawings

#### Early 20th Century (1900-1950):
- **art-nouveau-style** - 1890s-1910s
- **constructivist-propaganda-style** - 1920s-1930s Soviet
- **noir-pulp-fiction-style** - 1930s-1950s
- **expressionist-style** - 1910s-1930s
- **vintage-travel-poster-style** - 1920s-1950s

#### Mid-Late 20th Century:
- **comic-book-style** - 1960s onward
- **retro-pixel-art-style** - 1980s-1990s
- **risograph-print-style** - 1980s-1990s aesthetic

#### Contemporary (2000+):
- **anime-style** - modern Japanese influence
- **flat-design-style** - digital age minimalism
- **glitch-art-style** - post-internet era
- **3d-clay-render-style** - modern 3D aesthetic
- **soft-glow-gradient-3d-style** - contemporary digital art

### By Genre:

#### Fantasy/Sci-Fi:
- **concept-art-fantasy-style** - detailed world-building
- **mythological-epic-style** - classical fantasy
- **anime-style** - modern fantasy/sci-fi
- **surrealist-dreamlike-style** - weird fiction
- **glitch-art-style** - cyberpunk
- **photorealistic-glass-3d-render-style** - hard sci-fi

#### Mystery/Thriller:
- **noir-pulp-fiction-style** - classic detective
- **hatching-crosshatch-style** - gothic mystery
- **expressionist-style** - psychological thriller
- **comic-book-style** - action thriller

#### Romance:
- **watercolor-style** - gentle romance
- **art-nouveau-style** - period romance
- **soft-glow-gradient-3d-style** - contemporary romance
- **anime-style** - modern romance

#### Literary Fiction:
- **pencil-sketch-style** - character studies
- **oil-painting-style** - epic literary works
- **geometric-abstract-style** - experimental fiction
- **textured-collage-style** - postmodern narratives

#### Children's Literature:
- **children-book-illustration-style** - traditional
- **3d-clay-render-style** - modern playful
- **watercolor-style** - gentle stories
- **doodle-sketch-style** - fun, casual

#### Historical Fiction:
- **victorian-book-illustration-style** - 19th century
- **oil-painting-style** - any historical period
- **vintage-travel-poster-style** - early-mid 20th century
- **constructivist-propaganda-style** - revolutionary periods

#### Nature/Environmental:
- **eco-botanical-style** - nature writing
- **watercolor-style** - natural beauty
- **stipple-pointillism-style** - detailed nature studies

### Special Considerations:

#### For Podcast Thumbnails:
**High Contrast Needed** (visible at small size):
- line-art-style
- comic-book-style
- flat-design-style
- noir-pulp-fiction-style
- woodcut-linocut-style

**Avoid for Thumbnails** (too detailed):
- stipple-pointillism-style
- hatching-crosshatch-style (unless simplified)
- textured-collage-style (unless bold)

#### For Series Consistency:
**Most Flexible Across Scenes**:
- pencil-sketch-style
- watercolor-style
- line-art-style
- oil-painting-style

**Most Restrictive** (harder to maintain):
- retro-pixel-art-style
- constructivist-propaganda-style
- glitch-art-style

## Usage Instructions:

1. **Analyze the book's primary characteristics**:
   - Core mood/atmosphere
   - Historical period
   - Genre conventions
   - Target audience

2. **Consider technical requirements**:
   - Podcast thumbnail visibility
   - Consistency across 25 scenes
   - AI generation reliability

3. **Select primary style**:
   - Choose one style that best matches
   - Consider fallback options
   - Test with 2-3 scenes first

4. **Apply consistently**:
   - Use the selected style's JSON file
   - Maintain style across all 25 scenes
   - Adjust prompts if needed for consistency

## Style Combination Notes:

Some styles can be effectively combined:
- **pencil-sketch-style** + specific era details
- **watercolor-style** + genre elements
- **line-art-style** + mood modifiers

Avoid combining:
- Multiple 3D styles
- Conflicting era styles
- Opposing mood styles

## Final Tips:

- **When in doubt**: pencil-sketch-style or watercolor-style are safest
- **For maximum impact**: match style to book's core emotion
- **For series**: test consistency before committing
- **For AI reliability**: simpler styles generate more consistently