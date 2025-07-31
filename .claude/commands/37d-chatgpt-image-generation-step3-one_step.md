# ChatGPT AI Image Generation - Single Step Process

**AUTOMATED EXECUTION: Claude MUST execute ALL steps in EXACT ORDER using MCP playwright-headless tools to control ChatGPT browser.**

**PURPOSE**: Generate ONE AI image per execution from JSON scene file for book "[TITLE]" by "[AUTHOR]"

## CRITICAL EXECUTION RULES

1. **NEVER SKIP STEPS** - Each step must be completed before proceeding
2. **VERIFY AFTER EACH ACTION** - Confirm success before moving forward
3. **STOP ON ERROR** - Do not continue if any step fails
4. **ONE SCENE PER EXECUTION** - Process exactly one unrealized task
5. **USE EXACT MODEL** - Must use o4-mini

## EXECUTION PHASES

### Phase 1: RESEARCH & ANALYSIS
**Goal**: Understand current state and locate required files
1. Identify book folder and JSON files
2. Check TODO list status
3. Analyze available scenes

### Phase 2: PLANNING  
**Goal**: Determine exact actions and prepare ChatGPT
4. Find first unrealized task
5. Set up ChatGPT project
6. Configure correct AI model

### Phase 3: EXECUTION
**Goal**: Generate the AI image
7. Attach JSON file to conversation
8. Send generation prompt
9. Monitor generation process

### Phase 4: VERIFICATION
**Goal**: Confirm generation started and update status
10. Update TODO status
11. Confirm task initiated


## DETAILED STEP-BY-STEP EXECUTION

### STEP 1: Locate Book Directory and JSON Files

**Action**:
```bash
ls -la /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/
```

**Expected Result**: 
- Directory exists and contains JSON files
- Files named like: scene_01.json, scene_02.json, etc.

**VALIDATION CHECKPOINT**: 
- ✓ Genimage directory exists
- ✓ Contains at least one JSON file
- ✓ JSON files follow scene_NN.json naming pattern

**STOP**: Do not proceed if genimage directory is missing or empty.

### STEP 2: Check TODO List Status

**Action**:
```bash
ls -la /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/TODO-GENERATE.md
```

**Expected Result**: 
- File exists → Proceed to STEP 4
- File not found → Proceed to STEP 3

**VALIDATION CHECKPOINT**: 
- ✓ Confirmed TODO-GENERATE.md status
- ✓ Path is correct for the book

**STOP**: Do not proceed until you have confirmed the TODO list status.

### STEP 3: Create TODO List (IF NEEDED)

**Sub-step 3.1: Count JSON Files**

**Action**:
```bash
find /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/ -name "scene_*.json" | sort
```

**Expected Result**: List of all scene JSON files in numerical order

**VALIDATION CHECKPOINT**:
- ✓ Found at least one scene file
- ✓ Files follow scene_NN.json pattern
- ✓ Scene numbers are sequential (01, 02, 03...)

**Sub-step 3.2: Create TODO File**

**Action**:
1. Create new file: `/home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/TODO-GENERATE.md`
2. Add EACH JSON file as a separate line

**Format Requirements**:
```
[ ] Generate image using scene_01.json
[ ] Generate image using scene_02.json
[ ] Generate image using scene_03.json
```

**VALIDATION CHECKPOINT**:
- ✓ File created successfully
- ✓ Contains ALL JSON files (verify count matches)
- ✓ Each line has `[ ]` prefix
- ✓ Each line references correct JSON filename

### STEP 4: Find First Unrealized Task

**Action**:
```bash
grep -n "^\[ \]" /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/TODO-GENERATE.md | head -1
```

**Expected Result**:
- Line number and task description
- Example: `2:[ ] Generate image using scene_02.json`

**VALIDATION CHECKPOINT**:
- ✓ Found at least one uncompleted task
- ✓ Task line starts with `[ ]`
- ✓ JSON filename extracted successfully
- ✓ Noted line number for later update

**STOP**: If no tasks found (all completed), report completion and exit.

### STEP 5: Set Up ChatGPT Project

**Sub-step 5.1: Navigate to ChatGPT**

**Action**:
1. Open browser to ChatGPT
2. Take initial snapshot to verify page loaded

**VALIDATION CHECKPOINT**:
- ✓ ChatGPT page loaded correctly
- ✓ Can see left sidebar with projects
- ✓ Interface is responsive

**CRITICAL ERROR HANDLING - CloudFlare/CAPTCHA Detection**:
If CloudFlare protection page or CAPTCHA appears:
1. **IMMEDIATELY take screenshot** using browser screenshot tool
2. **ABORT the task** - do not attempt to bypass
3. **Report**: "CloudFlare/CAPTCHA detected - task terminated, screenshot saved"
4. **EXIT** without updating TODO status

**Sub-step 5.2: Check/Create Project**

**CRITICAL**: Project name MUST match book folder exactly!

