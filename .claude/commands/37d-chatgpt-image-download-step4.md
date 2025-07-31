# ChatGPT Image Download and Save Process

**AUTOMATED EXECUTION: Claude must execute all steps using MCP Playwright tools and file operations. This is for downloading and saving generated images from ChatGPT.**

For book titled "[TITLE]" by "[AUTHOR]":

## Prerequisites

- **ALL images must already be generated** in ChatGPT project for the book
- Project name should match book folder (e.g., `0036_treasure_island`)
- All images are visible and fully generated in ChatGPT conversations
- **ASSUMPTION**: Complete image generation process has been finished for all 25 scenes

## 1. Project Analysis and TODO Creation

### a) Access ChatGPT Project
- Open ChatGPT project for the book (created in previous steps)
- **IMPORTANT**: All 25 scenes must have completed image generation
- Project should contain multiple conversations with generated images

### b) Complete Project Analysis
**STEP 1: Navigate and Scroll Through Entire Project**
- Enter the ChatGPT project for the book
- **IMPORTANT**: Scroll through the ENTIRE conversation list to see all chats
- Use Page Down, End key, or scroll to bottom to see all conversations
- Count total number of conversations in the project
- Look for conversations with various names: "Create image from JSON scene_XX", custom resolution requests, or other image generation prompts

**STEP 2: Identify Image-Containing Conversations**
- Each conversation typically corresponds to one scene (scene_01, scene_02, etc.)
- **CRITICAL RULE**: The attached JSON file name is the ONLY reliable way to identify scene number
  - **IGNORE chat titles** - they may contain errors or be misleading
  - **ALWAYS look for attached JSON file icon and filename** (e.g., "scene_24.json")
  - **The JSON filename gives 100% certainty** about which scene the conversation represents
- **IMPORTANT**: Look for non-standard conversation names like:
  - "Wygeneruj obraz z tym samym promptem, zmien tylko rozdzielczosc na 1024 × 1792 px" (resolution change)
  - Other custom image generation requests
- **CRITICAL**: Some conversations may contain multiple images for the same scene
- **MISLEADING TITLES**: Conversations titled "Brak wygenerowanego obrazu" may still contain generated images - this title means the USER wrote this text, but ChatGPT may have generated an image anyway
- **VERIFICATION METHOD**: When entering each conversation, first look for the JSON file attachment to confirm scene number

### c) Create TODO List for Downloads
**MANDATORY STEP**: ONLY AFTER scrolling through entire project, create a comprehensive TODO list containing:
- One task for each conversation that contains generated images
- Identify which scene each conversation represents
- Note if conversation contains single or multiple images
- **Example TODO structure**:
  - "Check and download from scene_01 conversation"
  - "Check and download from scene_02 conversation" 
  - "Check and download from scene_03 conversation"
  - "Check and download from resolution conversation (Wygeneruj obraz z tym samym promptem, zmien tylko rozdzielczosc na 1024 × 1792 px)"
  - "Check and download from 'Brak wygenerowanego obrazu' conversation - may have generated image despite title"
  - "Download image(s) from scene_08 conversation (first)" - if multiple conversations for same scene
  - "Download image(s) from scene_08 conversation (second)" 
  - etc.

**Analysis Example Process:**
1. Open ChatGPT project → Navigate to conversation list
2. Scroll from top to bottom (scene_25 → scene_01 order typically)
3. Create comprehensive list: "Found conversations: scene_25, scene_24, scene_23, resolution change conversation, scene_22, scene_21, 'Brak wygenerowanego obrazu' (check for image), scene_19, scene_18, scene_16, scene_15, scene_14, scene_13, scene_12, scene_11, scene_10, scene_09, scene_08 (two conversations), scene_07, scene_06, scene_05, scene_04, scene_03, scene_02, scene_01"
4. Create TODO with one item per conversation with images
5. **IMPORTANT**: Create TODO with "Check and download" tasks - you must verify each conversation actually contains an image before attempting download
6. **ONLY THEN** start systematic checking and downloading process

### d) Identify Multiple Images per Scene
- **SCAN EACH CONVERSATION**: Some conversations may contain 2, 3, or more images for the same scene
- **COUNT IMAGES**: Note exact number of images in each conversation
- **PREPARE NAMING**: Plan naming scheme for multiple images (see section 5)

## 2. Download Process

For each conversation from TODO list (following step 1):

