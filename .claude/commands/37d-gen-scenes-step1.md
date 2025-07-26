# Custom Instruction: Step 1 - Scene Descriptions Generator

## Task Overview
Generate 25 scene descriptions in JSON format based on book research.

## Input Parameters
1. **Book Title**: (e.g., "Wuthering Heights")
2. **Author**: (e.g., "Emily Brontë")

## Process Steps

### 1. Locate Book Directory
- Read `docs/STRUCTURE.md` to understand project structure
- Find book directory by searching for book title/author in `books/` directories
- Identify book number and path (e.g., `books/0037_wuthering_heights/`)

### 2. Load Templates and Guidelines
- **Scene Structure**: 
  - Read and analyze `config/prompt/scene-generator/scene-description-template.json`
  - Study the JSON structure, field names, and data types
  - Understand all required and optional fields
  - Note any comments or documentation within the template
  
- **Generator Files**: Read, analyze and fully understand each generator:
  - **Narrative Generator** (`config/prompt/scene-generator/narrative-prompt-generator.md`):
    - Study the 3-act structure and scene distribution
    - Understand narrative arc and pacing guidelines
    - Analyze example prompts and their construction
    - Note all specific instructions and constraints
    
  - **Flexible Generator** (`config/prompt/scene-generator/flexible-prompt-generator.md`):
    - Understand the flexible approach to scene creation
    - Study how it differs from narrative approach
    - Analyze creative liberties and experimental elements
    - Note unique features and possibilities
    
  - **Podcast Generator** (`config/prompt/scene-generator/podcast-image-prompt-generator.md`):
    - Understand podcast-specific visual requirements
    - Study how to create images that support audio narrative
    - Analyze composition guidelines for podcast format
    - Note special considerations for this medium

### 3. Analyze Book Research
- Navigate to `books/[book_dir]/docs/` directory
- Read ONLY files matching pattern `37d-*_findings.md`
- These files contain all necessary book analysis and insights
- Extract themes, characters, historical context, and key discoveries from these findings files

### 4. Generate 3 Scene Sets
Create 25 scenes using each generator:

#### A. Narrative Set
- Use `narrative-prompt-generator.md` guidelines
- Save to `/prompts/scenes/narrative/`

#### B. Flexible Set  
- Use `flexible-prompt-generator.md` guidelines
- Save to `/prompts/scenes/flexible/`

#### C. Podcast Set
- Use `podcast-image-prompt-generator.md` guidelines
- Save to `/prompts/scenes/podcast/`

### 5. Output Structure
Save to:
```
books/[book_number]_[book_name]/prompts/scenes/
  ├── narrative/
  │   ├── scene_01.json
  │   └── ... (25 files)
  ├── flexible/
  │   └── ... (25 files)
  └── podcast/
      └── ... (25 files)
```

### 6. JSON Format
Each file must match `scene-description-template.json` structure exactly.

## Important Guidelines
- Generate JSON data that will be used as prompts for AI image generation
- Follow the exact structure and field requirements from scene-description-template.json
- Do NOT define visual style (colors, artistic technique, rendering style) - only describe WHAT is in the scene
- Each generator's 25 scenes must be internally consistent and cohesive
- Follow narrative arc defined in generators
- Each set tells same story differently
- Output must be valid JSON matching the template structure