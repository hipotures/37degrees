# ChatGPT Image Generation - Test Plan

**Version:** 1.0
**Created:** 2025-10-09
**Purpose:** Standalone Playwright automation for uploading YAML scenes to ChatGPT and generating images

---

## Overview

This test plan describes the automation workflow for uploading scene YAML files to ChatGPT (o4-mini model) and initiating image generation. The script must be **universal** and **parameterized** - not tied to any specific book or scene.

## Parameters

```typescript
interface UploadParams {
  bookFolder: string;      // e.g., "0016_lalka" (books) or "m00001_media" (media)
  sceneFile: string;       // e.g., "scene_01.yaml"
  projectId?: string;      // optional, e.g., "68b7e9551f8081919511b1ce73c242ca"
}

interface UploadResult {
  success: boolean;
  threadId?: string;       // e.g., "abc123-def456-..."
  error?: string;
  errorType?: 'policy' | 'limit' | 'network' | 'unknown';
}
```

**CLI Invocation:**
```bash
npx ts-node scripts/chatgpt/upload-scene.ts <folder> <sceneFile> [projectId]
```

**Examples:**
```bash
# Books (starts with digit → books/)
npx ts-node scripts/chatgpt/upload-scene.ts 0016_lalka scene_01.yaml

# Media (starts with 'm' → media/)
npx ts-node scripts/chatgpt/upload-scene.ts m00001_media scene_01.yaml
```

---

## Preconditions

### Required
- ✅ User is logged into ChatGPT Plus account (persistent browser profile)
- ✅ ChatGPT Plus subscription is active (not at usage limit)
- ✅ YAML file exists at:
  - Books: `/home/xai/DEV/37degrees/books/{folder}/prompts/genimage/{sceneFile}`
  - Media: `/home/xai/DEV/37degrees/media/{folder}/prompts/genimage/{sceneFile}`
- ✅ Playwright browser is installed (chromium)

### Optional
- 📁 `generated/` directory exists at: `/home/xai/DEV/37degrees/{books|media}/{folder}/generated/`
- 🔑 Project ID is known (if reusing existing ChatGPT project)

**Note:** Script auto-detects folder type by checking if name starts with 'm' (media) or digit (books)

---

## Test Scenario: Upload Scene and Generate Image

### Phase 1: Browser Setup

**Step 1.1: Launch Browser**
- Launch Chromium with **persistent user data directory** (to maintain login)
- User data dir: `~/.cache/chatgpt-playwright-profile/`
- Viewport: 1280x720 (standard desktop)
- Headless: false (initially, can be changed to true after testing)

**Step 1.2: Verify Login State**
- Navigate to: `https://chatgpt.com/`
- Wait for page load (networkidle)
- Check if logged in:
  - ✅ Logged in: Main chat interface visible
  - ❌ Not logged in: Login screen visible → ERROR: "User not logged in"

---

### Phase 2: Project Navigation

**Critical Notes:**
- ChatGPT project IDs can be:
  - Short format: `68b7e9551f8081919511b1ce73c242ca`
  - Long format: `g-p-68b7e9551f8081919511b1ce73c242ca`
- Always prepend `g-p-` if not present
- Project URL format: `https://chatgpt.com/g/g-p-{projectId}/project?model=o4-mini`

**Step 2.1: Navigate to Project (if projectId provided)**

If `projectId` is provided:
```typescript
const fullProjectId = projectId.startsWith('g-p-')
  ? projectId
  : `g-p-${projectId}`;

const projectUrl = `https://chatgpt.com/g/${fullProjectId}/project?model=o4-mini`;
await page.goto(projectUrl, { waitUntil: 'networkidle' });
```

Verify project loaded:
- Check URL contains `/project`
- Check page title or heading contains project name (optional)

**Step 2.2: Create New Project (if projectId NOT provided)**

If `projectId` is NOT provided:

1. Navigate to: `https://chatgpt.com/?model=o4-mini`
2. Wait for page load
3. **Open sidebar**:
   - Selector strategy: `button` with aria-label containing "sidebar" OR text "Menu"
   - Click button
   - Wait for sidebar to open (element with projects list visible)

