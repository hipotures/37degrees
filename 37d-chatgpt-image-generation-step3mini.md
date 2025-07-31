# ChatGPT Bulk Image Generation Process for 
book_info:
  title: "Quo Vadis"
  author: "Henryk Sienkiewicz"
  dir_path: books/0027_quo_vadis
  
**AUTOMATED EXECUTION: Claude must execute all steps from first to last using MCP Playwright tools to control ChatGPT in the browser. This is NOT a manual instruction for the user.**

For book titled "[TITLE]" by "[AUTHOR]":

## 1. File Location

Find the book folder in `/home/xai/DEV/37degrees/books/` (format: `NNNN_book_name`)

## 2. Preparation

### a) Check/Create Project in ChatGPT
- Check if a project exists with the same name as the book folder (e.g., `0036_treasure_island`)
- If project doesn't exist:
  - Click "New project" in the left panel
  - Name the project exactly like the book folder
- If project exists, use it

### b) Prepare JSON Files
Navigate to the `prompts/genimage/` directory for this book

## 3. Generation Process

Choose one JSON file in numerical order (scene_01.json, scene_02.json, etc. /ignore files ended with done, e.g. scene_01.json.done/ ):

### a) Prepare JSON File
- Locate the appropriate JSON file in `prompts/genimage/` folder (e.g., `scene_01.json`)

### b) Configure ChatGPT - NEW METHOD WITH FILE ATTACHMENT
- Ensure you're in the project for this book (created in step 2a)
- **NEW METHOD (RECOMMENDED)**:
  - Click "+" (plus) button at the bottom of chat window
  - Select "Add photos & files" from menu
  - In file selection dialog, navigate to the book's `prompts/genimage/` folder
  - Select appropriate JSON file (e.g., `scene_01.json`)
  - After attaching file, type exactly this text in text field: `Create an image based on the scene, style, and visual specifications described in the attached JSON. The JSON is a blueprint, not the content.`
  - Click "Choose tool" button (left side of text field)
  - From dropdown menu select "Create image"
  - Send prompt by clicking send button (arrow)
- **OLD METHOD (ALTERNATIVE)**:
  - Open JSON file and copy its content
  - Paste **ONLY** clean JSON content (no additional instructions)
  - Set image generation tool (click "Choose tool" → "Create image")
  - Send prompt

### After send promtp, rename json file from prompts/genimage/ adding .done at the end of filename, e.g. mv scene_01.json scene_01.json.done

## IMPORTANT LIMITATIONS

- If generation hangs, refreash page
- Use "Create image" (DALL-E) tool for each image
- Add context files ONLY when creating new project, not for each image

## Example Naming

For book e.g. "Treasure Island" (number 0036):
- `scene_01.json` → `0036_scene_01.png`
- `scene_02.json` → `0036_scene_02.png`
- `scene_03.json` → `0036_scene_03.png`
- etc.

## Directory Structure

```
books/
  0036_treasure_island/
    prompts/
      genimage/         # Source JSON files here
        scene_01.json
        scene_02.json
        ...
    generated/          # Save generated images here
        0036_scene_01.png
        0036_scene_02.png
        ...
```

## Tips

1. Use dedicated ChatGPT project for each book (project name = book folder name)
2. If page reload is needed, always check current state before proceeding
