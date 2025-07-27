# Technical Specifications Guide for LLM

## technicalSpecifications
The root container that defines the required technical parameters for the generated image to ensure it meets the podcast visual requirements.

## resolution
This section specifies the exact dimensions and proportions the generated image must have.

* **aspectRatio** - The width-to-height proportion of the image - "9:16" means the image should be 9 units wide for every 16 units tall, creating a vertical format suitable for mobile viewing. **Maintaining this aspect ratio is more important than achieving the highest resolution**
* **minWidth** - The minimum horizontal dimension in pixels - ensures the image has sufficient resolution for clear display
* **minHeight** - The minimum vertical dimension in pixels - ensures the image maintains quality when displayed on high-resolution screens
* **unit** - Specifies that the width and height values are measured in pixels

## orientation
Defines that the image must be created in portrait/vertical format - this is optimized for podcast thumbnails and mobile device displays where users typically hold phones vertically.