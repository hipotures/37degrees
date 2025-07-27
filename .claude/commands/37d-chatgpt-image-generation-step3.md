# ChatGPT Bulk Image Generation Process

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

### b) Add Context Files (ONLY when creating new project)
**Execute this step ONLY if you just created a new project:**
- Click "Add files" to open file addition dialog
- In the dialog window, click "Add files" button in the top right corner (next to Close button)
- System file selection window will open
- Provide full path to the book's `docs/findings` folder, e.g.:
  `/home/xai/DEV/37degrees/books/0036_treasure_island/docs/findings`
- Select ALL markdown files (.md) in the `findings` folder (using Ctrl+A or manual selection)
- Click "Open" button in the system window
- **WAIT** at least 10 seconds for all files to load
  - While loading, files show a spinning circle icon (loading indicator)
  - When loaded, icon changes to regular document icon
  - **IMPORTANT**: Close window only when all files show document icon (no loading circle)
- Click "Close" button (X) to close the dialog
- After closing, "Project files" should show file count (e.g., "7 files")
- **TROUBLESHOOTING**:
  - If any file loads indefinitely (loading circle doesn't disappear):
    - Reload the entire page (F5 or Ctrl+R)
    - Repeat file attachment operation
  - **NOTE**: Some files may already be attached - check which files are already added
  - Should be exactly **7 files** from findings folder:
    - 37d-bibliography-manager_findings.md
    - 37d-culture-impact_findings.md
    - 37d-facts-hunter_findings.md
    - 37d-polish-specialist_findings.md
    - 37d-source-validator_findings.md
    - 37d-symbol-analyst_findings.md
    - 37d-youth-connector_findings.md
- **ONLY NOW** click in the chat text field (where it says "New chat in [project_name]")

### c) Prepare JSON Files
Navigate to the `prompts/genimage/` directory for this book

## 3. Generation Process

For each JSON file in numerical order (scene_01.json, scene_02.json, etc.):

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

### c) Wait for Generation
- After clicking "Send prompt", execute script 37degrees/sleep_script.sh with argument 150 before checking generation status
- Then check if status changed from "Creating image" or "Adding details" to "Image created"
- If image is NOT ready after first run sleep_script.sh:
  - run 37degrees/sleep_script.sh with argument 50 and than check again
  - If still not ready, run 37degrees/sleep_script.sh 50 again and check again
  - Maximum 3 checks total (150s + 50s + 50s = 250 seconds maximum)
- **If image is still not generated after 250 seconds**:
  - Reload the entire page (F5 or Ctrl+R)
  - Check if the image was actually generated and is visible on the page
  - Check if the prompt is still in the input field
  - Proceed based on what you find:
    - If image exists: proceed to download step
    - If prompt is still there but no image: send prompt again
    - If neither: restart from file attachment step

### d) Save Image
After generation completes:
- **METHOD 1 (RECOMMENDED)**: Right-click on generated image and select "Save image as..."
- **METHOD 2 (ALTERNATIVE)**: Click "Download this image" button under image (may not always work)
- **NOTE**: If download button doesn't work, ALWAYS use right-click on image
- File will be downloaded with automatic name format: `ChatGPT-Image-[Month]-[Day]-[Year]-[Hour]-[Minute]-[Second]-[AM/PM].png`
- Example: `ChatGPT-Image-Jul-27-2025-03-17-41-AM.png`

### e) Move to Proper Location
Move downloaded file from temporary folder (usually `/tmp/playwright-mcp-output/[timestamp]/`) to:
```
/home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/
```
changing name to: `[book_number]_scene_[NN].png`

### f) Proceed to Next
**ONLY AFTER** completing entire process for one image, proceed to next JSON

## IMPORTANT LIMITATIONS

- **DO NOT** send next JSON until previous image is fully generated
- **DO NOT** add any text to JSON - only clean file content (applies to old method)
- For new method use EXACTLY this text: `Create an image based on the scene, style, and visual specifications described in the attached JSON. The JSON is a blueprint, not the content.`
- Each image must be fully generated and saved before proceeding to next
- If generation hangs, wait or refresh page before continuing
- Use "Create image" (DALL-E) tool for each image
- Add context files ONLY when creating new project, not for each image

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

## Tips

1. Process is time-consuming - each image may take up to 4 minutes to generate (250s maximum)
2. **STRICT TIMING**: Always wait 150 seconds initially, then check every 50 seconds (max 3 times)
3. Monitor generation status following the exact timing protocol
4. In case of errors, record which images were already generated
5. Use dedicated ChatGPT project for each book (project name = book folder name)
6. Thanks to projects, you can easily return to image generation for specific book
7. **NEW METHOD**: Attaching JSON files via "+" button is more reliable than pasting content
8. ChatGPT automatically recognizes JSON structure from attached file
9. If page reload is needed, always check current state before proceeding