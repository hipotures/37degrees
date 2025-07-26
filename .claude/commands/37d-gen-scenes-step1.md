# Custom Instruction: Step 1 - Scene Descriptions Generator

## Task Overview
Generate 25 scene descriptions in JSON format based on book research.

## Input Parameters
1. **Book Title**: (e.g., "Wuthering Heights")
2. **Author**: (e.g., "Emily Brontë")
3. **Generator Type**: Choose one: `narrative`, `flexible`, or `podcast` (default: `podcast` if not specified)

## Process Steps

### 1. Validate Generator Type and Locate Book Directory
- If no generator type is provided, inform user: "No generator type specified. Using default: podcast"
- Validate generator type is one of: `narrative`, `flexible`, or `podcast`
- Read `docs/STRUCTURE.md` to understand project structure
- Find book directory by searching for book title/author in `books/` directories
- Identify book number and path (e.g., `books/0037_wuthering_heights/`)

### 2. Load Templates and Guidelines
- **Scene Structure**: 
  - Read and analyze `config/prompt/scene-description-template.json`
  - Study the JSON structure, field names, and data types
  - Understand all required and optional fields
  - Note any comments and length recommendations within the template
  
- **Generator File**: Read and analyze ONLY ONE generator file based on the chosen generator type:
  - If `narrative`: Read `config/prompt/scene-generator/narrative-prompt-generator.md`
  - If `flexible`: Read `config/prompt/scene-generator/flexible-prompt-generator.md`
  - If `podcast`: Read `config/prompt/scene-generator/podcast-image-prompt-generator.md`
  
  IMPORTANT: Read ONLY the file corresponding to the selected generator type. Do NOT read the other two generators.
  
  Study the selected generator thoroughly:
  - Understand its specific approach and guidelines
  - Analyze structure and pacing requirements
  - Note all instructions and constraints
  - Understand how it differs from other generators

### 3. Analyze Book Research
- Navigate to `books/[book_dir]/docs/` directory
- Read ONLY files matching pattern `37d-*_findings.md`
- These files contain all necessary book analysis and insights
- Extract themes, characters, historical context, and key discoveries from these findings files

### 4. Check Existing Files and Generate Scene Set

**Before generating**:
- Check if any scene files already exist in `/prompts/scenes/[generator_type]/`
- If `scene_01.json` exists, read ALL existing scene files to understand the story so far
- Find the first missing scene number (e.g., if scenes 1-15 exist, start from scene 16)
- If all 25 scenes already exist, STOP and inform user: "All 25 scenes already exist. Delete existing files if you want to regenerate."

**Generate missing scenes**:
- Apply the guidelines from the chosen generator file
- Ensure new scenes are consistent with any existing scenes
- Continue the story from where existing scenes left off
- Save only the missing scenes to `/prompts/scenes/[generator_type]/`

### 5. Output Structure
Create directories if they don't exist and save to:
```
books/[book_number]_[book_name]/prompts/scenes/[generator_type]/
  ├── scene_01.json
  ├── scene_02.json
  └── ... (25 files total)
```
Where [generator_type] matches the input parameter (narrative, flexible, or podcast).

**Important**: Create the directory structure if it doesn't exist:
- First create `prompts/` if missing
- Then create `prompts/scenes/` if missing  
- Finally create `prompts/scenes/[generator_type]/` if missing

**Critical Safety Rules**:
- NEVER delete or overwrite existing files
- Files should be checked in the earlier step (Step 4)
- Only create files that don't already exist
- At the end, report: "Created X new scenes (scenes Y-Z)" or "All scenes already existed"

### 6. JSON Format
Each file must match `scene-description-template.json` structure exactly.

## Important Guidelines
- Generate JSON data that will be used as prompts for AI image generation
- **LANGUAGE: All scene descriptions MUST be in English**
- **PERSPECTIVE: Write as a neutral observer who sees the scene for the first time**
  - Describe what is visually present, not story context
  - The observer knows geography/locations but NOT the characters or plot
  - Scene can be dramatic/emotional, but described through visual elements
  - Like a photographer who stumbled upon this moment without knowing the backstory
- **LOCATIONS: Each scene must include FULL location context**
  - Good: "Mountain monastery, Tibet" or "Desert oasis town, Morocco"
  - Bad: "Main hall of Dragon's Keep" (AI won't know where this is)
  - Always provide complete geographical/contextual information
  - Treat each scene as independent - AI won't see previous scenes
- **CHARACTERS: Describe as if viewer has never seen them before**
  - NO references to other scenes or aging ("older Anna", "Marco now grown")
  - EVERY character must have complete description:
    - age (exact for children, approximate for adults: 20s, 40s, 60s)
    - hair color and style
    - build (slender, stocky, athletic, muscular, frail)
    - height indication (tall, average, short)
  - NO character names unless describing what's written/visible
  - Good: "teenage boy, 16 years old, brown hair, athletic build"
  - Bad: "Elena, older and more mature" or just "Boy watching"
- **EMOTIONS: Use visual cues, not abstract descriptions**
  - Good: "furrowed brow, clenched fists, leaning forward"
  - Bad: "determination on face", "feeling anxious"
  - Avoid abstract concepts in atmosphere/details:
    - Bad: "dangerous diplomacy", "chess match of words", "veneer of civility"
    - Good: "man gripping crutch tightly", "sweat on foreheads", "hands near weapons"
  - Describe what camera would see, not what it means
- **CLOTHING: Be specific about period garments**
  - Good: "brown wool vest, white linen shirt, knee-length breeches"
  - Bad: "everyday clothes", "best outfit"
- **NO PROPRIETARY NAMES**: Replace with descriptive terms
  - Bad: "Castle Blackstone", "The Wanderer ship", "Isle of Mysteries"
  - Good: "medieval fortress", "merchant sailing vessel", "foggy island"
  - The "title" field must NOT contain character names
    - Good: "Negotiations at Dawn", "Library Window View"
    - Bad: "Sofia at the Gate", "Marcus's Discovery"
- **NO STORY REFERENCES**: Each scene stands alone
  - Bad: "return to where adventure began", "reminder of journey"
  - Good: "young man at tavern window", "treasure chest in corner"
  - Never mention what happened before or will happen after
- **SIMPLE VISUAL LANGUAGE**: Write like describing a photograph
  - Bad: "sunset painting ocean gold like remembered doubloons"
  - Good: "orange sunset reflecting on water surface"
  - Bad: "eternal sea continuing its rhythms"
  - Good: "waves breaking on shore"
- Follow the exact structure and field requirements from scene-description-template.json
- Do NOT define visual style (colors, artistic technique, rendering style) - only describe WHAT is in the scene
- The 25 scenes must be internally consistent and cohesive
- Follow narrative arc defined in the selected generator
- Focus only on the chosen approach without mixing styles
- Output must be valid JSON matching the template structure