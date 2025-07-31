# ChatGPT Image Download - Single Step Process

**AUTOMATED EXECUTION: Claude MUST execute ALL steps in EXACT ORDER using MCP playwright-headless tools and file operations.**

**PURPOSE**: Download ONE image per execution from ChatGPT conversations for book "[TITLE]" by "[AUTHOR]"

## CRITICAL EXECUTION RULES

1. **NEVER SKIP STEPS** - Each step must be completed before proceeding
2. **VERIFY AFTER EACH ACTION** - Confirm success before moving forward  
3. **STOP ON ERROR** - Do not continue if any step fails
4. **ONE TASK PER EXECUTION** - Process exactly one unrealized task

## EXECUTION PHASES

### Phase 1: RESEARCH & ANALYSIS
**Goal**: Understand current state and what needs to be done
1. Check if TODO list exists
2. Analyze existing files
3. Document findings

### Phase 2: PLANNING  
**Goal**: Determine exact actions needed
4. If no TODO: Plan TODO creation
5. Identify first unrealized task
6. Define success criteria

### Phase 3: EXECUTION
**Goal**: Perform the actual download task
7. Navigate to correct conversation
8. Download image(s)
9. Process and rename files

### Phase 4: VERIFICATION
**Goal**: Ensure task completed successfully
10. Verify files saved correctly
11. Update TODO status
12. Confirm no data loss

## DETAILED STEP-BY-STEP EXECUTION

### STEP 1: Check TODO List Status

**Action**:
```bash
ls -la /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md
```

**Expected Result**: 
- File exists → Proceed to STEP 3
- File not found → Proceed to STEP 2

**VALIDATION CHECKPOINT**: 
- ✓ Confirmed TODO-DOWNLOAD.md status
- ✓ Path is correct for the book
- ✓ No permission errors

**STOP**: Do not proceed until you have confirmed the TODO list status.

### STEP 2: Create TODO List (IF NEEDED)

**Sub-step 2.1: Navigate to ChatGPT Project**

**Action**:
1. Open browser to ChatGPT
2. Navigate to project for book "[TITLE]"
3. Take initial snapshot to verify correct project

**VALIDATION CHECKPOINT**:
- ✓ Correct project opened
- ✓ Can see conversation list
- ✓ Project name matches book title

**CRITICAL ERROR HANDLING - CloudFlare/CAPTCHA Detection**:
If CloudFlare protection page or CAPTCHA appears:
1. **IMMEDIATELY take screenshot** using browser screenshot tool
2. **ABORT the task** - do not attempt to bypass
3. **Report**: "CloudFlare/CAPTCHA detected - task terminated, screenshot saved"
4. **EXIT** without updating TODO status

**Sub-step 2.2: Load ALL Conversations**

**CRITICAL**: The page uses DYNAMIC LOADING - conversations appear as you scroll!

**Action**:
1. Start scrolling down the conversation list
2. **CONTINUE SCROLLING** until you see "scene_01" in a conversation
3. Take snapshot after each scroll to track progress
4. Count total conversations found

**Success Criteria**:
- Found conversation with "scene_01" (indicates end of list)
- All scene numbers from 01 to 25 are visible
- No more conversations load when scrolling

**STOP**: Do NOT proceed until you have scrolled to the very END and see scene_01!

**Sub-step 2.3: Create TODO File**

**Action**:
1. Create new file: `/home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md`
2. Add EACH conversation as a separate line
3. Use EXACT chat names from ChatGPT (not generic descriptions)

**Format Requirements**:
```
[ ] [Exact conversation title from ChatGPT]
```

**Example (CORRECT)**:
```
[ ] Create image from JSON scene_25 - create an image based on the scene, style, and visual specifications described in the attached JSON. The JSON is a blueprint, not the content.
[ ] Wygeneruj obraz z tym samym promptem, zmien tylko rozdzielczosc na 1024 × 1792 px
[ ] Brak wygenerowanego obrazu obraz sie nie wygenerował
```

**Example (WRONG - Do NOT use generic descriptions)**:
```
[ ] Check and download from scene_25 conversation
[ ] Download image for scene 24
```

**VALIDATION CHECKPOINT**:
- ✓ File created successfully
- ✓ Contains ALL conversations (verify count)
- ✓ Each line has `[ ]` prefix
- ✓ Using REAL chat names, not generic text

### STEP 3: Find First Unrealized Task

**Action**:
```bash
grep -n "^\[ \]" /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md | head -1
```

**Expected Result**:
- Line number and task description
- Example: `2:[ ] Create image from JSON scene_24 - create an image...`

**VALIDATION CHECKPOINT**:
- ✓ Found at least one uncompleted task
- ✓ Task line starts with `[ ]`
- ✓ Noted line number for later update

**STOP**: If no tasks found (all completed), report completion and exit.

### STEP 4: Navigate to Specific Conversation

**Sub-step 4.1: Open Conversation**

**Action**:
1. Click on the conversation matching the task description
2. Wait for conversation to fully load
3. Take snapshot to verify correct conversation

**VALIDATION CHECKPOINT**:
- ✓ Conversation title matches TODO task
- ✓ Can see attached JSON files
- ✓ Images are visible in conversation

**Sub-step 4.2: Verify Scene Number**

**CRITICAL**: Check the attached JSON filename to confirm scene number!