4. **Check if project exists**:
   - Search sidebar for project name matching `bookFolder`
   - If found: Click project → skip to Step 2.3
   - If NOT found: Continue to create new project

5. **Create new project**:
   - Selector strategy: Button with text "New project" OR similar
   - Click "New project"
   - Wait for project name input field
   - Type project name: `bookFolder` (e.g., "0016_lalka")
   - Press Enter OR click "Create"
   - Wait for navigation to project page

6. **Extract Project ID**:
   ```typescript
   const url = page.url();
   const projectIdMatch = url.match(/\/g\/(g-p-[a-z0-9-]+)/);
   const newProjectId = projectIdMatch ? projectIdMatch[1] : null;

   if (!newProjectId) {
     throw new Error('Failed to extract project ID from URL');
   }

   // Return this ID so it can be saved for future use
   console.log(JSON.stringify({ projectId: newProjectId }));
   ```

**Step 2.3: Verify Model is o4-mini**

ChatGPT may switch models. Ensure o4-mini is selected:
- Check for model selector dropdown
- If current model ≠ "o4-mini": Click model selector → Select "o4-mini"

---

### Phase 3: Attach YAML File and Select Tool

**Step 3.1: Locate Attachment Button**

**Primary Selector:**
```typescript
// Attachment button in composer area
await page.locator('div.composer-container button[aria-label*="Attach"]').click();
```

**Fallback Selectors:**
```typescript
// Option 1: Button with paperclip icon
await page.locator('button:has(svg):has-text("")').filter({ has: page.locator('svg[class*="paperclip"]') }).click();

// Option 2: Button near text input
await page.locator('div[contenteditable="true"]').locator('..').locator('button').first().click();
```

**Step 3.2: Select "Create Image" Tool**

```typescript
// Wait for menu to appear, then click "Create image"
await page.waitForTimeout(500);
await page.locator('text="Create image"').click();
```

**Step 3.3: Upload YAML File**

```typescript
const yamlPath = `/home/xai/DEV/37degrees/books/${bookFolder}/prompts/genimage/${sceneFile}`;

// Click "Add files" in the opened menu
await page.locator('text="Add files"').click();

// Upload file via file input
await page.setInputFiles('input[type="file"]', yamlPath);

// Wait for upload to complete
await page.waitForTimeout(3000);
```

**Step 3.4: Verify File Attached**

```typescript
// Check if filename appears in UI
const fileAttached = await page.locator(`text="${sceneFile}"`).isVisible();
if (!fileAttached) {
  throw new Error('File upload failed - filename not visible in UI');
}
```

---

### Phase 4: Enter Prompt and Send

**Step 4.1: Construct Prompt**

```typescript
const sceneMatch = sceneFile.match(/scene_(\d+)\.yaml/);
const sceneKey = sceneMatch ? `scene_${sceneMatch[1].padStart(4, '0')}` : 'scene_unknown';

const promptText = `${bookFolder}:${sceneKey} - create an image based on the scene, style, and visual specifications described in the attached YAML. Think carefully: the YAML is a blueprint, not the content!`;
```

**Step 4.2: Enter Prompt**

```typescript
// ChatGPT uses contenteditable div
const contentEditable = page.locator('[contenteditable="true"]').first();
await contentEditable.fill(promptText);
```

**Step 4.3: Click Send Button**

```typescript
// Primary selector
await page.locator('button[data-testid="send-button"]').click();

// Fallback
// await page.locator('button[aria-label="Send"]').click();
```

---

### Phase 5: Wait for Response and Verify Result

**Step 5.1: Wait for ChatGPT Response**

```typescript
await page.waitForSelector('[data-message-author-role="assistant"]', {
  timeout: 60000
});
await page.waitForTimeout(30000);  // Wait for generation to start
```

**Step 5.2: Extract Thread ID

