# Custom Instruction: Step 2 - Style Applicator

## Task Overview
Apply a selected graphic style to existing scene descriptions to create final AI-ready prompts using automated script.

## Input Parameters
1. **Book Title** or **Book Number**: (e.g., "Wuthering Heights" or "0037_wuthering_heights")
2. **Scene Set**: Which set to apply style to (`narrative`, `flexible`, `podcast`, `atmospheric`, or `emotional`)
3. **Style Name**: Graphic style to apply (e.g., `line-art-style` or `victorian-book-illustration-style`)
4. **Scene Number** (optional): Specific scene to process (e.g., `15` for scene_15.yaml)

## Process Steps

### 1. Locate Book Directory
- Find book directory by searching for book title/number in `books/` directories
- Identify book number and path (e.g., `books/0037_wuthering_heights/`)

### 2. Execute Merge Script
Use the automated merge script to process scenes:

```bash
python3 scripts/merge-scenes-with-style.py \
  books/[book_dir]/prompts/scenes/[scene_set]/ \
  books/[book_dir]/prompts/genimage/ \
  [style_name] \
  technical-specifications
```

The script automatically:
- Loads all scene YAML files from source directory
- Loads specified style from `config/prompt/graphics-styles/`
- Loads technical specifications from `config/prompt/technical-specifications.yaml`
- Merges scene descriptions (excluding `title`) with style and specifications
- Excludes metadata fields: `styleName`, `description`, `aiPrompts`
- Saves merged files to genimage directory

### 3. Verification Process
After script execution, verify three sample files for quality assurance:

#### Verify Scene 01 (First):
- Read and validate `books/[book_dir]/prompts/genimage/scene_01.yaml`
- Check YAML syntax is valid
- Confirm contains `sceneDescription` without `title` field
- Verify style fields are present (colorPalette, lineArt, lighting, etc.)
- Confirm technical specifications are included

#### Verify Scene 13 (Middle):
- Read and validate `books/[book_dir]/prompts/genimage/scene_13.yaml`
- Perform same checks as scene 01
- Ensure consistent merge quality

#### Verify Scene 25 (Last):
- Read and validate `books/[book_dir]/prompts/genimage/scene_25.yaml`
- Perform same checks as scene 01
- Confirm all scenes processed successfully

### 4. Output Location and Structure

#### Output directory:
```
books/[book_number]_[book_name]/prompts/genimage/
```

#### File naming:
- For all scenes: `scene_01.yaml`, `scene_02.yaml`, etc.
- For single scene: `scene_[number].yaml`

#### Example commands:
- All scenes: "Apply line-art-style to 'Wuthering Heights', narrative set"
- Single scene: "Apply watercolor-style to 'Wuthering Heights', narrative set, scene 15"

## Important Guidelines
- Use automated script for consistency and reliability
- Always perform three-point verification (first, middle, last)
- Report any YAML validation errors or missing fields
- Confirm total file count matches expected scenes

## Script Location
The merge script is located at: `scripts/merge-scenes-with-style.py`

For help with script parameters:
```bash
python3 scripts/merge-scenes-with-style.py --help
```