---
name: 37d-m1-generate-scenes
description: |
  Generates canonical definitions file (canon.yaml) and scene descriptions in YAML format based on media research.
  Creates TODOIT list with hierarchical subtask structure for each scene processing stage.
  Analyzes media research files and creates visual scene descriptions for AI image generation.
  Number of scenes is determined by scene_count in media.yaml.
execution_order: 1
min_tasks: 3
max_tasks: 8
todo_list: true
---
# Custom Instruction: Step 1 - Scene Descriptions Generator for Media (Subtasks Version)

**MANDATORY CONTENT RESTRICTIONS: You MUST strictly follow all content guidelines in [config/prompt/content-restrictions-guidelines.md](../../../config/prompt/content-restrictions-guidelines.md). This includes avoiding ALL prohibited content categories, red flag terms, and ensuring all scene descriptions are appropriate for general audiences. When in doubt, always choose safer alternatives.**

## Task Overview
Generate a canonical definition file (canon.yaml) and scene descriptions in YAML format based on media research.
Create TODOIT list with hierarchical subtask structure for systematic processing.
Number of scenes is determined by scene_count field in media.yaml.

## Input Parameters
- MEDIA_FOLDER (e.g. m00001_atomic_bomb, schema like mNNNN_lower_case_title, then this is a media folder media/mNNNN_xxxx, eg. media/m00001_atomic_bomb)

## Process Steps

### 0. Create and Save Canonical Definitions File (MANDATORY First Step)

Before any other action, analyze the media research file (research.md if exists for this media).

Identify all major recurring characters, locations, and items.

Create and save a new file named canon.yaml in the media/[MEDIA_FOLDER]/prompts/ directory.

In this canon.yaml file, create canonical entries for each recurring element. The file must have a main key, canon, which contains lists of characters, locations, and items.

**Rule for Canonical Definitions: No Ambiguity and No Choices**

Canonical definitions MUST be absolute, deterministic, and contain NO optional elements or choices.

It is forbidden to use any words or structures that suggest a choice, such as "or", "can be", "sometimes", "either/or".

Every single detail must be a single, concrete, final decision. This is the most critical rule to ensure visual consistency.

**CRITICAL RULE FOR MEDIA - NO PERSONAL DATA:**
- NEVER use real names (first names or surnames) in canon.yaml
- Use ONLY initials for character IDs and names (e.g., for Albert Anastasia use "character_AA")
- If multiple characters have same initials, add numbers: "character_VG1", "character_VG2"
- This restriction applies ONLY to names - ALL other details must be included:
  - Age, appearance, clothing, build, height - all must be specified
  - Locations can use real place names (Park Sheraton Hotel, Manhattan, etc.)
  - Objects can have their real names
- AI image generators WILL FAIL if real names are included
- IMPORTANT: In actual YAML files, NEVER include real names even in comments!

