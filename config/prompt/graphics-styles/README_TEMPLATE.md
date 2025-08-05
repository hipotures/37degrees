# Graphics Style Template Guide

## Template Usage

The `style-description.yaml` file contains a universal template for defining graphic styles.

### Key Principles:

1. **Describe STYLE, not CONTENT** - all fields should describe HOW something looks, not WHAT it represents
2. **Not all fields are required** - fill only those relevant to the specific style
3. **The `technicalSpecifications` field is ALWAYS required**

### Field Structure:

- **styleName**: Identifying name for the style
- **description**: Brief description of visual character
- **aiPrompts**: Keywords for AI generators (optional but recommended)
- **visualElements**: Main container for visual characteristics
  - **colorPalette**: Everything about colors - palette, contrast, saturation
  - **lineArt**: Line characteristics - thickness, style, texture
  - **composition**: Layout and arrangement (optional)
  - **lighting**: Lighting and shadows - direction, intensity, type
  - **rendering**: Execution technique - from sketch to photorealism
  - **perspective**: Point of view - isometric, frontal, etc.
  - **typography**: Typography integration (optional)
  - **mood**: Mood and emotions conveyed by the style
  - **symbolism**: Symbolic elements (optional)
- **postProcessing**: Additional effects like bloom, grain, vignette (optional)
- **stylePrecedents**: Artistic inspirations (optional)
- **useCases**: Best applications for the style (optional)
- **technicalSpecifications**: Technical requirements (REQUIRED)

### Example Values:

**colorPalette.saturation**: 
- "vibrant" - vivid, saturated colors
- "muted" - toned down, subdued
- "monochromatic" - shades of one color
- "desaturated" - almost grayscale

**lighting.type**:
- "flat" - no light gradients
- "dramatic" - strong light and shadow contrasts
- "soft diffused" - soft, scattered light
- "studio" - professional studio lighting

**rendering.detailLevel**:
- "minimal" - only essential elements
- "moderate" - moderate amount of detail
- "highly detailed" - rich in details
- "hyperrealistic" - extreme detail

**rendering.technique**:
- "digital painting" - painted digital artwork
- "vector art" - clean vector graphics
- "3D render" - three-dimensional rendering
- "watercolor simulation" - watercolor painting effect
- "oil painting" - traditional oil painting style

**mood.overall**:
- "playful" - fun and lighthearted
- "dramatic" - intense and serious
- "serene" - calm and peaceful
- "energetic" - dynamic and active
- "mysterious" - enigmatic and intriguing

### Creating a New Style:

1. Copy `style-description.yaml` to a new file
2. Name it descriptively, e.g., `vintage-poster-style.yaml`
3. Fill in the appropriate fields
4. Remove unused sections (except technicalSpecifications)
5. Maintain consistency in descriptions - use similar language
6. Ensure all descriptions focus on visual appearance, not content
7. Test with AI generators to verify the style works as intended

### Best Practices:

- Use specific, actionable descriptions
- Avoid subjective terms without clear meaning
- Include concrete examples where helpful
- Focus on measurable visual characteristics
- Consider how AI generators will interpret your descriptions
- Test your style definitions with actual generation tools

### Common Mistakes to Avoid:

- Describing content instead of style ("shows happy people" vs "bright colors, soft lighting")
- Using vague terms ("nice", "good", "beautiful")
- Missing technical specifications
- Inconsistent terminology within the same style
- Overly complex descriptions that confuse AI generators