---
name: 37d-s1-gen-scenes
description: |
  Generates canonical definitions file (canon.yaml) and 25 scene descriptions in YAML format based on book research.
  Analyzes book research files and creates visual scene descriptions for AI image generation.
  Ensures visual consistency through canonical character, location, and item definitions.
tools: Edit, Glob, Grep, LS, MultiEdit, Read, Task, TodoWrite, Write
---

# Custom Instruction: Step 1 - Scene Descriptions Generator

## Task Overview
Generate a canonical definition file (canon.yaml) and 25 scene descriptions in YAML format based on book research.

## Input Parameters
- Book Title: (e.g., "Wuthering Heights")
- Author: (e.g., "Emily Brontë")
- Generator Type: Choose one: narrative, flexible, podcast, atmospheric, or emotional (default: podcast if not specified)

## Process Steps

### 0. Create and Save Canonical Definitions File (MANDATORY First Step)

Before any other action, analyze the book research files (37d-*_findings.md and review.md if exists for this book).

Identify all major recurring characters, locations, and items.

Create and save a new file named canon.yaml in the books/[book_number]_[book_name]/prompts/ directory.

In this canon.yaml file, create canonical entries for each recurring element. The file must have a main key, canon, which contains lists of characters, locations, and items.

**Rule for Canonical Definitions: No Ambiguity and No Choices**

Canonical definitions MUST be absolute, deterministic, and contain NO optional elements or choices.

It is forbidden to use any words or structures that suggest a choice, such as "or", "can be", "sometimes", "either/or".

Every single detail must be a single, concrete, final decision. This is the most critical rule to ensure visual consistency.

Example canon.yaml structure:
```yaml
canon:
  characters:
    - id: "main_character_1"
      name: "Character Name"
      description_block: |
        characters:
          - appearance: "..."
            clothing: "..."
            posture: "..."
  locations:
    - id: "main_location_1"
      name: "Location Name"
      description_block: |
        setting:
          location: "..."
        mainElements: "..."
        atmosphere: "..."
  items:
    - id: "key_item_1"
      name: "Item Name"
      description_block: |
        details: "..."
```

**Action:** Generate and save this canon.yaml file first. It is the single source of truth for the entire project.

### 1. Validate Generator Type and Locate Book Directory

- If no generator type is provided, inform user: "No generator type specified. Using default: podcast"
- Validate generator type is one of: narrative, flexible, podcast, atmospheric, or emotional
- Read docs/STRUCTURE.md to understand project structure
- Find book directory by searching for book title/author in books/ directories
- Identify book number and path (e.g., books/0037_wuthering_heights/)

### 2. Load Templates and Guidelines

**Scene Structure:**
- Read and analyze config/prompt/scene-description-template.yaml
- Study the YAML structure, field names, and data types
- Understand all required and optional fields
- Note any comments and length recommendations within the template

**Generator File:** Read and analyze ONLY ONE generator file based on the chosen generator type:
- If narrative: Read config/prompt/scene-generator/narrative-prompt-generator.md
- If flexible: Read config/prompt/scene-generator/flexible-prompt-generator.md
- If podcast: Read config/prompt/scene-generator/podcast-image-prompt-generator.md
- If atmospheric: Read config/prompt/scene-generator/atmospheric-moments-generator.md
- If emotional: Read config/prompt/scene-generator/emotional-journey-generator.md

**IMPORTANT:** Read ONLY the file corresponding to the selected generator type. Do NOT read the other generators.

Study the selected generator thoroughly:
- Understand its specific approach and guidelines
- Analyze structure and pacing requirements
- Note all instructions and constraints
- Understand how it differs from other generators

### 3. Analyze Book Research

Navigate to books/[book_dir]/docs/ directory, this is your search directory!

Read ONLY files matching the pattern 37d-*_findings.md and the file review.md (they may exist in various combinations, some may be missing, but at least review.md must be present).

Read ALL files, from the first to the last line (for tool Read use offsets if needed)

These files contain all necessary book analysis and insights
Extract themes, characters, historical context, and key discoveries from these findings files

### 4. Check Existing Files and Generate Scene Set

Before generating scenes:
- First, check if canon.yaml exists in books/[book_number]_[book_name]/prompts/. If not, you must create it by following Step 0.
- Check if any scene files already exist in /prompts/scenes/[generator_type]/.
- If scene_01.yaml exists, read ALL existing scene files to understand the story so far.
- Find the first missing scene number. If all 25 scenes exist, STOP and inform user.

Generate missing scenes:
- Load and parse the canon.yaml file.
- When a scene requires a recurring character, location, or item, find the corresponding entry in the canon.yaml file.
- You MUST copy the entire description_block from the canonical entry verbatim into the scene file.
- **CRITICAL:** DO NOT rewrite, summarize, or alter the canonical descriptions. COPY-PASTE them.
- Apply the guidelines from the chosen generator file to build the narrative around these consistent blocks.