Example canon.yaml structure for media (CORRECT - no real names anywhere):
```yaml
canon:
  characters:
    - id: "character_JRO"
      name: "Character JRO"
      description_block: |
        characters:
          - appearance: "Caucasian man, 40s, slender build, intense dark eyes, receding hairline"
            clothing: "1940s white lab coat over dress shirt, or casual suit with tie"
            posture: "Thoughtful, often with hands in pockets or adjusting glasses"
    - id: "character_AE"
      name: "Character AE"
      description_block: |
        characters:
          - appearance: "Caucasian man, 60s, white hair, mustache, thoughtful expression"
            clothing: "Early 20th century suit, slightly rumpled, no tie"
            posture: "Relaxed, often with hands behind head or gesturing"
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

### 1. Read Media Configuration and Extract Settings

#### Locate Media Directory
  - ALWAYS use specific media path, NOT media/ directory
  - Correct: LS(media/m00001_atomic_bomb)
  - WRONG: LS(media)
  - if not found, stop

#### Read Media YAML Configuration
- Read media/[MEDIA_FOLDER]/media.yaml
- Extract the following critical fields:
  - scene_count: Number of scenes to generate (e.g., 10)
  - scene_generator: Generator type (e.g., "narrative" (narrative-prompt-generator))
  - graphics_style: Style to apply (e.g., "feature-animation-2d-classical")

These values will be used throughout the generation process.

### 2. Load Templates and Guidelines

**Scene Structure:**
- Read and analyze config/prompt/scene-description-template.yaml
- Study the YAML structure, field names, and data types
- Understand all required and optional fields
- Note any comments and length recommendations within the template

**Generator File:** Read and analyze the specified generator file:
- Read config/prompt/scene-generator/[scene_generator].md where [scene_generator] is the value from media.yaml
- Example: if scene_generator is "narrative", read config/prompt/scene-generator/narrative.md

**IMPORTANT:** Read ONLY the file corresponding to the selected generator type. Do NOT read the other generators.

Study the selected generator thoroughly:
- Understand its specific approach and guidelines
- Analyze structure and pacing requirements
- Note all instructions and constraints
- Understand how it differs from other generators

### 3. Analyze Media Research
pwd - should be inside 37degrees/ directory
Execute these commands:
  1. Read(file_path="media/[MEDIA_FOLDER]/docs/research.md", offset=1, limit=300)
  2. If you read 300 lines in previous call, execute also:
       Read(file_path="media/[MEDIA_FOLDER]/docs/research.md", offset=301, limit=300)
  3. If you read 300 lines in previous call, execute also:
       Read(file_path="media/[MEDIA_FOLDER]/docs/research.md", offset=601, limit=300)
  4. If research.md file DOES NOT EXIST:
     a) Run media-researcher agent with parameter MEDIA_FOLDER=[MEDIA_FOLDER] using Task tool
     b) Wait for agent completion
     c) Check if research.md was created
     d) If research.md still doesn't exist, stop execution and report error

These files contain all necessary media analysis and insights
Extract themes, characters, historical context, and key discoveries from file

**IMPORTANT:** The research.md file should already contain comprehensive information. If you encounter minor uncertainties, you can use WebSearch and WebFetch tools to verify specific details like:
- Exact historical dates and timelines
- Specific location details
- Character names and roles verification

### 4. Check Existing Files and Generate Scene Set

Before generating scenes:
- First, check if canon.yaml exists in media/[MEDIA_FOLDER]/prompts/. If not, you must create it by following Step 0.
- Check if any scene files already exist in prompts/scenes/[scene_generator]/
- If scene_0001.yaml exists, read ALL existing scene files to understand the narrative so far.
- Find the first missing scene number. If all scenes (based on scene_count from media.yaml) exist, STOP and inform user.

Generate missing scenes:
- Load and parse the canon.yaml file.
- When a scene requires a recurring character, location, or item, find the corresponding entry in the canon.yaml file.
- You MUST copy the entire description_block from the canonical entry verbatim into the scene file.
- **CRITICAL:** DO NOT rewrite, summarize, or alter the canonical descriptions. COPY-PASTE them.
- Apply the guidelines from the chosen generator file to build the narrative around these consistent blocks.
- Generate EXACTLY the number of scenes specified in scene_count from media.yaml (not always 25!)

### 5. Mark Scene Generation Subtasks as Completed:
// Mark all scene_gen subtasks as completed since scenes are already generated
Uruchom Bash, polecenie z parametrem
```
./scripts/internal/37d-m1-01.sh [MEDIA_FOLDER]
```

### 6. Output Structure

Create directories if they don't exist. The final structure should be:
```
media/[MEDIA_FOLDER]/prompts/
  ├── canon.yaml
  └── scenes/
      └── [scene_generator]/
          ├── scene_0001.yaml
          ├── scene_0002.yaml
          └── ... (total based on scene_count from media.yaml)