**Action**:
1. Look for attached file like `scene_XX.json`
2. Extract scene number (XX)
3. Confirm it matches expected scene from task

**Success Criteria**:
- JSON filename visible
- Scene number extracted correctly
- Matches task description

### STEP 5: Download Image(s)

**Sub-step 5.1: Count Images**

**Action**:
1. Count total number of images in conversation
2. Note if multiple images exist
3. Plan naming strategy if multiple

**Sub-step 5.2: Download Each Image**

**Action**:
1. Locate "Download this image" button below FIRST image
2. Click the download button
3. Wait for download to complete
4. Repeat for any additional images

**VALIDATION CHECKPOINT**:
- ✓ Download initiated successfully
- ✓ No error messages appeared
- ✓ Browser shows download completed

**Alternative Method** (if button fails):
1. Right-click on image
2. Select "Save image as..."
3. Save with temporary name

### STEP 6: File Management and Naming

**Sub-step 6.1: Locate Downloaded File**

**Action**:
```bash
ls -la /tmp/playwright-mcp-output/*/
```

**Expected**: Find file like `ChatGPT-Image.png` with recent timestamp

**Sub-step 6.2: Check for Existing Files**

**CRITICAL**: Never overwrite existing files!

**Action**:
```bash
ls -la /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/[book_number]_scene_[XX]*
```

**Naming Decision Tree**:
- No existing files → Use: `[book_number]_scene_[XX].png`
- File exists → Use: `[book_number]_scene_[XX]_a.png`
- Multiple exist → Use next letter: b, c, d, etc.

**Sub-step 6.3: Move and Rename**

**Action**:
```bash
mv "/tmp/playwright-mcp-output/[timestamp]/ChatGPT-Image.png" \
   "/home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/[final_name].png"
```

**VALIDATION CHECKPOINT**:
- ✓ File moved successfully
- ✓ No existing files overwritten
- ✓ Correct naming convention used
- ✓ File permissions are readable

### STEP 7: Update TODO Status

**Sub-step 7.1: Mark Task Complete**

**Action**:
1. Read entire TODO file into memory
2. Find the specific line (use line number from STEP 3)
3. Replace `[ ]` with `[x]` on that exact line
4. Write updated content back to file

**Command** (where N is line number):
```bash
sed -i 'Ns/^\[ \]/[x]/' /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md
```

**VALIDATION CHECKPOINT**:
- ✓ TODO file updated successfully
- ✓ Only one line changed
- ✓ Task now shows `[x]`
- ✓ Other tasks unchanged

## FINAL VERIFICATION

### STEP 8: Complete Execution Verification

**Action**:
1. Verify downloaded file exists in target location
2. Check TODO status updated correctly
3. Confirm no data loss or overwrites

**Verification Commands**:
```bash
# Verify file exists and is valid
file /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/[final_name].png

# Check TODO update
grep -n "^\[x\].*[task_description]" /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md

# Progress report
echo "Completed: $(grep -c '^\[x\]' TODO-DOWNLOAD.md)"
echo "Remaining: $(grep -c '^\[ \]' TODO-DOWNLOAD.md)"
```

**SUCCESS CRITERIA**:
- ✓ Image file exists and is valid PNG
- ✓ TODO shows task as completed `[x]`
- ✓ No existing files were overwritten
- ✓ Proper naming convention followed

## ERROR RECOVERY PROCEDURES

### Common Issues and Solutions

**ERROR: TODO file not found**
- **RECOVERY**: Return to STEP 2 to create TODO list
- **PREVENTION**: Always check file existence first

**ERROR: All tasks already completed**
- **RECOVERY**: Report "All tasks completed" and exit gracefully
- **VERIFICATION**: Show completion statistics

**ERROR: Download button not found**
- **RECOVERY**: Use alternative right-click method
- **FALLBACK**: Take screenshot and report issue

**ERROR: File naming collision**
- **RECOVERY**: Use next available letter suffix (a, b, c...)
- **NEVER**: Overwrite existing files

**ERROR: Scene number mismatch**
- **RECOVERY**: Double-check JSON attachment
- **ACTION**: Report discrepancy and skip task

## EXECUTION SUMMARY

### Complete Process Flow
```
START
  ├─→ Check TODO exists?
  │     ├─ NO → Create TODO (STEP 2)
  │     └─ YES → Continue
  ├─→ Find first [ ] task (STEP 3)
  ├─→ Navigate to conversation (STEP 4)
  ├─→ Download image(s) (STEP 5)
  ├─→ Process files (STEP 6)
  ├─→ Update TODO (STEP 7)
  └─→ Verify success (STEP 8)
END
```

### Key Principles
1. **ONE TASK PER EXECUTION** - Never process multiple tasks
2. **VERIFY EACH STEP** - Confirm success before proceeding
3. **PRESERVE DATA** - Never overwrite existing files
4. **EXACT NAMING** - Use real ChatGPT conversation titles
5. **COMPLETE VALIDATION** - Check results at every stage

## CRITICAL REMINDERS

⚠️ **NEVER SKIP VALIDATION CHECKPOINTS**
⚠️ **ALWAYS SCROLL TO scene_01 WHEN CREATING TODO**
⚠️ **USE EXACT CONVERSATION NAMES FROM CHATGPT**
⚠️ **NEVER OVERWRITE EXISTING FILES**
⚠️ **PROCESS ONLY ONE TASK PER EXECUTION**