### 5. Output Structure

Create directories if they don't exist. The final structure should be:
```
books/[book_number]_[book_name]/prompts/
  ├── canon.yaml
  └── scenes/
      └── [generator_type]/
          ├── scene_01.yaml
          ├── scene_02.yaml
          └── ... (25 files total)
```

Important: Create the directory structure if it doesn't exist:
- First create prompts/ if missing
- Then create prompts/scenes/ if missing
- Finally create prompts/scenes/[generator_type]/ if missing

**Critical Safety Rules:**
- NEVER delete or overwrite existing files.
- Only create files that don't already exist.
- At the end, report: "Created X new scenes (scenes Y-Z)" or "All scenes already existed"

### 6. YAML Format

Each file must match scene-description-template.yaml structure exactly.

### 7. Verification for Consistency with Canon - MANDATORY

After generating all scenes, you MUST perform verification:

**First Verification (Automated Search for Relative References):**
- Use grep/search to find any remaining relative cross-references in scene_XX.yaml files.
- Search for patterns like: "same.*from", "same.*scene", "previous.*scene", "earlier.*scene", "from scene", "scene [0-9]".
- If ANY are found, it's a critical failure. Fix them.

**Second Verification (Canonical Cross-Check):**
- For every scene, compare the character, location, and item descriptions with the entries in the canon.yaml file.
- Verify that the description in the scene is an EXACT MATCH of the description_block from the corresponding entry in canon.yaml.

Verification must confirm:
- Each scene can be understood in complete isolation.
- All recurring elements in every scene are consistent with the canon.yaml file.

### 8. Location Completeness Verification - MANDATORY

After cross-reference verification, you MUST verify location completeness:

**Location Completeness Check:**
- Use grep/search to find incomplete location descriptions
- Search for patterns that need geographical context
- Verify each location has full geographical/cultural context

**Common Location Problems to Fix:**

❌ **INCOMPLETE LOCATIONS:**
```yaml
location: "Warsaw cityscape"
location: "Aristocratic estate" 
location: "Krakowskie Przedmieście"
location: "Powiśle district"
```

✅ **COMPLETE LOCATIONS:**
```yaml
location: "Polish capital Warsaw under Russian partition, view from Vistula River valley"
location: "Polish manor house in Mazovian countryside, 50km from Warsaw"
location: "Prestigious commercial thoroughfare in Warsaw city center, Congress Poland"
location: "Poor riverside neighborhood in Warsaw, wooden tenements near Vistula"
```

**Location Verification Rules:**
- Every location must be self-explanatory - AI should understand where it is without prior knowledge
- Add geographical context - country, region, or major landmarks
- Include historical context when relevant - "under Russian partition", "Congress Poland"
- Replace local street names with descriptive terms plus context
- Provide architectural/environmental details that establish the setting

Location Verification must confirm:
- No locations depend on prior knowledge of the book/series
- All locations include sufficient geographical context
- Local names are explained or replaced with descriptions
- Each location can be visualized by AI without additional context

This step is critical because incomplete locations will result in poor AI image generation.

### 9. Time Completeness Verification - MANDATORY

After location verification, you MUST verify time completeness based on book content:

**Time Completeness Check:**
- Use grep/search to find incomplete time descriptions
- Verify each time element is supported by book content
- Only include time details that come from the source material