**Action**:
1. Look for existing project with name `[BOOK_FOLDER]`
2. If project exists: Click on it
3. If project doesn't exist: Create new project

**To Create New Project**:
1. Click "New project" in left sidebar
2. Enter project name exactly as `[BOOK_FOLDER]` (e.g., "0036_treasure_island")
3. Press Enter to create

**VALIDATION CHECKPOINT**:
- ✓ Project exists with correct name
- ✓ Currently in the correct project
- ✓ Project name matches book folder exactly

### STEP 6: Configure AI Model

**CRITICAL**: Must use o4-mini - other models may not work correctly!

**Action**:
1. Look for model selector in top-left (shows current model like "ChatGPT 4o")
2. **ONLY IF model is NOT o4-mini**: Click on the model selector
3. **IF needed**: Select "o4-mini" from dropdown list
4. **IF model already shows o4-mini**: Skip clicking - proceed directly to STEP 7

**VALIDATION CHECKPOINT**:
- ✓ Model shows o4-mini in the interface
- ✓ No need to change if already correct
- ✓ Do NOT click model selector if it already shows o4-mini

**STOP**: Do not proceed with wrong model - images may not generate correctly.

**IMPORTANT**: If you can see "o4-mini" in the model selector, do NOT click it - just verify and continue!

### STEP 7: Attach JSON File

**Sub-step 7.1: Prepare File Attachment**

**Action**:
1. Click "+" (plus) button at bottom of chat window
2. Select "Add photos & files" from menu
3. File dialog opens

**VALIDATION CHECKPOINT**:
- ✓ File upload dialog opened
- ✓ Can navigate filesystem
- ✓ Dialog is functional

**Sub-step 7.2: Select JSON File**

**CRITICAL**: Select the EXACT JSON file from the TODO task!

**Action**:
1. Navigate to: `/home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/`
2. Select the JSON file for current task (e.g., `scene_02.json`)
3. Click "Open" or confirm selection

**VALIDATION CHECKPOINT**:
- ✓ Navigated to correct directory
- ✓ Selected correct JSON file
- ✓ File attachment confirmed in chat

### STEP 8: Configure Generation Prompt

**Sub-step 8.1: Extract Scene Number**

**Action**:
1. From JSON filename (e.g., `scene_02.json`), extract scene number: `02`
2. Save this for prompt construction

**Sub-step 8.2: Type Generation Prompt**

**CRITICAL**: Use EXACT prompt format!

**Prompt Template**:
```
scene_[NN] - create an image based on the scene, style, and visual specifications described in the attached JSON. The JSON is a blueprint, not the content.
```

**Example for scene_02.json**:
```
scene_02 - create an image based on the scene, style, and visual specifications described in the attached JSON. The JSON is a blueprint, not the content.
```

**Action**:
1. Type the prompt with correct scene number
2. Double-check scene number matches JSON file
3. Verify prompt text is exactly as template

**VALIDATION CHECKPOINT**:
- ✓ Prompt typed correctly
- ✓ Scene number matches JSON file
- ✓ Template format followed exactly

### STEP 9: Select Image Creation Tool

**Action**:
1. Click "Choose tool" button (left side of text field)
2. From dropdown menu select "Create image"
3. Verify "Create image" is selected/highlighted

**VALIDATION CHECKPOINT**:
- ✓ Tool selector opened
- ✓ "Create image" option found
- ✓ "Create image" tool selected

**STOP**: Do not proceed without "Create image" tool selected.

### STEP 10: Initiate Generation

**Action**:
1. Click send button (arrow icon) to submit prompt
2. Immediately start monitoring for generation start

**Expected Result**:
- Message sent successfully
- ChatGPT begins processing
- Wait for "Getting started" button to appear (disabled status)

**VALIDATION CHECKPOINT**:
- ✓ Prompt sent successfully
- ✓ No error messages appeared
- ✓ Generation process started

### STEP 11: Confirm Generation Started

**CRITICAL**: We only verify that generation STARTED, not that it completed!

**Sub-step 11.1: Wait for Generation to Start**

**CRITICAL**: Execute this exact Bash command to wait 60 seconds!

**Action**:
Execute: `Bash(sleep 60)` 

**Purpose**: Wait 60 seconds for ChatGPT to initialize generation process

**Sub-step 11.2: Check for "Getting Started" Status**

**Action**:
1. Take snapshot of ChatGPT page after 60-second wait
2. Look for generation start indicators:
   - "Getting started" button (disabled status)
   - "Thought for X seconds" message
   - No immediate error messages

**Success Indicators** (Generation Started):
- "Getting started" button visible and disabled
- May show "Thought for X seconds" before "Getting started"
- No error messages appeared

**Sub-step 11.3: Handle Generation Timeout**

**If "Getting started" NOT found after 60 seconds**:

**Action**:
1. Reload the page using Playwright refresh function
2. Execute: `Bash(sleep 30)` to wait additional 30 seconds after reload
3. Take another snapshot
4. Check again for "Getting started" status

