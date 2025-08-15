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

# Custom Instruction: Step 2 - Style Applicator (Subtasks Version)

## Task Overview
Apply a selected graphic style to existing scene descriptions to create final AI-ready prompts using automated script.
Process scene_style subtasks systematically using the hierarchical TODOIT structure.

## Input Parameters
1. **Book Title** or **Book Number**: (e.g., "Wuthering Heights" or "0037_wuthering_heights")
2. **Scene Set**: Which set to apply style to (`narrative`, `flexible`, `podcast`, `atmospheric`, or `emotional`)
3. **Style Name**: Graphic style to apply (e.g., `line-art-style` or `victorian-book-illustration-style`)
4. **Scene Number** (optional): Specific scene to process (e.g., `15` for scene_15.yaml)

## Process Steps

### 1. Locate Book Directory and TODOIT List
- Find book directory by searching for book title/number in `books/` directories
- Identify book number and path (e.g., `books/0037_wuthering_heights/`)
- Verify TODOIT list exists with the same name as book folder

```javascript
const BOOK_FOLDER = "[BOOK_FOLDER]"; // e.g., "0037_wuthering_heights"

// Verify list exists
const listInfo = await mcp__todoit__todo_get_list({
  list_key: BOOK_FOLDER,
  include_items: false,
  include_properties: true
});

if (!listInfo.success) {
  throw new Error(`TODOIT list ${BOOK_FOLDER} not found. Run 37d-a1 first.`);
}
```

### 2. Find Ready Scene Style Subtasks

Use `todo_find_subitems_by_status` to locate subtasks ready for style application:

```javascript
// Find scene_style subtasks where scene_gen is completed but scene_style is pending
const readyStyleTasks = await mcp__todoit__todo_find_subitems_by_status({
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

### 3. Process Each Scene Style Subtask

For each found subtask, apply style and update status:

```javascript
for (const subtask of readyStyleTasks.items) {
  const sceneKey = subtask.parent_key; // e.g., "scene_0001"
  const styleSubtaskKey = subtask.item_key; // e.g., "scene_0001_scene_style"
  
  // Extract scene number from key
  const sceneNumber = sceneKey.replace('scene_', '').replace(/^0+/, '') || '1';
  const scenePadded = sceneNumber.padStart(2, '0');
  
  console.log(`Processing ${sceneKey} - applying ${styleName} style`);
  
  // Subtask remains pending during processing - no in_progress needed
  
  // Execute merge script for this specific scene
  const mergeCommand = `python3 scripts/merge-scenes-with-style.py ` +
    `books/${BOOK_FOLDER}/prompts/scenes/${sceneSet}/ ` +
    `books/${BOOK_FOLDER}/prompts/genimage/ ` +
    `${styleName} ` +
    `technical-specifications ` +
    `--scene-number ${sceneNumber}`;
  
  try {
    const mergeResult = await Bash({
      command: mergeCommand,
      description: `Apply ${styleName} style to ${sceneKey}`
    });
    
    if (mergeResult.includes("ERROR") || mergeResult.includes("Failed")) {
      throw new Error(`Style application failed: ${mergeResult}`);
    }
    
    // Save style file path in properties
    const styleFilePath = `books/${BOOK_FOLDER}/prompts/genimage/scene_${scenePadded}.yaml`;
    await mcp__todoit__todo_set_item_property({
      list_key: BOOK_FOLDER,
      item_key: styleSubtaskKey,
      property_key: "scene_style_pathfile",
      property_value: styleFilePath
    });
    
    // Mark subtask as completed
    await mcp__todoit__todo_update_item_status({
      list_key: BOOK_FOLDER,
      item_key: styleSubtaskKey,
      status: "completed"
    });
    
    console.log(`✅ ${sceneKey} style applied successfully`);
    
  } catch (error) {
    // Mark subtask as failed
    await mcp__todoit__todo_update_item_status({
      list_key: BOOK_FOLDER,
      item_key: styleSubtaskKey,
      status: "failed"
    });
    
    // Save error in properties
    await mcp__todoit__todo_set_item_property({
      list_key: BOOK_FOLDER,
      item_key: styleSubtaskKey,
      property_key: "ERROR",
      property_value: error.message
    });
    
    console.log(`❌ ${sceneKey} style application failed: ${error.message}`);
  }
}
```

### 4. Batch Processing Alternative

For processing all scenes at once (when no specific scene number provided):

```javascript
// Execute merge script for all scenes
const batchMergeCommand = `python3 scripts/merge-scenes-with-style.py ` +
  `books/${BOOK_FOLDER}/prompts/scenes/${sceneSet}/ ` +
  `books/${BOOK_FOLDER}/prompts/genimage/ ` +
  `${styleName} ` +
  `technical-specifications`;

