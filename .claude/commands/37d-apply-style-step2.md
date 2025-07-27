# Custom Instruction: Step 2 - Style Applicator

## Task Overview
Apply a selected graphic style to existing scene descriptions to create final AI-ready prompts.

## Input Parameters
1. **Book Title**: (e.g., "Wuthering Heights")
2. **Author**: (e.g., "Emily Brontë")
3. **Scene Set**: Which set to apply style to (`narrative`, `flexible`, `podcast`, `atmospheric`, or `emotional`)
4. **Style Name**: Graphic style to apply (e.g., `line-art-style`)
5. **Scene Number** (optional): Specific scene to process (e.g., `15` for scene_15.json)

## Process Steps

### 1. Locate Book Directory
- Read `docs/STRUCTURE.md` to understand project structure
- Find book directory by searching for book title/author in `books/` directories
- Identify book number and path (e.g., `books/0037_wuthering_heights/`)

### 2. Load Resources
- **Scene(s)**: 
  - If scene number provided: Load `books/[book_dir]/prompts/scenes/[scene_set]/scene_[number].json`
  - Otherwise: Load all 25 scenes from `books/[book_dir]/prompts/scenes/[scene_set]/`
- **Style**: Load style from `config/prompt/graphics-styles/[style_name].json`
- **Technical Specifications**: Load from `config/prompt/technical-specifications.json`
- Validate all files are valid JSON

### 3. Merge Process
For each scene file:

#### A. Extract from Scene JSON:
- `sceneDescription` (entire section with all subsections EXCEPT `title`)
- Exclude `title` field from sceneDescription (not a visual element)

#### B. Add from Style JSON all fields EXCEPT:
- `styleName` (metadata)
- `description` (metadata)
- `aiPrompts` (redundant prompt information)

#### C. Add Technical Specifications:
- Include all fields from `technical-specifications.json`
- These provide standard resolution and format requirements

### 4. Output Location and Structure

#### Output directory:
Save all generated files to:
```
books/[book_number]_[book_name]/prompts/genimage/
```

**Important**: Create the `genimage/` directory if it doesn't exist.

#### File naming:
- For all scenes: `scene_01.json`, `scene_02.json`, etc. (maintain original naming)
- For single scene: `scene_[number].json` (e.g., `scene_15.json`)

#### Example output structure:
```
books/0037_wuthering_heights/prompts/genimage/
  ├── scene_01.json  # Merged scene 1 + selected style
  ├── scene_02.json  # Merged scene 2 + selected style
  └── ... (25 files total, or just 1 if single scene specified)
```

#### Example commands:
- All scenes: "Apply line-art-style to 'Wuthering Heights' by Emily Brontë, narrative set"
- Single scene: "Apply watercolor-style to 'Wuthering Heights' by Emily Brontë, narrative set, scene 15"


## Important Guidelines
- Preserve exact field structure from both sources
- Ensure output is valid JSON
- Style fields override any conflicting scene fields
- Do not modify field values, only combine them

## Validation
Before saving, verify:
- Valid JSON syntax
- Contains `sceneDescription` from scene file
- Contains all style fields (except excluded metadata)
- Merged structure follows expected format