### a) Open and Verify Target Conversation
- Navigate to specific conversation from your TODO list
- **CRITICAL VERIFICATION RULE**: The attached JSON file name is the 100% reliable identifier for scene number
  - **ALWAYS check the attached file icon and name** (e.g., "scene_24.json", "scene_01.json")
  - **The JSON filename gives absolute certainty** about which scene this conversation represents
  - **Chat title may contain errors** - ignore chat title, trust only the JSON filename
  - **Example**: If you see "scene_24.json" attached, this is definitively scene 24, regardless of chat title
- **VERIFY**: Check if conversation actually contains generated images
  - Look for "Image created" status or visible generated images
  - Some conversations may not have images despite being in project
  - If no image found, mark TODO as "No image - skip" and continue to next
- Ensure all images in conversation are fully loaded and visible
- Images should be displayed as complete generated artworks

### b) Count Images in Conversation
- **IMPORTANT**: Count exact number of images in the conversation
- **SINGLE IMAGE**: If conversation contains exactly 1 image → standard naming
- **MULTIPLE IMAGES**: If conversation contains 2+ images → alphabetic suffix naming

### c) Download All Images in Conversation
**For EACH image in the conversation**:
- **METHOD 1 (PREFERRED)**: Click "Download this image" button under the generated image
  - Look for button with text "Download this image" below the image
  - Button appears in the same area as Like/Dislike and Share buttons
  - This method works reliably and automatically saves with proper ChatGPT filename format
- **METHOD 2 (ALTERNATIVE)**: Right-click on generated image and select "Save image as..."
- **NOTE**: Use METHOD 1 first, only try right-click if download button is not visible or doesn't work
- **DOWNLOAD ALL**: Do not skip any images - download every single image in the conversation

**Download Button Location:**
- The "Download this image" button is located below each generated image
- It appears alongside other image interaction buttons (Like, Dislike, Share)
- Button has a download icon and "Download this image" text
- Clicking this button automatically downloads the image with ChatGPT's standard filename format

### d) Downloaded File Names and Location
- Each file will be downloaded with automatic name format: `ChatGPT-Image-[Month]-[Day]-[Year]-[Hour]-[Minute]-[Second]-[AM/PM].png`
- Example: `ChatGPT-Image-Jul-30-2025-05-37-28-PM.png`

**IMPORTANT - Download Location Check:**
Before starting downloads, check the current state:
```bash
# Check if MCP directory exists and is empty
ls -la /tmp/playwright-mcp-output/
```

**Expected behavior:**
- **BEFORE downloads**: Directory may be empty or contain old folders
- **DURING downloads**: MCP Playwright creates new folder with UTC timestamp format: `2025-07-30T12-37-32.794Z/`
- **FILES LOCATION**: All downloaded images save to: `/tmp/playwright-mcp-output/[UTC-timestamp]/`
- **FILE SIZES**: Typical size 2-3 MB per PNG image
- **TRACK DOWNLOADS**: Keep note of which downloaded file corresponds to which image position

**Example download location:**
```
/tmp/playwright-mcp-output/2025-07-30T12-37-32.794Z/ChatGPT-Image-Jul-30-2025-05-37-28-PM.png
```

## 3. File Organization

### a) Determine Book Information
- Extract book number from folder name (e.g., `0036` from `0036_treasure_island`)
- Identify scene number from conversation context (e.g., scene_01, scene_02, etc.)

### b) Create Target Directory
- Ensure target directory exists: `/home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/`
- Create directory if it doesn't exist

### c) Check Existing Files and Determine Naming
**CRITICAL**: Before moving/renaming files, check what already exists in target directory:
```bash
ls -la /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/
```

### d) Move and Rename Files with Collision Prevention
Move downloaded files from temporary location to:
```
/home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/
```

**NAMING RULES - NO OVERWRITING**:

**For FIRST image from a scene conversation:**
- **IF NO FILE EXISTS**: Use format `[book_number]_scene_[NN].png`
- **IF FILE ALREADY EXISTS**: Use format `[book_number]_scene_[NN]_a.png` (and rename existing file to `[book_number]_scene_[NN]_a.png` if needed)
- Example: If `0036_scene_01.png` exists, new image becomes `0036_scene_01_b.png`

**For ADDITIONAL images from same scene conversation:**
- Format: `[book_number]_scene_[NN]_[letter].png`
- Letters: a, b, c, d, etc. (find next available letter)
- Examples: `0036_scene_01_a.png`, `0036_scene_01_b.png`, `0036_scene_01_c.png`

**File Collision Prevention:**
- **NEVER overwrite existing files**
- Always check what files already exist for that scene
- Use next available letter in alphabetical sequence
- If `0036_scene_05.png` and `0036_scene_05_a.png` exist, use `0036_scene_05_b.png`