```

Important: Create the directory structure if it doesn't exist:
- First create prompts/ if missing
- Then create prompts/scenes/ if missing
- Finally create prompts/scenes/[scene_generator]/ if missing

**Critical Safety Rules:**
- NEVER delete or overwrite existing files.
- Only create files that don't already exist.
- At the end, report: "Created X new scenes (scenes Y-Z)" or "All scenes already existed"

### 7. YAML Format

Each file must match scene-description-template.yaml structure exactly.

### 8. Verification for Consistency with Canon - MANDATORY

After generating all scenes, you MUST perform verification:

**First Verification (Automated Search for Relative References):**
- Use grep/search to find any remaining relative cross-references in scene_XXXX.yaml files.
- Search for patterns like: "same.*from", "same.*scene", "previous.*scene", "earlier.*scene", "from scene", "scene [0-9]".
- If ANY are found, it's a critical failure. Fix them.

**Second Verification (Canonical Cross-Check):**
- For every scene, compare the character, location, and item descriptions with the entries in the canon.yaml file.
- Verify that the description in the scene is an EXACT MATCH of the description_block from the corresponding entry in canon.yaml.

**Third Verification (Abstract Concept Check) - CRITICAL:**
Search ALL generated scenes for forbidden abstract patterns:
- Use grep to find red flag words: "represents", "symbolizes", "reflects aspects", "metaphorically", "embodying"
- Search for temporal abstractions: "past.*present.*future", "different periods", "stages of", "aspects of"
- Look for divided objects: "divided into.*sections", "each.*reflecting", "parts showing"
- Check for conceptual descriptions: "journey of", "representing", "symbolizing"

If ANY abstract concepts are found:
1. STOP immediately
2. Replace abstract description with concrete physical details
3. Focus on what's actually visible, not what it means
4. Re-verify after corrections

Verification must confirm:
- Each scene can be understood in complete isolation.
- All recurring elements in every scene are consistent with the canon.yaml file.
- No usage of words like "nudity", "naked", "nude", "bare skin" or synonyms - replace with scenes showing characters clothed or from angles that don't reveal nudity.
- NO abstract or metaphorical descriptions exist in any scene.

### 9. Character Name Verification - CRITICAL FOR MEDIA

Before location verification, you MUST check that NO real names appear in scenes:

**Character Name Check:**
- Use grep/search to find ANY real names from research.md that might have leaked into scenes
- Search for common name patterns that indicate personal data
- This is CRITICAL - scenes with real names will FAIL in AI generation

**Search for forbidden patterns:**
```bash
# Search for any potential real names (these are examples from historical records)
grep -i "oppenheimer\|einstein\|truman\|fermi\|anastasia\|costello\|rosenberg" scene_*.yaml
grep -i "robert\|albert\|harry\|enrico\|julius\|ethel\|frank" scene_*.yaml
grep -E "[A-Z][a-z]+ [A-Z][a-z]+" scene_*.yaml  # Pattern for "FirstName LastName"
```

**Common Problems to Fix:**

❌ **FORBIDDEN - Real names in scenes:**
```yaml
characters:
  - appearance: "J. Robert Oppenheimer in white lab coat"
  - appearance: "Albert Einstein with wild white hair"
  - appearance: "Frank Costello in pinstripe suit"
```

✅ **CORRECT - Only character codes:**
```yaml
characters:
  - appearance: "character_JRO in white lab coat"
  - appearance: "character_AE with wild white hair"
  - appearance: "character_FC in pinstripe suit"
