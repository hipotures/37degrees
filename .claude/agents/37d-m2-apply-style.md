---
name: 37d-m2-apply-style
description: |
  Applies selected graphic style to existing scene descriptions using automated script.
  Processes scene_style subtasks by finding scenes where scene_gen is completed but scene_style is pending.
  Merges scene descriptions with visual styles and saves paths in properties.
  Style is read from graphics_style field in media.yaml.
execution_order: 2
min_tasks: 5
max_tasks: 12
todo_list: true
---

## Task Overview
Apply a selected graphic style to existing scene descriptions to create final AI-ready prompts using automated script.
Process scene_style subtasks systematically using the hierarchical TODOIT structure.
Style is automatically retrieved from media.yaml configuration.

## Input Parameters
1. MEDIA_FOLDER - media path media/[MEDIA_FOLDER] (e.g. for "m00001_atomic_bomb", full media path will be media/m00001_atomic_bomb)

## Process Steps

### 1. Locate Media Directory and Read Configuration
  - ALWAYS use specific media path, NOT media/ directory
  - Correct: LS(media/m00001_atomic_bomb)
  - WRONG: LS(media)
  - if not found, stop

  Read media/[MEDIA_FOLDER]/media.yaml and extract:
  - graphics_style: The style to apply (e.g., "film-noir-1950s-melodrama")
  - scene_generator: The generator type used for scenes
  - scene_count: Total number of scenes

### 2. Find Ready Scene Style Subtasks

Use `todo_find_items_by_status` to locate subtasks ready for style application:

```javascript
// Find scene_style subtasks where scene_gen is completed but scene_style is pending
const readyStyleTasks = await mcp__todoit__todo_find_items_by_status({
  list_key: MEDIA_FOLDER,
  conditions: {
    "scene_gen": "completed",
    "scene_style": "pending"
  },
  limit: scene_count  // Use scene_count from media.yaml
});

if (!readyStyleTasks.success || readyStyleTasks.items.length === 0) {
  console.log("No scene_style subtasks ready for processing");
  return;
}

console.log(`Found ${readyStyleTasks.items.length} scenes ready for style application`);
```

### 3. Apply Style Using Batch Script

Apply style to all scenes at once using the bash script (don't use folders paths):
```
./scripts/internal/37d-m2-02.sh [MEDIA_FOLDER] [SCENE_GENERATOR] [GRAPHICS_STYLE]
```
Usage: ./37d-m2-02.sh <media_folder> <scene_generator> <graphics_style>
Example: ./37d-m2-02.sh m00001_atomic_bomb narrative film-noir-1950s-melodrama


### 4. Verification Process

After processing, verify the generated files:

```javascript
// Determine verification scenes based on scene_count
const sceneCount = parseInt(scene_count); // from media.yaml
const verificationScenes = [];

// Always check first scene
verificationScenes.push(1);

// Add middle scene if more than 2 scenes
if (sceneCount > 2) {
  verificationScenes.push(Math.ceil(sceneCount / 2));
}

// Add last scene if more than 1 scene
if (sceneCount > 1) {
  verificationScenes.push(sceneCount);
}

for (const sceneNum of verificationScenes) {
  const scenePadded = sceneNum.toString().padStart(4, '0');
  const filePath = `media/${MEDIA_FOLDER}/prompts/genimage/scene_${scenePadded}.yaml`;

  try {
    const fileContent = await Read({ file_path: `/home/xai/DEV/37degrees/${filePath}` });

    // Verify YAML syntax and content
    if (!fileContent.includes('sceneDescription:')) {
      throw new Error(`Missing sceneDescription in scene_${scenePadded}.yaml`);
    }

    if (!fileContent.includes('colorPalette:') && !fileContent.includes('lineArt:')) {
      throw new Error(`Missing style fields in scene_${scenePadded}.yaml`);
    }

    console.log(`✅ Verification passed for scene_${scenePadded}.yaml`);

  } catch (error) {
    console.log(`❌ Verification failed for scene_${scenePadded}.yaml: ${error.message}`);
  }
}
```

### 5. Output Location and Structure

#### Output directory:
```
media/[media_folder]/prompts/genimage/
```

### 6. Mark Scene Style Subtasks as Completed

Uruchom Bash, polecenie z parametrem
```
./scripts/internal/37d-m2-01.sh [MEDIA_FOLDER]
```

#### File naming:
- For all scenes: `scene_0001.yaml`, `scene_0002.yaml`, etc.
- For single scene: `scene_[number].yaml`
- Number of files depends on scene_count from media.yaml

#### Property tracking:
- Each completed scene_style subtask has `scene_style_pathfile` property
- Failed subtasks have `ERROR` property with failure reason

## Important Guidelines

- Use automated script for consistency and reliability
- Always perform verification on key scenes (first, middle, last) based on scene_count
- Report any YAML validation errors or missing fields
- Update subtask status immediately after processing
- Save file paths in properties for next stage reference
- Handle both individual scene and batch processing modes
- Adapt to variable scene counts (not always 25 like books)

## Script Location

The merge script is located at: `scripts/merge-scenes-with-style.py`

For help with script parameters:
```bash
python3 scripts/merge-scenes-with-style.py --help
```

## Error Handling

- Failed subtasks are marked with status "failed" and ERROR property
- Successful subtasks get "completed" status and scene_style_pathfile property
- Verification catches YAML syntax errors and missing required fields
- Progress tracking allows resuming from any point

## Final Report

The agent provides comprehensive reporting:
1. **Scenes Processed:** Count of successfully styled scenes (out of scene_count total)
2. **Verification Results:** Status of quality checks
3. **Properties Set:** Confirmation of scene_style_pathfile properties
4. **Next Stage Readiness:** Count of scenes ready for image generation
5. **Error Summary:** Any failed scenes with reasons

The system is now ready for the next agent (37d-m3-generate-image) to process the image_gen subtasks.