try {
  const batchResult = await Bash({
    command: batchMergeCommand,
    description: `Apply ${styleName} style to all scenes`
  });
  
  if (batchResult.includes("ERROR") || batchResult.includes("Failed")) {
    throw new Error(`Batch style application failed: ${batchResult}`);
  }
  
  // Update all processed subtasks
  for (const subtask of readyStyleTasks.items) {
    const styleSubtaskKey = subtask.item_key;
    const sceneKey = subtask.parent_key;
    const sceneNumber = sceneKey.replace('scene_', '').replace(/^0+/, '') || '1';
    const scenePadded = sceneNumber.padStart(2, '0');
    
    // Save style file path in properties
    const styleFilePath = `books/${BOOK_FOLDER}/prompts/genimage/scene_${scenePadded}.yaml`;
    await mcp__todoit__todo_set_item_property({
      list_key: BOOK_FOLDER,
      item_key: styleSubtaskKey,
      property_key: "scene_style_pathfile",
      property_value: styleFilePath
    });
    
    // Mark subtask as completed
    await mcp__todoit__todo_update_item_status({
      list_key: BOOK_FOLDER,
      item_key: styleSubtaskKey,
      status: "completed"
    });
  }
  
  console.log(`✅ Batch style application completed for ${readyStyleTasks.items.length} scenes`);
  
} catch (error) {
  console.log(`❌ Batch style application failed: ${error.message}`);
  // Mark all as failed and continue with individual processing
}
```

### 5. Verification Process

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

### 6. Update Progress and Report

```javascript
// Get updated progress
const progress = await mcp__todoit__todo_get_progress({
  list_key: BOOK_FOLDER
});

// Count completed style subtasks
const completedStyleTasks = await mcp__todoit__todo_find_subitems_by_status({
  list_key: BOOK_FOLDER,
  conditions: {
    "scene_style": "completed"
  },
  limit: 25
});

console.log(`Style Application Complete:`);
console.log(`- Processed: ${completedStyleTasks.items.length}/25 scenes`);
console.log(`- Overall Progress: ${progress.completed}/${progress.total} tasks`);
console.log(`- Next Stage Ready: ${completedStyleTasks.items.length} scenes ready for image generation`);
```

### 7. Output Location and Structure

#### Output directory:
```
books/[book_number]_[book_name]/prompts/genimage/
```

#### File naming:
- For all scenes: `scene_01.yaml`, `scene_02.yaml`, etc.
- For single scene: `scene_[number].yaml`

#### Property tracking:
- Each completed scene_style subtask has `scene_style_pathfile` property
- Failed subtasks have `ERROR` property with failure reason

### 8. Integration with Next Stage

After completion, the system is ready for 37d-a3-generate-image:

```javascript
// Verify readiness for next stage
const readyImageTasks = await mcp__todoit__todo_find_subitems_by_status({
  list_key: BOOK_FOLDER,
  conditions: {
    "scene_style": "completed",
    "image_gen": "pending"
  },
  limit: 25
});

console.log(`Ready for image generation: ${readyImageTasks.items.length} scenes`);
```

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