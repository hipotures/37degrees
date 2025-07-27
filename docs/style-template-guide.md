# Style Template Guide for LLM

**Important**: All style parameters work together to create a cohesive visual aesthetic. Maintaining consistency across all elements is more important than perfect adherence to any single parameter.

## styleName
The identifying name of the visual style being defined - this helps categorize and reference the specific aesthetic approach.

## description
A brief explanation of the style's character and its typical applications - provides context for when and how this style should be used.

## aiPrompts
Optional section containing specific prompts to guide AI image generators in achieving the desired style. **These prompts have high priority in defining the visual output.**

* **basePrompt** - Core keywords that define the fundamental characteristics of this style
* **negativePrompt** - Elements to avoid when generating images in this style - helps prevent unwanted features
* **styleKeywords** - Additional descriptive terms that reinforce the style's aesthetic qualities

## colorPalette
Defines the color scheme and how colors should be used to achieve the style's characteristic look. **Color choices strongly influence the mood and period feel of the final image.**

* **primary** - Main colors that dominate the style - can be specified as hex codes, RGB values, or descriptive terms
* **secondary** - Accent colors that complement the primary palette
* **background** - The predominant background color or type that creates the base canvas
* **usageNotes** - Guidance on how to apply the color palette effectively
* **saturation** - The intensity of colors - determines if colors are bold and vibrant or subdued and muted
* **contrast** - The level of difference between light and dark elements - affects visual impact and readability

## lineArt
Characteristics of lines and strokes that define the drawing style. **Line work significantly affects readability and artistic character, especially important for styles like comics or sketches.**

* **style** - The type of line work that characterizes this aesthetic
* **weight** - The thickness of lines used throughout the image
* **color** - The color of outlines and line work
* **texture** - The quality and feel of the lines - whether smooth, rough, or organic
* **edgeTreatment** - How edges and boundaries are handled in the style

## lighting
How light and illumination are handled to create the style's distinctive atmosphere. **Lighting dramatically affects the emotional impact and three-dimensionality of the scene.**

* **type** - The overall lighting approach that defines the style's mood
* **direction** - Where light sources come from in the composition
* **intensity** - How strong or subtle the lighting appears
* **shadows** - How shadows are rendered to complement the lighting
  * **style** - The quality of shadow edges and transitions
  * **color** - The hue used for shadowed areas
  * **opacity** - How transparent or opaque shadows appear
* **highlights** - How bright spots and reflections are rendered

## rendering
The technical approach to creating the visual output. **The rendering technique fundamentally determines whether the style appears painted, drawn, photographic, or digitally created.**

* **technique** - The primary method used to create the imagery
* **texture** - The surface quality applied to elements in the style
* **detailLevel** - How much fine detail is included versus simplified forms
* **finish** - The final surface appearance of the rendered image

## perspective
The viewing angle and spatial representation used in the style - affects how three-dimensional space is depicted. **Consistent perspective across all scenes helps maintain visual coherence in a series.**

## mood
The emotional and atmospheric qualities that the style conveys. **These should complement the scene's content while maintaining the style's characteristic aesthetic.**

* **overall** - The general feeling evoked by the style
* **emotion** - The primary emotional response the style aims to create
* **tempo** - The visual energy level - whether calm and static or dynamic and active
* **keywords** - Descriptive terms that capture the style's atmospheric qualities

## postProcessing
Optional effects applied after the main image generation to enhance the style.

* **effects** - List of visual effects that enhance the final appearance
* **filters** - Color grading or tonal adjustments applied to the entire image
* **adjustments** - Additional fine-tuning parameters for the final look

## stylePrecedents
Optional list of artistic styles or specific artists that inspire this visual approach - helps establish aesthetic references.

**Note**: Not all fields need to be filled for every style. Some styles may emphasize certain aspects (like bold line art) while having minimal requirements for others (like complex lighting). The key is creating a coherent visual language that serves the style's purpose.