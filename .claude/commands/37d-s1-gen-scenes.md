# Custom Instruction: Step 1 - Scene Descriptions Generator

## Task Overview
Generate 25 scene descriptions in JSON format based on book research.

## Input Parameters
1. **Book Title**: (e.g., "Wuthering Heights")
2. **Author**: (e.g., "Emily Brontë")
3. **Generator Type**: Choose one: `narrative`, `flexible`, `podcast`, `atmospheric`, or `emotional` (default: `podcast` if not specified)

## Process Steps

### 1. Validate Generator Type and Locate Book Directory
- If no generator type is provided, inform user: "No generator type specified. Using default: podcast"
- Validate generator type is one of: `narrative`, `flexible`, `podcast`, `atmospheric`, or `emotional`
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
  - If `atmospheric`: Read `config/prompt/scene-generator/atmospheric-moments-generator.md`
  - If `emotional`: Read `config/prompt/scene-generator/emotional-journey-generator.md`
  
  IMPORTANT: Read ONLY the file corresponding to the selected generator type. Do NOT read the other generators.
  
  Study the selected generator thoroughly:
  - Understand its specific approach and guidelines
  - Analyze structure and pacing requirements
  - Note all instructions and constraints
  - Understand how it differs from other generators

### 3. Analyze Book Research
- Navigate to `books/[book_dir]/docs/` directory, this is your search directory!
- Read ONLY files matching the pattern `37d-*_findings.md` and the file `review.md` (they may exist in various combinations, some may be missing, but at least review.md must be present).
- Read ALL files, from the first to the last line (for tool Read use offsets if needed)
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

### 7. Verification for Cross-References - MANDATORY
After generating all scenes, you MUST perform verification:

**First Verification:**
- Use grep/search to find cross-references between scenes
- Search for patterns like: "same.*from", "same.*scene", "previous.*scene", "earlier.*scene", "from scene", "scene [0-9]"
- If ANY cross-references are found:
  - Fix all instances by providing complete, standalone descriptions
  - Replace all relative references with absolute descriptions
  
**Second Verification (if corrections were made):**
- Run the same search again after corrections
- Ensure NO cross-references remain
- If still found, fix and verify one more time

**Verification must confirm:**
- No character descriptions reference other scenes
- No location descriptions reference other scenes  
- No time references are relative to other scenes
- Each scene can be understood in complete isolation

Only after passing verification can the task be considered complete.

### 8. Location Completeness Verification - MANDATORY
After cross-reference verification, you MUST verify location completeness:

**Location Completeness Check:**
- Use grep/search to find incomplete location descriptions
- Search for patterns that need geographical context
- Verify each location has full geographical/cultural context

**Common Location Problems to Fix:**
❌ **INCOMPLETE LOCATIONS:**
```json
"location": "Warsaw cityscape"
"location": "Aristocratic estate" 
"location": "Krakowskie Przedmieście"
"location": "Powiśle district"
```

✅ **COMPLETE LOCATIONS:**
```json
"location": "Polish capital Warsaw under Russian partition, view from Vistula River valley"
"location": "Polish manor house in Mazovian countryside, 50km from Warsaw"
"location": "Prestigious commercial thoroughfare in Warsaw city center, Congress Poland"
"location": "Poor riverside neighborhood in Warsaw, wooden tenements near Vistula"
```

**Location Verification Rules:**
1. **Every location must be self-explanatory** - AI should understand where it is without prior knowledge
2. **Add geographical context** - country, region, or major landmarks
3. **Include historical context when relevant** - "under Russian partition", "Congress Poland"
4. **Replace local street names** with descriptive terms plus context
5. **Provide architectural/environmental details** that establish the setting

