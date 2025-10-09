# Playwright Standalone Automation for ChatGPT

This directory contains standalone Playwright automation for ChatGPT image generation, replacing the MCP-based approach.

## Setup

### 1. Install Dependencies

```bash
# Install Node.js dependencies (Playwright, TypeScript)
npm install

# Install Chromium browser
npm run install:browsers
```

### 2. Configure Browser Profile

The script uses a **persistent browser profile** to maintain ChatGPT login:

```bash
# Profile directory: ~/.cache/chatgpt-playwright-profile/
# This keeps you logged in across runs
```

**First time setup:**
1. Run script once: `npx ts-node scripts/chatgpt/upload-scene.ts 0016_lalka scene_01.yaml`
2. Browser will open and show ChatGPT login page
3. **Manually log in** to your ChatGPT Plus account
4. Close the browser
5. Future runs will reuse this login!

## Usage

### Upload Scene to ChatGPT

```bash
# Basic usage (creates new project if needed)
npx ts-node scripts/chatgpt/upload-scene.ts <folder> <sceneFile>

# Examples - Books
npx ts-node scripts/chatgpt/upload-scene.ts 0016_lalka scene_01.yaml

# Examples - Media
npx ts-node scripts/chatgpt/upload-scene.ts m00001_media_item scene_01.yaml

# With existing project ID
npx ts-node scripts/chatgpt/upload-scene.ts 0016_lalka scene_01.yaml 68b7e9551f8081919511b1ce73c242ca
```

**Note:** Script auto-detects folder type:
- Starts with digit (e.g., `0016_lalka`) → `books/0016_lalka`
- Starts with 'm' (e.g., `m00001_xxx`) → `media/m00001_xxx`

### Output

The script outputs JSON to stdout:

**Success:**
```json
{
  "success": true,
  "threadId": "abc123-def456-ghi789",
  "projectId": "g-p-68b7e9551f8081919511b1ce73c242ca",
  "sceneKey": "scene_0001"
}
```

**Error:**
```json
{
  "success": false,
  "threadId": "abc123-def456-ghi789",
  "error": "You've hit the plus plan limit...",
  "errorType": "limit"
}
```

## Integration with Claude Code Agent

The standalone script is designed to be called from a Claude Code agent:

```bash
# Agent calls this
npx ts-node scripts/chatgpt/upload-scene.ts 0016_lalka scene_01.yaml

# Parses JSON output
# Saves threadId to TODOIT
# Updates task status
```

**Benefits:**
- ✅ 0 tokens (no MCP overhead)
- ✅ Fast and deterministic
- ✅ Easy to debug (standard Playwright tools)
- ✅ Reusable across all books

## Files

- `chatgpt-upload-test-plan.md` - Detailed test plan and selectors
- `../scripts/chatgpt/upload-scene.ts` - Main standalone script
- `../../package.json` - Node.js dependencies
- `../../playwright.config.ts` - Playwright configuration
- `../../tsconfig.json` - TypeScript configuration

## Troubleshooting

### Browser Not Installed

```bash
npm run install:browsers
```

### Login Not Persisting

Check that profile directory exists:
```bash
ls -la ~/.cache/chatgpt-playwright-profile/
```

### Selectors Not Working (ChatGPT UI Changed)

1. Check `chatgpt-upload-test-plan.md` for current selectors
2. Run with headed browser to inspect:
   ```typescript
   // In script, change:
   headless: false
   ```
3. Use Playwright Inspector:
   ```bash
   PWDEBUG=1 npx ts-node scripts/chatgpt/upload-scene.ts ...
   ```

### Screenshots

On failure, screenshots are saved to:
```
/tmp/chatgpt-error-{bookFolder}-{sceneKey}.png
```

On success:
```
/tmp/chatgpt-success-{bookFolder}-{sceneKey}.png
```

## Development

### Test Plan

See `chatgpt-upload-test-plan.md` for complete automation workflow.

### Debugging

```bash
# Run with Playwright Inspector (pauses before each action)
PWDEBUG=1 npx ts-node scripts/chatgpt/upload-scene.ts 0016_lalka scene_01.yaml

# Run with verbose logging
DEBUG=pw:api npx ts-node scripts/chatgpt/upload-scene.ts 0016_lalka scene_01.yaml
```

### Future: Playwright Agents (v1.56+)

When ChatGPT UI changes break selectors, can use Playwright Healer Agent to auto-fix:

```bash
# Future feature (not yet implemented)
npx playwright agents --healer
```

## Cost Comparison

### Before (MCP Playwright)
- 25 scenes × ~600 lines snapshot = 15,000 lines/book
- Token cost: ~$X per book
- Speed: Slow (LLM overhead)

### After (Standalone)
- Setup: 1× cost (generate script once)
- Runtime: **0 tokens**, **0 cost**
- Speed: Fast (no LLM overhead)
- Reusable: ∞ times for free ✨