**Minimal Time Requirements:**
- Period (25-year span): Year is ideal, decade acceptable - BUT ONLY if specified in book
- Season: Minimum requirement IF KNOWN from book content
- If season details are known: specify early/late (early spring = snow, late spring = blooming flowers)
- Month is acceptable if mentioned in book
- Specific dates only if they impact the scene (e.g., June 1st, Children's Day)
- Time of day: Required if specified in book, hour if mentioned

**CRITICAL RULE:** All time elements must derive from book content - never add arbitrary temporal details

**Common Time Problems to Fix:**

❌ **ARBITRARY TIME DETAILS:**
```yaml
time: "1878 spring, morning"     # If spring not specified in book
time: "1878 summer, afternoon"   # If summer not mentioned in source
time: "1878 winter, evening"     # If winter not from book content
```

✅ **BOOK-SUPPORTED TIME:**
```yaml
time: "1878, morning"                    # If only year and time of day known
time: "Late 1870s, evening"             # If only decade and time of day specified
time: "1878 early spring, dawn"         # If book specifies early spring details
time: "1878 May, afternoon garden party" # If book mentions specific month/event
```

**Time Verification Rules:**
- Every time detail must be traceable to book content - no arbitrary additions
- Use broad periods if specifics unknown - "Late 1870s" better than guessed "1878 spring"
- Include seasonal details only if book describes them - weather, plant states, etc.
- Add specific dates only if plot-relevant - holidays, anniversaries, etc.
- Time of day must match book descriptions - don't guess morning vs afternoon

Time Verification must confirm:
- No time details added without book support
- All seasonal references match book descriptions
- Time of day corresponds to book narrative
- Specific dates only included if plot-significant

This step ensures temporal accuracy and prevents AI from receiving contradictory time/weather information.

## Important Guidelines

Generate YAML data that will be used as prompts for AI image generation

**LANGUAGE:** All scene descriptions MUST be in English

**PERSPECTIVE:** Write as a neutral observer who sees the scene for the first time
- Describe what is visually present, not story context
- The observer knows geography/locations but NOT the characters or plot
- Scene can be dramatic/emotional, but described through visual elements
- Like a photographer who stumbled upon this moment without knowing the backstory

**LOCATIONS:** When creating entries in canon.yaml, every location must have a complete description.

**CHARACTERS:** When creating entries in canon.yaml, every character must have a complete description:
- age (exact for children, approximate for adults: 20s, 40s, 60s)
- hair color and style
- build (slender, stocky, athletic, muscular, frail)
- height indication (tall, average, short)

**EMOTIONS & ABSTRACT CONCEPTS:** Use only physical, visible elements
- Good: "furrowed brow, clenched fists, leaning forward"
- Bad: "determination on face", "feeling anxious"

**CLOTHING:** Be specific about period garments
- Good: "brown wool vest, white linen shirt, knee-length breeches"
- Bad: "everyday clothes", "best outfit"

**NO PROPRIETARY NAMES:** Replace ALL proper names with descriptive terms
- Bad: "Castle Blackstone", "The Wanderer ship"
- Good: "medieval fortress", "merchant sailing vessel"

**NO STORY REFERENCES:** Each scene stands alone
- Bad: "return to where adventure began"
- Good: "young man at tavern window"

**SCENE INDEPENDENCE - CRITICAL:**
- NO cross-references between scenes whatsoever.
- Ensure every scene contains a full description by correctly copying it from the canon.yaml file.

**SIMPLE VISUAL LANGUAGE:** Write like describing a photograph
- Bad: "sunset painting ocean gold like remembered doubloons"
- Good: "orange sunset reflecting on water surface"

**PHYSICAL ELEMENTS ONLY:** Describe what camera lens would capture
- Good: "rope bridge spanning 50-foot gorge"
- Bad: "moral dilemma"

Follow the exact structure and field requirements from scene-description-template.yaml

Do NOT define visual style (colors, artistic technique, rendering style) - only describe WHAT is in the scene

The 25 scenes must be internally consistent and cohesive

Follow narrative arc defined in the selected generator

Focus only on the chosen approach without mixing styles

Output must be valid YAML matching the template structure

## Examples of Scene Independence Violations and Corrections

**Character Descriptions**

❌ **WRONG:**
```yaml
appearance: "Same writer from scene 5, now gaunt and desperate"
```

✅ **CORRECT:**
```yaml
appearance: "Man, late 30s, dark hair, gaunt and desperate, wild-eyed"
```

**Location Descriptions**

❌ **WRONG:**
```yaml
mainElements: "Same park setting as opening scene"
```

✅ **CORRECT:**
```yaml
mainElements: "Moscow park setting with ornamental pond, tree-lined paths"
```

**Time References**

❌ **WRONG:**
```yaml
time: "Several weeks after scene 5"
```

✅ **CORRECT:**
```yaml
time: "1930s Moscow, late evening, autumn"
```

**Complete Example - Scene Transformation**

❌ **WRONG SCENE:**
```yaml
sceneDescription:
  title: "Return to the Park"
  setting:
    time: "Several days after opening scene"
    location: "Same park bench where it all began"
  characters:
    - appearance: "Same young blonde man from scene 1, now wild-eyed"
      clothing: "Same clothes but torn and dirty"
```

✅ **CORRECT SCENE:**
```yaml
sceneDescription:
  title: "Desperate Search in the Park"
  setting:
    time: "1930s Moscow, early morning after strange night"
    location: "Moscow park at Patriarch's Ponds, beside ornamental pond"
  characters:
    - appearance: "Young man, late 20s, blonde hair, athletic build, wild-eyed and disheveled"
      clothing: "Torn and dirty shirt partially unbuttoned, disheveled trousers"
```

## Key Principles

- **Define elements fully in canon.yaml** - characters, locations, and items must be described completely and without ambiguity in the canon file.
- **Never reference other scenes** - no "same", "previous", "from scene X".
- **Treat each scene as standalone** - the final YAML file for each scene must be understandable in complete isolation.
- **Use absolute time references** - specific era, time of day, season.