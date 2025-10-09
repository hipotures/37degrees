#!/usr/bin/env ts-node
/**
 * Standalone Playwright automation for uploading YAML scenes to ChatGPT
 *
 * Usage:
 *   npx ts-node scripts/chatgpt/upload-scene.ts <bookFolder> <sceneFile> [projectId]
 *
 * Example:
 *   npx ts-node scripts/chatgpt/upload-scene.ts 0016_lalka scene_01.yaml
 *   npx ts-node scripts/chatgpt/upload-scene.ts 0016_lalka scene_01.yaml 68b7e9551f8081919511b1ce73c242ca
 *
 * Output (JSON to stdout):
 *   {"success": true, "threadId": "abc123", "projectId": "g-p-xyz", "sceneKey": "scene_0001"}
 *   {"success": false, "threadId": "abc123", "error": "...", "errorType": "limit"}
 */

import { chromium, BrowserContext, Page } from 'playwright';
import * as path from 'path';
import * as fs from 'fs';

// ============================================================================
// TYPES
// ============================================================================

interface UploadParams {
  bookFolder: string;
  sceneFile: string;
  projectId?: string;
}

interface UploadResult {
  success: boolean;
  threadId?: string;
  projectId?: string;
  sceneKey?: string;
  error?: string;
  errorType?: 'policy' | 'limit' | 'network' | 'unknown';
}

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
  // Persistent browser profile (maintains ChatGPT login)
  // Using same profile as MCP playwright-show-browser for existing session
  userDataDir: '/home/xai/DEV/ms-playwright/mcp-chrome-profile-2',

  // Base paths
  projectRoot: '/home/xai/DEV/37degrees',

  // ChatGPT URLs
  chatgptBase: 'https://chatgpt.com',

  // Timeouts
  navigationTimeout: 60000,  // 1 minute
  actionTimeout: 30000,      // 30 seconds
  responseTimeout: 60000,    // 1 minute for ChatGPT response
  generationWait: 30000,     // 30 seconds for generation to start

  // Model
  model: 'o4-mini',

  // Screenshots
  screenshotDir: '/tmp',

  // Headless mode (set to false for debugging)
  headless: true
};

// ============================================================================
// ERROR KEYWORDS
// ============================================================================

const ERROR_KEYWORDS = [
  "can't create",
  "unable to generate",
  "cannot create",
  "violates our content policies",
  "content policy",
  "plus plan limit",
  "sorry",
  "unfortunately"
];

// ============================================================================
// MAIN FUNCTION
// ============================================================================

