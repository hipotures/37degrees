# Custom Instruction: Step 2 - Style Applicator

## Task Overview
Apply a selected graphic style to existing scene descriptions to create final AI-ready prompts.

## Input Parameters
1. **Book Title**: (e.g., "Wuthering Heights")
2. **Author**: (e.g., "Emily Brontë")
3. **Scene Set**: Which set to apply style to (`narrative`, `flexible`, or `podcast`)
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
- Validate all files are valid JSON

### 3. Merge Process
For each scene file:

#### A. Extract from Scene JSON:
- `sceneDescription` (entire section with all subsections)

#### B. Add from Style JSON all fields EXCEPT:
- `styleName` (metadata)
- `description` (metadata)

#### C. Remove from Scene JSON:
- `sceneNumber` (metadata)
- `sceneType` (metadata)
- `narrativeContext` (metadata)

### 4. Output Naming
- Single file: `[scene_name]_[style_name].json`
- Batch: Preserve original filenames in output directory

### 5. Output Structure and Examples

#### Default output location:
```
/tmp/[book_number]_[book_name]_[scene_set]_[style_name]/
  ├── scene_01_[style_name].json
  ├── scene_02_[style_name].json
  └── ... (25 files or just 1 if scene number specified)
```

#### Example commands:
- All scenes: "Apply line-art-style to 'Wuthering Heights' by Emily Brontë, narrative set"
- Single scene: "Apply watercolor-style to 'Wuthering Heights' by Emily Brontë, narrative set, scene 15"


## Important Guidelines
- Preserve exact field structure from both sources
- Ensure output is valid JSON
- Style fields override any conflicting scene fields
- Maintain all style-specific fields (e.g., `postProcessing`, `stylePrecedents`)
- Do not modify field values, only combine them

## Validation
Before saving, verify:
- Valid JSON syntax
- Contains `sceneDescription` from scene file
- Contains all style fields (except excluded ones)
- No forbidden metadata fields remain