**Complete Examples:**
- For book "Treasure Island" (0036):
  - **Scene 01 - first image, no existing files**: `0036_scene_01.png`
  - **Scene 01 - second image downloaded later**: `0036_scene_01_a.png` (first becomes `0036_scene_01_b.png`)
  - **Scene 02 - multiple images from one conversation**: `0036_scene_02_a.png`, `0036_scene_02_b.png`, `0036_scene_02_c.png`
  - **Scene 03 - new image, but `scene_03.png` already exists**: `0036_scene_03_a.png`

### d) Verify File Operations
- Confirm file exists in target location
- Verify file size is reasonable (not 0 bytes)
- Check file opens correctly as image

## 4. Process Flow for All Images

### Pre-Download Requirements
**BEFORE starting any downloads, ensure you have:**
- ✅ Completed full project analysis (scrolled through entire conversation list)
- ✅ Created comprehensive TODO list with ALL conversations (including non-standard names)
- ✅ Included conversations with misleading titles like "Brak wygenerowanego obrazu"
- ✅ Identified conversations with multiple images per scene
- ✅ Noted non-standard conversations (resolution changes, custom prompts)
- ✅ Created target directory for downloads

### Sequential Processing by TODO List
**ONLY AFTER completing analysis above**, process each conversation with images (following TODO from step 1):

1. **Navigate** to specific ChatGPT conversation
2. **Count** all images in the conversation
3. **Download** ALL images using "Download this image" button (preferred) or right-click method
4. **Check existing files** in target directory for that scene number
5. **Move** ALL files from download location to target directory
6. **Rename** files according to naming convention with collision prevention (never overwrite existing files)
7. **Update TODO** - mark conversation as completed
8. **Verify** file integrity for all downloaded images
9. **MANDATORY: Return to project conversation list** before proceeding to next conversation
   - **METHOD 1**: Click on project name (e.g., "0019_master_and_margarita") in the sidebar
   - **METHOD 2**: Click "See All" link if visible in the project section
   - **PURPOSE**: Ensures systematic navigation through all conversations
   - **IMPORTANT**: Do not use browser back/forward - always return to project list first
10. **Proceed** to next conversation from TODO list

### Multiple Images Handling
**When conversation contains multiple images**:
- Download images in order from top to bottom of conversation
- First image gets suffix "_a"
- Second image gets suffix "_b" 
- Third image gets suffix "_c"
- Continue alphabetically as needed

### MCP Playwright Download Commands
**To download using "Download this image" button:**
```javascript
// Method 1: Click download button by button name
await page.getByRole('button', { name: 'Download this image' }).click();

// Method 2: Right-click on image (alternative)
await page.getByRole('img', { name: 'Generated image' }).first().click({ button: 'right' });
```

**Finding the download button:**
- Look for button element with text "Download this image"
- Button appears below generated image alongside Like/Dislike/Share buttons
- Button typically has ref attribute that can be identified in page snapshot
- If multiple images in conversation, each image has its own download button

### File Management Commands
```bash
# Check download location after each download session
ls -la /tmp/playwright-mcp-output/

# List downloaded files
ls -la /tmp/playwright-mcp-output/2025-07-30T12-37-32.794Z/

# Create target directory if needed
mkdir -p /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/

# CRITICAL: Check existing files before naming new ones
ls -la /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/[book_number]_scene_[NN]*

# Move and rename files - COLLISION PREVENTION EXAMPLES
# Scenario 1: No existing files for this scene
mv "/tmp/playwright-mcp-output/[timestamp]/ChatGPT-Image-Jul-30-2025-05-37-28-PM.png" "/home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/[book_number]_scene_[NN].png"

# Scenario 2: File already exists (e.g., 0019_scene_05.png exists)
mv "/tmp/playwright-mcp-output/[timestamp]/ChatGPT-Image-Jul-30-2025-05-37-28-PM.png" "/home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/[book_number]_scene_[NN]_a.png"

# Scenario 3: Multiple files exist (e.g., 0019_scene_05.png and 0019_scene_05_a.png exist)
mv "/tmp/playwright-mcp-output/[timestamp]/ChatGPT-Image-Jul-30-2025-05-37-28-PM.png" "/home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/[book_number]_scene_[NN]_b.png"

# Verify files after moving
ls -la /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/

# Clean up temporary downloads after successful move
rm -rf /tmp/playwright-mcp-output/[timestamp]/
```

## 5. Naming Convention Reference

### Single Image Format: `[book_number]_scene_[NN].png`
### Multiple Images Format: `[book_number]_scene_[NN]_[letter].png`

**Examples for different books:**