async function uploadScene(params: UploadParams): Promise<UploadResult> {
  let browser: BrowserContext | null = null;
  let page: Page | null = null;

  try {
    // Parse scene key from filename
    const sceneMatch = params.sceneFile.match(/scene_(\d+)\.yaml/);
    const sceneKey = sceneMatch ? `scene_${sceneMatch[1].padStart(4, '0')}` : 'scene_unknown';

    // Detect if this is a book or media folder
    // - books: NNNN_xxxx (starts with digit)
    // - media: mNNNNN_xxxx (starts with 'm')
    const isMediaFolder = params.bookFolder.startsWith('m');
    const basePath = isMediaFolder ? 'media' : 'books';

    console.error(`  → Type: ${basePath}`);

    // Construct YAML file path
    const yamlPath = path.join(
      CONFIG.projectRoot,
      basePath,
      params.bookFolder,
      'prompts',
      'genimage',
      params.sceneFile
    );

    // Verify YAML file exists
    if (!fs.existsSync(yamlPath)) {
      throw new Error(`YAML file not found: ${yamlPath}`);
    }

    // ========================================================================
    // PHASE 1: Browser Setup
    // ========================================================================

    console.error('[1/6] Launching browser...');
    browser = await chromium.launchPersistentContext(CONFIG.userDataDir, {
      headless: CONFIG.headless,
      viewport: { width: 1280, height: 720 },
      args: [
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
      ],
      userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    });

    page = browser.pages()[0] || await browser.newPage();

    // ========================================================================
    // PHASE 2: Project Navigation
    // ========================================================================

    console.error('[2/6] Navigating to project...');

    let finalProjectId = params.projectId;

    if (params.projectId) {
      // Navigate directly to existing project (skip home page!)
      // (Agent always provides projectId from TODOIT after first creation)
      const fullProjectId = params.projectId.startsWith('g-p-')
        ? params.projectId
        : `g-p-${params.projectId}`;

      const projectUrl = `${CONFIG.chatgptBase}/g/${fullProjectId}/project?model=${CONFIG.model}`;
      console.error(`  → Using existing project: ${fullProjectId}`);

      await page.goto(projectUrl, {
        waitUntil: 'networkidle',
        timeout: CONFIG.navigationTimeout
      });

      finalProjectId = fullProjectId;

      // Check if logged in (basic check after loading project page)
      const isLoginPage = await page.locator('text="Log in"').isVisible().catch(() => false);
      if (isLoginPage) {
        throw new Error('User not logged in to ChatGPT. Please log in manually first.');
      }

    } else {
      // Create NEW project (first time only)
      console.error(`  → Creating new project: ${params.bookFolder}`);

      // Navigate to ChatGPT home page
      await page.goto(`${CONFIG.chatgptBase}/?model=${CONFIG.model}`, {
        waitUntil: 'networkidle',
        timeout: CONFIG.navigationTimeout
      });

      // Check if logged in
      const isLoginPage = await page.locator('text="Log in"').isVisible().catch(() => false);
      if (isLoginPage) {
        throw new Error('User not logged in to ChatGPT. Please log in manually first.');
      }

      // Open sidebar to access "New project" button
      const sidebarButton = page.locator('button').filter({ hasText: /sidebar|menu/i }).first();
      if (await sidebarButton.isVisible()) {
        await sidebarButton.click();
        await page.waitForTimeout(1000);
      }

      // Click "New project"
      await page.locator('text="New project"').click();
      await page.waitForTimeout(500);

      // Enter project name
      const projectNameInput = page.locator('input[placeholder*="name" i]').first();
      await projectNameInput.fill(params.bookFolder);
      await projectNameInput.press('Enter');
      await page.waitForTimeout(2000);

      // Extract project ID from URL
      const url = page.url();
      const projectIdMatch = url.match(/\/g\/(g-p-[a-z0-9-]+)/);
      finalProjectId = projectIdMatch ? projectIdMatch[1] : undefined;

      if (!finalProjectId) {
        console.error('  ⚠ Warning: Could not extract project ID from URL');
      } else {
        console.error(`  ✓ New Project ID: ${finalProjectId}`);
      }
    }

    // ========================================================================
    // PHASE 3: Attach YAML File and Select Tool
    // ========================================================================

    console.error('[3/6] Attaching YAML file...');

    // Hide project-level "Add files" button BEFORE opening menu
    // This prevents confusion between project files and chat attachment
    console.error('  → Hiding project files section...');
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      for (let button of buttons) {
        if (button.textContent?.includes('Add files')) {
          const parent = button.parentElement;
          if (parent && parent instanceof HTMLElement) {
            parent.style.display = 'none';
            parent.setAttribute('data-hidden-by-automation', 'project-files');
          }
          break;  // Only hide the FIRST "Add files" button (project-level)
        }
      }
    });

    // Wait a bit for DOM to update
    await page.waitForTimeout(500);

    // Find and click "+" button to open tools menu
    console.error('  → Looking for tools button (+)...');

    // Try multiple selector strategies
    const toolsButton = page.locator('button').filter({ hasText: '+' }).or(
      page.locator('button[aria-label*="Attach"]')
    ).or(
      page.locator('form button').filter({ has: page.locator('svg') })
    ).first();

    console.error('  → Opening tools menu...');
    await toolsButton.click();
    await page.waitForTimeout(1000);

    // Wait for menu and click file upload option
    // Try mobile UI first: "Add photos & files", then desktop: "Add files"
    console.error('  → Looking for file upload option...');

    const mobileButton = page.locator('text="Add photos & files"');
    const desktopButton = page.locator('text="Add files"').filter({ hasNot: page.locator('[data-hidden-by-automation]') });

    // Check which one is visible
    const isMobileVisible = await mobileButton.isVisible().catch(() => false);

    if (isMobileVisible) {
      console.error('  → Found mobile UI: "Add photos & files"');
      await mobileButton.click();
    } else {
      console.error('  → Found desktop UI: "Add files"');
      await desktopButton.waitFor({ state: 'visible', timeout: 5000 });
      await desktopButton.click();
    }

    await page.waitForTimeout(500);

    // Upload YAML file via file input
    console.error(`  → Uploading ${params.sceneFile}...`);
    await page.setInputFiles('input[type="file"]', yamlPath);
    await page.waitForTimeout(3000);

    // Verify file attached
    const fileAttached = await page.locator(`text="${params.sceneFile}"`).isVisible();
    if (!fileAttached) {
      throw new Error('File upload failed - filename not visible in UI');
    }

    console.error('  ✓ File attached successfully');

    // ========================================================================
    // PHASE 4: Enter Prompt and Send
    // ========================================================================

    console.error('[4/6] Entering prompt and sending...');

    const promptText = `${params.bookFolder}:${sceneKey} - create an image based on the scene, style, and visual specifications described in the attached YAML. Think carefully: the YAML is a blueprint, not the content!`;

    // Enter prompt in contenteditable div
    const contentEditable = page.locator('[contenteditable="true"]').first();
    await contentEditable.fill(promptText);

    console.error('  → Clicking send button...');

    // Click send button
    const sendButton = page.locator('button[data-testid="send-button"]')
      .or(page.locator('button[aria-label="Send"]'));

    await sendButton.click();

    // ========================================================================
    // PHASE 5: Wait for Response and Verify Result
    // ========================================================================

    console.error('[5/6] Waiting for ChatGPT response...');

    // Wait for assistant response
    await page.waitForSelector('[data-message-author-role="assistant"]', {
      timeout: CONFIG.responseTimeout
    });

    console.error('  → Response received, waiting for generation to start...');

    // Wait for generation to start
    await page.waitForTimeout(CONFIG.generationWait);

    // Extract thread ID
    const url = page.url();
    const threadIdMatch = url.match(/\/c\/([a-f0-9-]+)/);
    const threadId = threadIdMatch ? threadIdMatch[1] : null;

    if (!threadId) {
      throw new Error('Failed to extract thread ID from URL');
    }

    console.error(`  ✓ Thread ID: ${threadId}`);

    // Check for errors
    const responseText = await page.evaluate(() => {
      const messages = document.querySelectorAll('[data-message-author-role="assistant"]');
      return Array.from(messages).map((m: Element) => m.textContent).join('\n');
    });

    const hasError = ERROR_KEYWORDS.some(kw =>
      responseText.toLowerCase().includes(kw.toLowerCase())
    );

    if (hasError) {
      // Categorize error type
      let errorType: 'policy' | 'limit' | 'unknown' = 'unknown';

      if (responseText.includes('limit') && responseText.includes('plus plan')) {
        errorType = 'limit';
      } else if (responseText.includes('policy') || responseText.includes('violates')) {
        errorType = 'policy';
      }

      // Take screenshot
      const screenshotPath = path.join(CONFIG.screenshotDir, `chatgpt-error-${params.bookFolder}-${sceneKey}.png`);
      await page.screenshot({ path: screenshotPath, fullPage: true });

      console.error(`  ✗ Error detected (${errorType})`);
      console.error(`  → Screenshot: ${screenshotPath}`);

      return {
        success: false,
        threadId,
        projectId: finalProjectId,
        sceneKey,
        error: responseText.substring(0, 500),  // Truncate to 500 chars
        errorType
      };
    }

    // Success
    const screenshotPath = path.join(CONFIG.screenshotDir, `chatgpt-success-${params.bookFolder}-${sceneKey}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });

    console.error('  ✓ Image generation started successfully');
    console.error(`  → Screenshot: ${screenshotPath}`);

    return {
      success: true,
      threadId,
      projectId: finalProjectId,
      sceneKey
    };

  } catch (error: any) {
    console.error(`✗ Error: ${error.message}`);

    // Take error screenshot if page exists
    if (page) {
      try {
        const screenshotPath = path.join(CONFIG.screenshotDir, `chatgpt-exception-${Date.now()}.png`);
        await page.screenshot({ path: screenshotPath, fullPage: true });
        console.error(`  → Screenshot: ${screenshotPath}`);
      } catch (screenshotError) {
        // Ignore screenshot errors
      }
    }

    return {
      success: false,
      error: error.message,
      errorType: 'unknown'
    };

  } finally {
    // ========================================================================
    // PHASE 6: Cleanup
    // ========================================================================

    console.error('[6/6] Cleaning up...');

    if (browser) {
      await browser.close();
    }
  }
}

// ============================================================================
// CLI ENTRY POINT
// ============================================================================

async function main() {
  // Parse arguments
  const args = process.argv.slice(2);

  if (args.length < 2) {
    console.error('Usage: npx ts-node scripts/chatgpt/upload-scene.ts <bookFolder> <sceneFile> [projectId]');
    console.error('Example: npx ts-node scripts/chatgpt/upload-scene.ts 0016_lalka scene_01.yaml');
    process.exit(1);
  }

  const params: UploadParams = {
    bookFolder: args[0],
    sceneFile: args[1],
    projectId: args[2]
  };

  console.error(`\n=== ChatGPT Upload Scene ===`);
  console.error(`Book: ${params.bookFolder}`);
  console.error(`Scene: ${params.sceneFile}`);
  if (params.projectId) {
    console.error(`Project ID: ${params.projectId}`);
  }
  console.error('');

  // Run upload
  const result = await uploadScene(params);

  // Output JSON to stdout (for parent agent to parse)
  console.log(JSON.stringify(result, null, 2));

  // Exit with appropriate code
  process.exit(result.success ? 0 : 1);
}

// Run if called directly
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

export { uploadScene, UploadParams, UploadResult };
