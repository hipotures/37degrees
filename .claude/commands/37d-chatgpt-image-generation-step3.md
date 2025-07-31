# ChatGPT Bulk Image Generation Process

**AUTOMATED EXECUTION: Claude must execute all steps from first to last using MCP Playwright tools to control ChatGPT in the browser. This is NOT a manual instruction for the user.**

For book titled "[TITLE]" by "[AUTHOR]":

## 1. File Location

Find the book folder in `/home/xai/DEV/37degrees/books/` (format: `NNNN_book_name`)
- Change folder to `prompts/genimage/` directory for this book, this folder should contains JSON files

## 2. Preparation

### a) Check/Create Project in ChatGPT
- Check if a project exists with the same name as the book folder (e.g., `0036_treasure_island`)
- If project doesn't exist:
  - Click "New project" in the left panel
  - Name the project exactly like the book folder
- If project exists, use it

### b) Change Model to o3 
- left top side of page, default text "ChatGPT 4o", click it
- choose second model from list 'o3', click it
- if o3 is disabled, choose 'o4-mini'

<START LOOP>
## 3. Generation Process
For each JSON file in numerical order (scene_01.json, scene_02.json, etc.):

### a) Prepare JSON File
- Locate the appropriate JSON file in `prompts/genimage/` folder (e.g., `scene_01.json`)

### b) Configure ChatGPT - METHOD WITH FILE ATTACHMENT
- Ensure you're in the project for this book (created in step 2a)
  - Click "+" (plus) button at the bottom of chat window
  - Select "Add photos & files" from menu
  - In file selection dialog, navigate to the book's `prompts/genimage/` folder
  - Select appropriate JSON file (e.g., `scene_01.json`)
  - After attaching file, type exactly this text in text field: 
  `scene_NN - create an image based on the scene, style, and visual specifications described in the attached JSON. The JSON is a blueprint, not the content.`
  (where NN is scene number). Example of full text: `scene_12 create an image based on the scene, style, and visual specifications described in the attached JSON. The JSON is a blueprint, not the content.`
  - Click "Choose tool" button (left side of text field)
  - From dropdown menu select "Create image"
  - Send prompt by clicking send button (arrow)

### c) Wait for Generation
- After clicking "Send prompt", execute first time tool Bash(sleep 100)
- Click project name (left side of page with name like our book folder (e.g., `0036_treasure_island`)
- execute second time tool Bash(sleep 100) 
- **ONLY AFTER** completing entire process for one image, proceed to next JSON
<END LOOP>

## IMPORTANT LIMITATIONS
- Use "Create image" (DALL-E) tool for each image

## Example Naming

For book "Treasure Island" (number 0036):
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