**Location Verification must confirm:**
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
1. **Period (25-year span)**: Year is ideal, decade acceptable - BUT ONLY if specified in book
2. **Season**: Minimum requirement IF KNOWN from book content
   - If season details are known: specify early/late (early spring = snow, late spring = blooming flowers)
   - Month is acceptable if mentioned in book
   - Specific dates only if they impact the scene (e.g., June 1st, Children's Day)
3. **Time of day**: Required if specified in book, hour if mentioned

**CRITICAL RULE: All time elements must derive from book content - never add arbitrary temporal details**

**Common Time Problems to Fix:**
❌ **ARBITRARY TIME DETAILS:**
```json
"time": "1878 spring, morning"     // If spring not specified in book
"time": "1878 summer, afternoon"   // If summer not mentioned in source
"time": "1878 winter, evening"     // If winter not from book content
```

✅ **BOOK-SUPPORTED TIME:**
```json
"time": "1878, morning"                    // If only year and time of day known
"time": "Late 1870s, evening"             // If only decade and time of day specified
"time": "1878 early spring, dawn"         // If book specifies early spring details
"time": "1878 May, afternoon garden party" // If book mentions specific month/event
```

**Time Verification Rules:**
1. **Every time detail must be traceable to book content** - no arbitrary additions
2. **Use broad periods if specifics unknown** - "Late 1870s" better than guessed "1878 spring"
3. **Include seasonal details only if book describes them** - weather, plant states, etc.
4. **Add specific dates only if plot-relevant** - holidays, anniversaries, etc.
5. **Time of day must match book descriptions** - don't guess morning vs afternoon

**Time Verification must confirm:**
- No time details added without book support
- All seasonal references match book descriptions
- Time of day corresponds to book narrative
- Specific dates only included if plot-significant

This step ensures temporal accuracy and prevents AI from receiving contradictory time/weather information.

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
- **EMOTIONS & ABSTRACT CONCEPTS: Use only physical, visible elements**
  - Good: "furrowed brow, clenched fists, leaning forward"
  - Bad: "determination on face", "feeling anxious"
  - Avoid abstract concepts in atmosphere/details:
    - Bad: "dangerous diplomacy", "chess match of words", "veneer of civility"
    - Good: "man gripping crutch tightly", "sweat on foreheads", "hands near weapons"
  - CRITICAL: Replace abstract moments with concrete visual elements:
    - Bad: "pivotal moment", "internal struggle", "crossroads of destiny"
    - Good: "two distinct dirt paths forking at 90-degree angle", "wooden signpost with two arrows", "boy standing with left foot on bright path, right foot on dark path"
  - Describe what camera would see, not what it means
  
  **REAL EXAMPLE - Scene 15 Problem:**
  ❌ **WRONG:** "atmosphere": "pivotal moment, internal struggle externalized, choice between paths"
  ✅ **CORRECT:** "details": "two clearly visible forest paths diverging - left path leads uphill toward sunny clearing with flowers, right path descends into dark forest with thorns, wooden crossroads marker with two directional arrows, boy positioned exactly where paths meet"
- **CLOTHING: Be specific about period garments**
  - Good: "brown wool vest, white linen shirt, knee-length breeches"
  - Bad: "everyday clothes", "best outfit"
- **NO PROPRIETARY NAMES**: Replace ALL proper names with descriptive terms
  - Bad: "Castle Blackstone", "The Wanderer ship", "Isle of Mysteries", "Admiral Benbow Inn", "Hispaniola"
  - Good: "medieval fortress", "merchant sailing vessel", "foggy island", "coastal tavern", "three-masted merchant ship"
  - This includes: building names, ship names, location names (except real geographic locations like "Devon" or "England")
  - Even if these names appear in the original book, replace them with descriptions
  - REMEMBER: AI image generators don't know fictional place names from books. Always describe what something IS, not what it's called in the story
  - The "title" field must NOT contain character names
    - Good: "Negotiations at Dawn", "Library Window View"
    - Bad: "Sofia at the Gate", "Marcus's Discovery"
- **NO STORY REFERENCES**: Each scene stands alone
  - Bad: "return to where adventure began", "reminder of journey"
  - Good: "young man at tavern window", "treasure chest in corner"
  - Never mention what happened before or will happen after
- **SCENE INDEPENDENCE - CRITICAL**: Each scene must be 100% independent
  - NO cross-references between scenes whatsoever
  - Each scene must have complete, standalone descriptions
  - NEVER use phrases like:
    - "Same character from scene X"
    - "Same location as earlier"
    - "Previously seen character"
    - "Returns to the place from scene Y"
  - ALWAYS provide full descriptions in every scene
  - Treat each scene as if it's the only one that exists
- **SIMPLE VISUAL LANGUAGE**: Write like describing a photograph
  - Bad: "sunset painting ocean gold like remembered doubloons"
  - Good: "orange sunset reflecting on water surface"
  - Bad: "eternal sea continuing its rhythms"
  - Good: "waves breaking on shore"
- **PHYSICAL ELEMENTS ONLY**: Describe what camera lens would capture
  - Good: "rope bridge spanning 50-foot gorge", "two wooden doors side by side", "scales weighing gold vs feathers"
  - Bad: "moral dilemma", "life-changing decision", "moment of truth"
  - Every abstract concept must have physical manifestation
  - If scene represents "choice" - show actual paths, doors, objects to choose between
  - If scene shows "conflict" - show weapons, aggressive postures, opposing groups
  - Complete visual clarity: every element must be specifically visible
    - Bad: "place where two worlds meet" → Good: "forest clearing divided by stream, bright meadow on left, dark woods on right"
- Follow the exact structure and field requirements from scene-description-template.json
- Do NOT define visual style (colors, artistic technique, rendering style) - only describe WHAT is in the scene
- The 25 scenes must be internally consistent and cohesive
- Follow narrative arc defined in the selected generator
- Focus only on the chosen approach without mixing styles
- Output must be valid JSON matching the template structure

## Examples of Scene Independence Violations and Corrections

### Character Descriptions
❌ **WRONG:**
```json
"appearance": "Same writer from scene 5, now gaunt and desperate"
"appearance": "Same elegant woman from previous scenes"
"appearance": "The young blonde man from opening scene, now disheveled"
```

✅ **CORRECT:**
```json
"appearance": "Man, late 30s, dark hair, gaunt and desperate, wild-eyed"
"appearance": "Elegant woman, early 30s, beautiful features, melancholy expression"
"appearance": "Young man, late 20s, blonde hair, athletic build, now disheveled"
```

### Location Descriptions
❌ **WRONG:**
```json
"mainElements": "Same park setting as opening scene"
"setting": {"location": "Same basement apartment from earlier"}
"background": "Returns to the location from scene 3"
```

✅ **CORRECT:**
```json
"mainElements": "Moscow park setting with ornamental pond, tree-lined paths"
"setting": {"location": "Small basement apartment, cramped writing space"}
"background": "Ancient Jerusalem palace courtyard with limestone columns"
```

### Time References
❌ **WRONG:**
```json
"time": "Several weeks after scene 5"
"time": "Same day as previous scene, later"
"time": "Following the events of scene 12"
```

✅ **CORRECT:**
```json
"time": "1930s Moscow, late evening, autumn"
"time": "1930s Moscow, evening approaching"
"time": "Ancient Jerusalem, afternoon, Passover season"
```

### Complete Example - Scene Transformation

❌ **WRONG SCENE:**
```json
{
  "sceneDescription": {
    "title": "Return to the Park",
    "setting": {
      "time": "Several days after opening scene",
      "location": "Same park bench where it all began"
    },
    "characters": [{
      "appearance": "Same young blonde man from scene 1, now wild-eyed",
      "clothing": "Same clothes but torn and dirty"
    }]
  }
}
```

✅ **CORRECT SCENE:**
```json
{
  "sceneDescription": {
    "title": "Desperate Search in the Park",
    "setting": {
      "time": "1930s Moscow, early morning after strange night",
      "location": "Moscow park at Patriarch's Ponds, beside ornamental pond"
    },
    "characters": [{
      "appearance": "Young man, late 20s, blonde hair, athletic build, wild-eyed and disheveled",
      "clothing": "Torn and dirty shirt partially unbuttoned, disheveled trousers"
    }]
  }
}
```

### Key Principles:
1. **Always describe characters fully** - age, hair, build, current state
2. **Always specify complete locations** - city, specific place, architectural details
3. **Never reference other scenes** - no "same", "previous", "from scene X"
4. **Treat each scene as standalone** - viewer knows nothing about other scenes
5. **Use absolute time references** - specific era, time of day, season