**Recovery Commands**:
1. Use Playwright page reload/refresh
2. Execute: `Bash(sleep 30)`

**Final Decision**:
- If "Getting started" appears after reload: Continue to STEP 12
- If "Getting started" still missing after reload: ABORT process

**VALIDATION CHECKPOINT**:
- ✓ "Getting started" button appeared and is disabled
- ✓ No immediate error messages
- ✓ ChatGPT is processing the request

**STOP**: If generation failed to start after reload, do NOT update TODO - report error and exit process.

### STEP 12: Update TODO Status

**Sub-step 12.1: Mark Task Complete**

**CRITICAL**: Update TODO only after confirming generation STARTED (not completed)!

**Action**:
1. Use line number saved from STEP 4
2. Update specific line in TODO file

**Command** (where N is line number):
```bash
sed -i 'Ns/^\[ \]/[x]/' /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/TODO-GENERATE.md
```

**VALIDATION CHECKPOINT**:
- ✓ TODO file updated successfully
- ✓ Only one line changed
- ✓ Task now shows `[x]`
- ✓ Other tasks unchanged

## FINAL VERIFICATION

### STEP 13: Complete Execution Verification

**Action**:
1. Verify generation started successfully in ChatGPT
2. Check TODO status updated correctly
3. Confirm single task initiated

**Verification Commands**:
```bash
# Check TODO update
grep -n "^\[x\].*scene_[0-9][0-9]\.json" /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/TODO-GENERATE.md

# Progress report
echo "Completed: $(grep -c '^\[x\]' TODO-GENERATE.md)"
echo "Remaining: $(grep -c '^\[ \]' TODO-GENERATE.md)"
```

**SUCCESS CRITERIA**:
- ✓ Generation started in ChatGPT (shows "Getting started" disabled button)
- ✓ TODO shows task as completed `[x]`
- ✓ Correct JSON file was processed
- ✓ Proper model (o4-mini) was used

## ERROR RECOVERY PROCEDURES

### Common Issues and Solutions

**ERROR: JSON file not found**
- **RECOVERY**: Verify book folder path and genimage directory
- **CHECK**: Ensure JSON files exist and follow naming pattern

**ERROR: Project creation failed**
- **RECOVERY**: Try refreshing ChatGPT page and retry
- **FALLBACK**: Use existing project if available

**ERROR: Model not available**
- **RECOVERY**: Use GPT-4o as fallback if o4-mini unavailable

**ERROR: Image generation failed to start**
- **RECOVERY**: Wait 60 seconds, then reload page if no "Getting started"
- **RETRY**: Check once more after page reload (additional 30 seconds)
- **ABORT**: If still no "Getting started" after reload, exit without TODO update

**ERROR: File attachment failed**
- **RECOVERY**: Refresh page and retry attachment
- **CHECK**: Verify file permissions and path access

## EXECUTION SUMMARY

### Complete Process Flow
```
START
  ├─→ Check JSON files exist (STEP 1)
  ├─→ Check TODO exists? (STEP 2)
  │     ├─ NO → Create TODO (STEP 3)
  │     └─ YES → Continue
  ├─→ Find first [ ] task (STEP 4)
  ├─→ Set up ChatGPT project (STEP 5)
  ├─→ Configure AI model (STEP 6)
  ├─→ Attach JSON file (STEP 7)
  ├─→ Send generation prompt (STEP 8-10)
  ├─→ Wait 60s + Monitor generation (STEP 11)
  │     ├─ "Getting started" found? → Continue
  │     └─ No "Getting started"? → Reload page + wait 30s
  │         ├─ Found after reload? → Continue  
  │         └─ Still missing? → ABORT
  ├─→ Update TODO (STEP 12)
  └─→ Verify success (STEP 13)
END
```

### Key Principles
1. **ONE SCENE PER EXECUTION** - Never process multiple scenes
2. **VERIFY EACH STEP** - Confirm success before proceeding
3. **EXACT MODEL REQUIRED** - Must use o4-mini
4. **PRECISE PROMPTS** - Use exact template format
5. **COMPLETE VALIDATION** - Check results at every stage

## CRITICAL REMINDERS

⚠️ **NEVER SKIP VALIDATION CHECKPOINTS**
⚠️ **ALWAYS USE o4-mini MODEL**
⚠️ **USE EXACT PROMPT TEMPLATE FORMAT**
⚠️ **ATTACH CORRECT JSON FILE FOR TASK**
⚠️ **PROCESS ONLY ONE SCENE PER EXECUTION**
⚠️ **WAIT 60 SECONDS + VERIFY "GETTING STARTED" BEFORE TODO UPDATE**
⚠️ **IF NO "GETTING STARTED" AFTER 60s: RELOAD PAGE + WAIT 30s MORE**
⚠️ **IF STILL MISSING AFTER RELOAD: ABORT WITHOUT TODO UPDATE**