**Book 0017 (Little Prince):**
- Single: `0017_scene_01.png`, `0017_scene_03.png`
- Multiple: `0017_scene_02_a.png`, `0017_scene_02_b.png`

**Book 0019 (Master and Margarita):**
- Single: `0019_scene_01.png`, `0019_scene_04.png`
- Multiple: `0019_scene_02_a.png`, `0019_scene_02_b.png`, `0019_scene_02_c.png`

**Book 0036 (Treasure Island):**
- Single: `0036_scene_01.png`, `0036_scene_05.png`
- Multiple: `0036_scene_03_a.png`, `0036_scene_03_b.png`

### Formatting Rules
- **Scene Numbers**: Always use 2-digit format: `01`, `02`, `03`, ..., `25`
- **Never use single digits**: `1`, `2`, `3`
- **Letter Suffixes**: Use lowercase letters in order: `a`, `b`, `c`, `d`, etc.
- **Order**: Letters assigned by top-to-bottom order in conversation

## 6. Directory Structure

Expected final structure:
```
books/
  [NNNN_book_name]/
    prompts/
      genimage/         # Source JSON files (already exist)
        scene_01.json
        scene_02.json
        ...
    generated/          # Target location for downloaded images
        [NNNN]_scene_01.png              # Single image for scene 01
        [NNNN]_scene_02_a.png            # Multiple images for scene 02
        [NNNN]_scene_02_b.png
        [NNNN]_scene_03.png              # Single image for scene 03
        [NNNN]_scene_04_a.png            # Multiple images for scene 04
        [NNNN]_scene_04_b.png
        [NNNN]_scene_04_c.png
        ...
        [NNNN]_scene_25.png              # Final scene
```

## 7. Error Handling

### Common Issues and Solutions

**Issue**: Download button not visible or not working
- **Solution**: Try refreshing the page first, then use right-click method on the image instead
- **Alternative**: Use right-click on generated image and select "Save image as..."

**Issue**: File not found in expected download location
- **Solution**: Check MCP Playwright location: `/tmp/playwright-mcp-output/[timestamp]/`
- **Alternative**: Look for newest timestamp folder: `ls -la /tmp/playwright-mcp-output/`

**Issue**: Target directory doesn't exist
- **Solution**: Create directory using `mkdir -p` command

**Issue**: File already exists with same name
- **Solution**: NEVER overwrite! Use next available alphabetic suffix (a, b, c, etc.)
- **Example**: If `0019_scene_05.png` exists, name new file `0019_scene_05_a.png`

**Issue**: Downloaded file is corrupted or 0 bytes
- **Solution**: Re-download image from ChatGPT conversation

**Issue**: Conversation appears to have no image despite being in project
- **Solution**: Check thoroughly for "Image created" status, scroll through entire conversation
- **Note**: Some conversations may genuinely not contain images - mark TODO as "No image - skip"

## 8. Verification Steps

After completing all downloads:

1. **Count files**: Should have at least 25 images (one per scene minimum), possibly more if multiple images per scene
2. **Check naming**: All files follow proper format:
   - Single images: `[NNNN]_scene_[NN].png`
   - Multiple images: `[NNNN]_scene_[NN]_[letter].png`
3. **Verify completeness**: Ensure all 25 scenes are represented (some may have multiple variants)
4. **Check sizes**: All files should have reasonable sizes (typically > 100KB)
5. **Test opening**: Sample few images to ensure they're valid PNG files
6. **Validate TODO completion**: All TODO items from step 1 should be marked as completed

## 9. Completion Checklist

- [ ] TODO list created with all conversations containing images
- [ ] All conversations with images processed (some may have multiple images)
- [ ] All images downloaded from each conversation
- [ ] All files moved to correct directory
- [ ] All files renamed according to convention (single vs multiple naming)
- [ ] All 25 scenes represented (minimum 25 files, possibly more)
- [ ] All files verified as valid images
- [ ] Directory structure matches expected format
- [ ] TODO list marked as 100% complete
- [ ] No temporary files left in download locations

## Important Notes

- **TODO-driven process**: Always create and follow TODO list before starting downloads
- **Multiple images support**: Some conversations may contain 2, 3, or more images - download ALL
- **Sequential processing**: Complete each conversation fully before moving to next
- **Naming precision**: Single images use standard format, multiple images use alphabetic suffixes
- **File integrity**: Always verify downloaded files are not corrupted
- **Naming consistency**: Strict adherence to naming convention is crucial
- **Directory organization**: Maintain proper folder structure for project consistency
- **Cleanup**: Remove temporary downloaded files after successful move operations
- **Completeness**: Ensure all 25 scenes are covered, even if some have multiple variations