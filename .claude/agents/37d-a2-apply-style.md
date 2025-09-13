---
name: 37d-a2-apply-style
description: |
  Applies selected graphic style to existing scene descriptions using automated script.
  Processes scene_style subtasks by finding scenes where scene_gen is completed but scene_style is pending.
  Merges scene descriptions with visual styles and saves paths in properties.
execution_order: 2
min_tasks: 5
max_tasks: 12
todo_list: true
---

## Task Overview
Apply a selected graphic style to existing scene descriptions to create final AI-ready prompts using automated script.
Process scene_style subtasks systematically using the hierarchical TODOIT structure.

## Input Parameters
1. BOOK_FOLDER - book path books/[BOOK_FOLDER] (e.g. for "0037_wuthering_heights", full book path will be books/0037_wuthering_heights)
2. SCENE_STYLE - Style Name, graphic style to apply (e.g., `line-art-style` or `victorian-book-illustration-style`)
  - Use command: `grep [BOOK_FOLDER] config/prompt/book_styles.txt` to find style for [BOOK_FOLDER]

## Process Steps

### 1. Locate Book Directory
  - ALWAYS use specific book path, NOT books/ directory
  - Correct: LS(books/0040_hamlet) 
  - WRONG: LS(books)
  - if not found, stop

### 2. Find Ready Scene Style Subtasks

Use `todo_find_items_by_status` to locate subtasks ready for style application:

```javascript
// Find scene_style subtasks where scene_gen is completed but scene_style is pending
const readyStyleTasks = await mcp__todoit__todo_find_items_by_status({
  list_key: BOOK_FOLDER,
  conditions: {
    "scene_gen": "completed",
    "scene_style": "pending"
  },
  limit: 25
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
./scripts/internal/37d-a2-02.sh [BOOK_FOLDER] [SCENE_SET] [SCENE_STYLE]
```
Usage: ./37d-a2-02.sh <book_folder> <scene_set> <style_name>
Example: ./37d-a2-02.sh 0039_odyssey world-building-focus-generator fresco-painting-style


### 4. Verification Process

After processing, verify the generated files:

```javascript
// Check key scenes for quality assurance
const verificationScenes = [1, 13, 25];

for (const sceneNum of verificationScenes) {
  const scenePadded = sceneNum.toString().padStart(2, '0');
  const filePath = `books/${BOOK_FOLDER}/prompts/genimage/scene_${scenePadded}.yaml`;
  
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
books/[book_number]_[book_name]/prompts/genimage/
```

### 6. Mark Scene Style Subtasks as Completed

Uruchom Bash, polecenie z parametrem
```
./scripts/internal/37d-a2-01.sh [BOOK_FOLDER]
```

#### File naming:
- For all scenes: `scene_0001.yaml`, `scene_0002.yaml`, etc.
- For single scene: `scene_[number].yaml`

#### Property tracking:
- Each completed scene_style subtask has `scene_style_pathfile` property
- Failed subtasks have `ERROR` property with failure reason

## Important Guidelines

- Use automated script for consistency and reliability
- Always perform verification on key scenes (first, middle, last)
- Report any YAML validation errors or missing fields
- Update subtask status immediately after processing
- Save file paths in properties for next stage reference
- Handle both individual scene and batch processing modes

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
1. **Scenes Processed:** Count of successfully styled scenes
2. **Verification Results:** Status of quality checks
3. **Properties Set:** Confirmation of scene_style_pathfile properties
4. **Next Stage Readiness:** Count of scenes ready for image generation
5. **Error Summary:** Any failed scenes with reasons

The system is now ready for the next agent (37d-a3-generate-image) to process the image_gen subtasks.