```typescript
const url = page.url();
const threadIdMatch = url.match(/\/c\/([a-f0-9-]+)/);
const threadId = threadIdMatch ? threadIdMatch[1] : null;

if (!threadId) {
  throw new Error('Failed to extract thread ID from URL');
}
```

**Step 5.3: Check for Errors**

```typescript
const responseText = await page.evaluate(() => {
  const messages = document.querySelectorAll('[data-message-author-role="assistant"]');
  return Array.from(messages).map(m => m.textContent).join('\n');
});
```

```typescript
const errorKeywords = [
  "can't create", "unable to generate", "cannot create",
  "violates our content policies", "content policy",
  "plus plan limit", "sorry", "unfortunately"
];

const hasError = errorKeywords.some(kw =>
  responseText.toLowerCase().includes(kw.toLowerCase())
);
```

**Step 5.4: Handle Result**

If error detected:

```typescript
const errorMessage = responseText;  // Already extracted above

// Categorize error type
let errorType: 'policy' | 'limit' | 'unknown' = 'unknown';

if (errorMessage.includes('limit') && errorMessage.includes('plus plan')) {
  errorType = 'limit';
} else if (errorMessage.includes('policy') || errorMessage.includes('violates')) {
  errorType = 'policy';
}

// Screenshot
await page.screenshot({
  path: `/tmp/chatgpt-error-${bookFolder}-${sceneKey}.png`,
  fullPage: true
});

// Return error
return { success: false, threadId, error: errorMessage, errorType };
```

If no error:
```typescript
// Success
await page.screenshot({
  path: `/tmp/chatgpt-success-${bookFolder}-${sceneKey}.png`,
  fullPage: true
});

return { success: true, threadId };
```

---

### Phase 6: Cleanup

```typescript
await browser.close();
```

---

## Output Format

The script MUST output JSON to stdout for parsing by parent agent:

**Success:**
```json
{
  "success": true,
  "threadId": "abc123-def456-ghi789",
  "projectId": "g-p-68b7e9551f8081919511b1ce73c242ca",
  "sceneKey": "scene_0001"
}
```

**Error (Content Policy):**
```json
{
  "success": false,
  "threadId": "abc123-def456-ghi789",
  "error": "I can't create that image as it violates our content policies...",
  "errorType": "policy"
}
```

**Error (Usage Limit):**
```json
{
  "success": false,
  "threadId": "abc123-def456-ghi789",
  "error": "You've hit the plus plan limit. Your limit will reset at 3:00 PM.",
  "errorType": "limit"
}
```

---

## Edge Cases

| Case | Detection | Action |
|------|-----------|--------|
| User not logged in | Login page appears | Throw error |
| ChatGPT Plus limit | `"limit" + "plus plan"` in response | Return `errorType: 'limit'` (retry later) |
| Content policy violation | `"policy"` or `"violates"` in response | Return `errorType: 'policy'` (permanent) |
| Network timeout | Page load > 60s | Retry once, then throw |
| File upload fails | Filename not visible after 3s | Retry once, then throw |
| UI changed (selector not found) | Element not found | Take screenshot, throw with diagnostics |
| Project not found | 404 on project URL | Fall back to creating new project |


## Success Criteria

✅ Script successfully uploads YAML file
✅ Script selects "Create image" tool
✅ Script enters correct prompt
✅ Script extracts thread ID from URL
✅ Script detects and categorizes errors correctly
✅ Script outputs valid JSON
✅ Script handles edge cases (limits, policy violations)
✅ Script works with ANY book/scene combination (universal parameters)
✅ Script completes in < 2 minutes (typical case)

---

## Next Steps

1. ✅ **Test Plan Complete** (this document)
2. ⏳ Implement TypeScript script based on this plan
3. ⏳ Test with 3-5 real scenes from different books
4. ⏳ Integrate with Claude Code agent (`.claude/agents/37d-a3-playwright-upload.md`)
5. ⏳ Monitor for UI changes, update selectors as needed

---

**Document End**