```

**Verification must confirm:**
- NO real first names or surnames anywhere in scene files
- ALL characters referenced only by their character codes (character_XX)
- Even in narrative descriptions, use only "the man", "the scientist", "the official" etc.
- If ANY real name is found, it's a CRITICAL FAILURE - fix immediately

### 10. Location Completeness Verification - MANDATORY

After character name verification, you MUST verify location completeness:

**Location Completeness Check:**
- Use grep/search to find incomplete location descriptions
- Search for patterns that need geographical context
- Verify each location has full geographical/cultural context

**Common Location Problems to Fix:**

❌ **INCOMPLETE LOCATIONS:**
```yaml
location: "Manhattan barbershop"
location: "Senate hearing room"
location: "Waterfront docks"
location: "Harlem street"
```

✅ **COMPLETE LOCATIONS:**
```yaml
location: "Park Sheraton Hotel barbershop, midtown Manhattan, New York City"
location: "US Senate Caucus Room 318, Russell Building, Washington DC"
location: "Brooklyn waterfront shipping docks, Red Hook district, New York"
location: "125th Street and Lenox Avenue intersection, Harlem, New York City"
```

**Location Verification Rules:**
- Every location must be self-explanatory - AI should understand where it is without prior knowledge
- Add geographical context - city, state, country, or major landmarks
- Include historical context when relevant - "1950s Manhattan", "Cold War era Washington"
- Replace local references with descriptive terms plus context
- Provide architectural/environmental details that establish the setting

Location Verification must confirm:
- No locations depend on prior knowledge of the media/event
- All locations include sufficient geographical context
- Local names are explained or replaced with descriptions
- Each location can be visualized by AI without additional context

This step is critical because incomplete locations will result in poor AI image generation.

### 11. Time Completeness Verification - MANDATORY

After location verification, you MUST verify time completeness based on media content:

**Time Completeness Check:**
- Use grep/search to find incomplete time descriptions
- Verify each time element is supported by media content
- Only include time details that come from the source material

**Minimal Time Requirements:**
- Period (25-year span): Year is ideal, decade acceptable - BUT ONLY if specified in media
- Season: Minimum requirement IF KNOWN from media content
- If season details are known: specify early/late (early spring = snow, late spring = blooming flowers)
- Month is acceptable if mentioned in media
- Specific dates only if they impact the scene (e.g., October 25, 1957 for Anastasia assassination)
- Time of day: Required if specified in media, hour if mentioned

**CRITICAL RULE:** All time elements must derive from media content - never add arbitrary temporal details

**Common Time Problems to Fix:**

❌ **ARBITRARY TIME DETAILS:**
```yaml
time: "1957 spring, morning"     # If spring not specified in media
time: "1943 summer, afternoon"   # If summer not mentioned in source
time: "1953 winter, evening"     # If winter not from media content
```

✅ **MEDIA-SUPPORTED TIME:**
```yaml
time: "October 25, 1957, 10:15 AM"        # If specific date/time documented
time: "August 1, 1943, evening"           # If date and time of day specified
time: "1950, afternoon Senate session"    # If media mentions specific session
time: "1953 June 19, 8 PM execution"      # If media documents exact time
```

**Time Verification Rules:**
- Every time detail must be traceable to media content - no arbitrary additions
- Use exact dates when historically documented - assassinations, trials, hearings
- Include seasonal details only if media describes them - weather conditions, etc.
- Add specific times when documented - "10:15 AM shooting", "8 PM execution"
- Time of day must match media descriptions - don't guess morning vs afternoon

Time Verification must confirm:
- No time details added without media support
- All seasonal references match media descriptions
- Time of day corresponds to media narrative
- Specific dates/times match historical records

This step ensures temporal accuracy and prevents AI from receiving contradictory time/weather information.

## COMMON MISTAKES TO AVOID - CRITICAL SECTION

### Frequently Occurring Errors in Scene Generation:

**1. Abstract Surface Divisions:**
❌ WRONG: "Mirror surface divided into three sections, each showing different aspect"
✅ CORRECT: "Ornate bronze mirror with engraved border patterns"

**2. Symbolic Time Representations:**
❌ WRONG: "Clock face where numbers represent stages of investigation"
✅ CORRECT: "Wall clock showing 10:15, black hands on white face"

**3. Metaphorical Object Arrangements:**
❌ WRONG: "Evidence arranged to represent the web of corruption"
✅ CORRECT: "Stack of photographs and documents on steel desk"

**4. Conceptual Visual Compositions:**
❌ WRONG: "Scene composed to show the duality of justice and crime"
✅ CORRECT: "Prosecutor and defendant facing each other across courtroom"

**5. Objects "Telling Stories":**
❌ WRONG: "Newspaper that tells the story of the mob's downfall"
✅ CORRECT: "New York Times front page with headline about arrest"

**6. Multiple Realities in Single Frame:**
❌ WRONG: "Courtroom where past crimes and present justice coexist"
✅ CORRECT: "Wood-paneled federal courtroom with American flag"

**7. Symbolic Light/Shadow:**
❌ WRONG: "Light representing truth cutting through darkness of crime"
✅ CORRECT: "Fluorescent lights illuminating witness stand"

**8. Abstract Emotional Landscapes:**
❌ WRONG: "City reflecting society's moral decay"
✅ CORRECT: "Rain-slicked Manhattan street with neon signs"

### Quick Checklist Before Finalizing Any Scene:
- [ ] Can this be photographed exactly as described?
- [ ] Are all elements physically present and visible?
- [ ] Does description avoid all red flag words?
- [ ] Are mirrors/reflections showing only real objects that are physically in front of them, following laws of optics?
- [ ] Is each detail concrete and observable?
- [ ] Would an AI image generator understand this without interpretation?

## Important Guidelines

Generate YAML data that will be used as prompts for AI image generation

**LANGUAGE:** All scene descriptions MUST be in English

**PERSPECTIVE:** Write as a neutral observer who sees the scene for the first time
- Describe what is visually present, not story context
- The observer knows geography/locations but NOT the characters or plot
- Scene can be dramatic/emotional, but described through visual elements
- Like a photographer who stumbled upon this moment without knowing the backstory

**LOCATIONS:** When creating entries in canon.yaml, every location must have a complete description.

**CHARACTERS:** When creating entries in canon.yaml for media, every character must have a complete description:
- **CRITICAL:** Use ONLY initials, never full names (use "character_AA" for someone with initials A.A.)
- age (exact for children, approximate for adults: 20s, 40s, 60s). If media scenes show the same characters at different life stages, do not write age ranges like "0-100". Instead, note that age depends on the specific scene and should be inferred from scene context if not definitively stated.
- hair color and style
- build (slender, stocky, athletic, muscular, frail)
- height indication (tall, average, short)
- ALL physical details from research.md EXCEPT the actual name

**EMOTIONS & ABSTRACT CONCEPTS:** Use only physical, visible elements
- Good: "furrowed brow, clenched fists, leaning forward"
- Bad: "determination on face", "feeling anxious"

**CLOTHING:** Be specific about period garments
- Good: "gray flannel suit, white dress shirt, narrow black tie"
- Bad: "everyday clothes", "best outfit"

**NO PROPRIETARY NAMES:**
For CHARACTERS in media (this is explanation for the agent, NOT to be included in YAML):
- Never write actual names in YAML files
- Use only: "character_AA", "character_FC", "character_JR" etc.

For LOCATIONS (can use real place names):
- Good: "Park Sheraton Hotel", "Manhattan", "Brooklyn waterfront"
- These are allowed as they are locations, not personal names

**NO STORY REFERENCES:** Each scene stands alone
- Bad: "return to where crime began"
- Good: "man at barbershop entrance"

**SCENE INDEPENDENCE - CRITICAL:**
- NO cross-references between scenes whatsoever.
- Ensure every scene contains a full description by correctly copying it from the canon.yaml file.

**ONE EVENT PER SCENE - MANDATORY:**
- Each scene must represent a DIFFERENT moment or event from the media.
- NEVER split a single event across multiple scenes.
- Choose the most visually compelling moment of each event.

❌ **WRONG - Sequential Event Breakdown:**
```
Scene A: Gunman entering barbershop, hand reaching for weapon
Scene B: Gunman aiming at target in barber chair
Scene C: Aftermath with victim slumped in chair
```
This is ONE event (assassination) artificially split into three scenes.

✅ **CORRECT - Different Events:**
```
Scene A: Morning briefing at police headquarters about mob activities
Scene B: Assassination scene in barbershop - gunman firing weapon
Scene C: Evening press conference announcing investigation
```
Each scene represents a completely different moment from the story.

**Selection Rule:** If you could describe multiple scenes as "then this happens next," they should be condensed into ONE scene showing the most dramatic moment.

**SIMPLE VISUAL LANGUAGE:** Write like describing a photograph
- Bad: "sunset painting city gold like spilled blood"
- Good: "orange sunset over Manhattan skyline"

**PHYSICAL ELEMENTS ONLY:** Describe what camera lens would capture
- Good: "witness stand with microphone and water glass"
- Bad: "moral dilemma"
- Good: "evidence table with photographs and typed documents"
- Bad: "table divided into sections showing progression of crime"
- Good: "map with red pins marking crime locations"
- Bad: "map representing the network of corruption"
- NO temporal concepts that can't be photographed (past/future in single frame)
- NO metaphorical divisions or symbolic sections in objects
- NO abstract representations of concepts through visual arrangement

**CRITICAL ANTI-PATTERNS - ABSOLUTELY FORBIDDEN:**
These abstract concepts MUST NEVER appear in scenes:

**IMPORTANT DISTINCTION: The scene itself CAN be metaphorical, but its DESCRIPTION must be purely physical.**

Example:
- ✅ SCENE CONCEPT: "Justice prevailing over crime" (metaphorical concept)
- ✅ PHYSICAL DESCRIPTION: "Judge's gavel striking wooden sound block in courtroom"
- ❌ ABSTRACT DESCRIPTION: "Gavel representing justice crushing the forces of corruption"

**The rule: Describe WHAT you see, not WHAT IT MEANS.**

**PUPPET STRING METAPHOR - STRICTLY FORBIDDEN:**
❌ NEVER use puppet string metaphors in any form:
- "puppet strings connecting", "strings of control", "invisible strings"
- "strings extending from hands/head", "puppet masters in background"
- High angle shots showing "puppet string metaphor from above"
- Any visual metaphor involving strings, wires, or threads controlling people

These create confusing visuals that look like snakes, tentacles, or supernatural elements rather than clear political commentary. Use direct physical descriptions instead.

❌ **Temporal Abstractions:**
- "reflecting different aspects of time/investigation/trial"
- "showing past, present, and future simultaneously"
- "divided into sections representing different periods"
- Any object "representing" or "symbolizing" abstract concepts

❌ **Red Flag Words - If you write these, STOP and revise:**
- "represents", "symbolizes", "reflects aspects of"
- "metaphorically", "conceptually", "philosophically"
- "divided into sections showing", "each part reflecting"
- "simultaneously visible", "aspects of", "embodying"

❌ **Abstract Visual Concepts:**
- Objects divided to show multiple time periods
- Mirrors showing anything except actual physical reflections
- Arrangements "representing" ideas rather than being physical layouts
- Visual metaphors or symbolic compositions

❌ **REAL EXAMPLES FROM GENERATED SCENES - NEVER DO THIS:**
- "Mushroom cloud represents destructive force of human ambition"
- "Courtroom represents the theater of justice"
- "Evidence board represents the web of connections"
- "Empty chair represents the absence of truth"
- "Figure embodying the spirit of resistance"
- "Standing with arms raised, embodying victory over corruption"
- "Smoke and chaos reflecting moral confusion"
- "Clock as metaphor for time running out"

✅ **Instead, use concrete physical descriptions:**
- Actual objects that exist in the scene
- Real reflections of what's physically present
- Tangible arrangements without symbolic meaning
- Observable details without interpretive overlay

**MIRROR AND REFLECTION RULES:**
- Mirrors show ONLY what is physically in front of them at that moment
- Reflections must obey laws of physics and optics
- NO "magical" mirrors showing different times or places
- NO divided surfaces showing multiple realities
- If describing a reflection, describe the actual reflected object, not concepts

Examples:
- Good: "mirror reflecting detective's tired face and rumpled suit"
- Bad: "mirror reflecting his past failures and current determination"
- Good: "window glass showing distorted reflection of street scene"
- Bad: "window surface divided showing stages of the investigation"

- Follow the exact structure and field requirements from scene-description-template.yaml
- Do NOT define visual style (colors, artistic technique, rendering style) - only describe WHAT is in the scene
- The scenes must be internally consistent and cohesive
- Follow narrative arc defined in the selected generator
- Focus only on the chosen approach without mixing styles
- Output must be valid YAML matching the template structure

## Final Report

After completing all steps, provide a report:

1. **Scenes Generated:** Number of new scenes created (if any)
2. **TODOIT Structure:** Confirm creation of hierarchical task structure
3. **Subtasks Created:** Report total count (should match scene_count from media.yaml)
4. **Scene Generation Status:** All scene_gen subtasks marked as completed