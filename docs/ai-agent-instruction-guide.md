# AI Agent Instruction Guide

A comprehensive guide for writing effective instructions that ensure AI agents execute tasks accurately and completely.

## Table of Contents

1. [Introduction](#introduction)
2. [Core Principles](#core-principles)
3. [Formatting and Structure](#formatting-and-structure)
4. [Common Mistakes to Avoid](#common-mistakes-to-avoid)
5. [Examples of Poor Instructions](#examples-of-poor-instructions)
6. [Examples of Effective Instructions](#examples-of-effective-instructions)
7. [Error Prevention Techniques](#error-prevention-techniques)
8. [Universal Template](#universal-template)
9. [Instruction Verification Checklist](#instruction-verification-checklist)

## Introduction

Well-crafted instructions are the foundation of reliable AI agent performance. This guide provides proven techniques for writing instructions that AI agents will follow precisely, reducing errors and ensuring consistent results.

### Why Instructions Matter

AI agents lack human intuition and common sense. They:
- Execute exactly what's written, not what's implied
- Don't recognize when something "feels wrong"
- Can't infer missing steps or context
- Will continue even when encountering errors (unless told otherwise)

## Core Principles

### 1. Be Explicit and Specific

**❌ Poor**: "Download the images"
**✅ Good**: "Download each image by clicking the 'Download this image' button located below each image"

### 2. Break Complex Tasks into Steps

**❌ Poor**: "Process the ChatGPT conversation and save the images"
**✅ Good**: 
```
1. Navigate to the conversation
2. Count the number of images
3. Download each image individually
4. Rename according to naming convention
5. Move to target directory
```

### 3. Add Validation Checkpoints

Every major step should include verification:
```markdown
**VALIDATION CHECKPOINT**:
- ✓ File downloaded successfully
- ✓ File size > 0 bytes
- ✓ File format is PNG
```

### 4. Use Clear Stop Points

```markdown
**STOP**: Do not proceed until you have verified the file exists.
```

### 5. Define Success Criteria

```markdown
**Success Criteria**:
- All 25 images downloaded
- No existing files overwritten
- TODO list updated
```

## Formatting and Structure

### Use Hierarchical Organization

```markdown
## Phase 1: Research
### Step 1: Analyze Current State
**Action**: [Specific action]
**Expected Result**: [What should happen]
**Validation**: [How to verify]
```

### Leverage Markdown Features

- **Bold** for emphasis: **CRITICAL**, **IMPORTANT**
- `Code blocks` for commands
- Numbered lists for sequential steps
- Bullet points for non-sequential items
- Checkboxes for validation items

### Visual Hierarchy Example

```markdown
# Main Task

## Phase 1: Preparation
### STEP 1: Check Prerequisites
**CRITICAL**: This step must be completed first!

**Action**:
1. Check system requirements
2. Verify permissions

**Validation Checkpoint**:
- ✓ All requirements met
- ✓ Permissions verified

**STOP**: Do not proceed if validation fails.
```

## Common Mistakes to Avoid

### 1. Ambiguous Instructions

**❌ Poor**:
```
"Handle the images appropriately"
```

**✅ Good**:
```
"Download each image using the 'Download this image' button, rename to 
[book_number]_scene_[XX].png format, and move to the generated/ directory"
```

### 2. Missing Context

**❌ Poor**:
```
"Create a TODO list"
```

**✅ Good**:
```
"Create a TODO list by:
1. Navigating to ChatGPT project [PROJECT_NAME]
2. Scrolling through ALL conversations until scene_01 is visible
3. Creating a file with each conversation as a checkbox item"
```

### 3. Assuming Prior Knowledge

**❌ Poor**:
```
"Use the standard naming convention"
```

**✅ Good**:
```
"Use naming convention: [book_number]_scene_[XX].png
Where:
- [book_number] = 4-digit book ID (e.g., 0019)
- [XX] = 2-digit scene number (e.g., 05)"
```

## Examples of Poor Instructions

### Example 1: Vague Process

```markdown
# Download Images

Go to ChatGPT and download all the images for the book.
Save them with appropriate names.
```

**Problems**:
- No specific navigation instructions
- "Appropriate names" is undefined
- No verification steps
- No error handling

### Example 2: Missing Validation

```markdown
1. Open the conversation
2. Download the image
3. Move to folder
4. Update TODO
```

**Problems**:
- No verification between steps
- No check if download succeeded
- No collision detection
- No confirmation of updates

### Example 3: Incomplete Error Handling

```markdown
If the download fails, try again.
```

**Problems**:
- No specific recovery steps
- No limit on retries
- No alternative methods
- No reporting mechanism

## Examples of Effective Instructions

### Example 1: Clear Sequential Process

```markdown
### STEP 1: Navigate to Conversation

**Prerequisite**: TODO list must exist and contain at least one uncompleted task

**Action**:
1. Read first uncompleted task from TODO.md
2. Extract conversation title
3. Click on matching conversation in ChatGPT
4. Wait for page to fully load (2 seconds)

**Expected Result**:
- Conversation open
- Images visible
- YAML attachment visible

**Validation Checkpoint**:
- ✓ Conversation title matches TODO task
- ✓ At least one image present
- ✓ YAML file attached with scene_XX.yaml name

**Error Recovery**:
- If conversation not found: Skip task and report
- If no images: Mark task with [ERROR] prefix
- If page timeout: Refresh and retry once

**STOP**: Do not proceed to download until all validation checks pass.
```

### Example 2: Robust File Handling

```markdown
### STEP 5: Process Downloaded File

**Context**: File downloaded to /tmp/playwright-mcp-output/

**Action**:
1. Locate downloaded file:
   ```bash
   find /tmp/playwright-mcp-output -name "*.png" -mmin -1
   ```

2. Determine target filename:
   - Extract scene number from TODO task
   - Check existing files:
     ```bash
     ls -la generated/0019_scene_[XX]*.png
     ```
   - Apply naming rules:
     - No existing: 0019_scene_XX.png
     - Exists: 0019_scene_XX_a.png
     - Multiple: Use next letter (b, c, d...)

3. Move and rename:
   ```bash
   mv "$SOURCE_FILE" "generated/$TARGET_NAME"
   ```

**Validation**:
```bash
file "generated/$TARGET_NAME" | grep -q "PNG image data"
```

**Success Criteria**:
- ✓ File exists in generated/
- ✓ File is valid PNG
- ✓ No files overwritten
- ✓ Naming convention followed
```

### Example 3: State Management

```markdown
### STEP 7: Update Task Status

**CRITICAL**: Only update after successful file save!

**Current State**:
- Task line number: [SAVED_FROM_STEP_3]
- Task description: [SAVED_FROM_STEP_3]
- File saved as: [SAVED_FROM_STEP_6]

**Action**:
1. Create backup of TODO.md:
   ```bash
   cp TODO.md TODO.md.backup
   ```

2. Update specific line:
   ```bash
   sed -i '${LINE_NUMBER}s/^\[ \]/[x]/' TODO.md
   ```

3. Verify update:
   ```bash
   diff TODO.md.backup TODO.md
   ```

**Expected Diff**:
```diff
< [ ] Create image from JSON scene_24 - create an image...
> [x] Create image from JSON scene_24 - create an image...
```

**Rollback on Error**:
```bash
mv TODO.md.backup TODO.md
```
```

## Error Prevention Techniques

### 1. Circuit Breakers

```markdown
**CIRCUIT BREAKER**: Maximum 3 retry attempts
- Attempt 1: Standard method
- Attempt 2: Alternative method
- Attempt 3: Fallback method
- After 3 failures: Report error and skip task
```

### 2. Validation Gates

```markdown
**VALIDATION GATE**: Before proceeding to Phase 2
□ All prerequisites verified
□ Required files exist
□ No pending errors
□ User confirmation received (if needed)

IF ANY UNCHECKED: Return to Phase 1
```

### 3. State Preservation

```markdown
**STATE TRACKING**:
Save these values for later steps:
- TASK_LINE_NUMBER = [from grep result]
- SCENE_NUMBER = [from JSON filename]  
- DOWNLOAD_PATH = [from download location]
- TARGET_FILENAME = [calculated name]
```

### 4. Explicit Boundaries

```markdown
**SCOPE BOUNDARIES**:
- Process ONLY conversations with scene_XX.yaml attachments
- Download ONLY PNG/JPG images
- Modify ONLY the specific TODO line
- Create files ONLY in generated/ directory
```

## Universal Template

Use this template as a starting point for new agent instructions:

```markdown
# [Task Name]

**PURPOSE**: [One sentence description]

**SCOPE**: [What this does and doesn't do]

## CRITICAL RULES
1. [Most important rule]
2. [Second most important]
3. [Third most important]

## PREREQUISITES
- [ ] [Required condition 1]
- [ ] [Required condition 2]

## PHASE 1: RESEARCH & ANALYSIS
**Goal**: [What this phase accomplishes]

### STEP 1: [Step Name]
**Action**:
1. [Specific action]
2. [Specific action]

**Expected Result**:
- [What should happen]

**Validation Checkpoint**:
- ✓ [Verification item]
- ✓ [Verification item]

**STOP**: [Condition that prevents continuation]

## PHASE 2: PLANNING
[Similar structure...]

## PHASE 3: EXECUTION
[Similar structure...]

## PHASE 4: VERIFICATION
[Similar structure...]

## ERROR RECOVERY

### [Error Type 1]
**Symptoms**: [How to recognize]
**Recovery**: [What to do]
**Prevention**: [How to avoid]

## SUCCESS CRITERIA
- [ ] [Measurable outcome 1]
- [ ] [Measurable outcome 2]
- [ ] [Measurable outcome 3]
```

## Instruction Verification Checklist

Before finalizing any agent instruction document, verify:

### Structure
- [ ] Clear phases/steps hierarchy
- [ ] Numbered steps in sequence  
- [ ] Consistent formatting throughout
- [ ] Proper use of Markdown

### Content
- [ ] Specific, unambiguous actions
- [ ] Validation after each major step
- [ ] Explicit success criteria
- [ ] Error recovery procedures
- [ ] No assumed knowledge

### Safety
- [ ] Circuit breakers defined
- [ ] Stop conditions clear
- [ ] Data preservation rules
- [ ] Scope boundaries set

### Completeness
- [ ] All edge cases addressed
- [ ] Examples provided
- [ ] Commands include full syntax
- [ ] File paths are absolute

### Testing
- [ ] Dry run performed
- [ ] Error scenarios tested
- [ ] Validation gates work
- [ ] Recovery procedures verified

## Conclusion

Effective AI agent instructions require:
1. **Clarity** - No ambiguity or assumptions
2. **Structure** - Logical flow with clear phases
3. **Validation** - Checkpoints at every step
4. **Recovery** - Explicit error handling
5. **Boundaries** - Clear scope and limits

Remember: AI agents execute exactly what's written. Make your instructions so clear that there's only one way to interpret them, and include enough validation that errors are caught immediately rather than propagating through the system.