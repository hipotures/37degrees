#!/usr/bin/env ts-node
/**
 * Standalone Playwright automation for Google Gemini Deep Research (AFA version)
 *
 * This version:
 * - Assembles prompt from 17 agent files dynamically
 * - Saves prompt to books/{book}/prompts/afa-deep-research-prompt.md
 * - Uses assembled prompt instead of static file
 *
 * Usage:
 *   npx ts-node scripts/gemini/execute-deep-research-afa.ts <sourceName> [headless]
 *
 * Example:
 *   npx ts-node scripts/gemini/execute-deep-research-afa.ts 0055_of_mice_and_men
 *   npx ts-node scripts/gemini/execute-deep-research-afa.ts 0055_of_mice_and_men false
 *
 * Output (JSON to stdout):
 *   {"success": true, "searchUrl": "https://gemini.google.com/app/xxx"}
 *   {"success": false, "error": "Model verification failed", "errorType": "model_error"}
 */

import { chromium, BrowserContext, Page } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';
import * as net from 'net';
import { parse as parseYaml } from 'yaml';
import { execSync } from 'child_process';
import { assembleAFAPrompt } from './assemble-afa-prompt';

// ============================================================================
// TYPES
// ============================================================================

interface DeepResearchParams {
  sourceName: string;
  headless?: boolean;
}

interface DeepResearchResult {
  success: boolean;
  searchUrl?: string;
  error?: string;
  errorType?: 'model_error' | 'file_not_found' | 'paste_failed' | 'navigation_failed' | 'prompt_assembly_failed' | 'unknown';
}

interface BookInfo {
  title: string;
  author: string;
  year?: number;
}

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
  // Persistent browser profile for Gemini
  userDataDir: '/home/xai/DEV/ms-playwright/mcp-chrome-profile-gemini',

  // Base paths
  projectRoot: '/home/xai/DEV/37degrees',

  // Timeouts
  navigationTimeout: 30000,  // 30 seconds
  actionTimeout: 15000,      // 15 seconds
  modelCheckWait: 3000,      // 3 seconds after navigation
  planWait: 180000,          // 3 minutes max wait for plan (used in waitFor)

  // Screenshots
  screenshotDir: '/tmp',

  // Headless mode
  headless: true
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Check if a port is open on localhost
 */
async function isPortOpen(port: number): Promise<boolean> {
  return new Promise((resolve) => {
    const socket = new net.Socket();

    socket.setTimeout(1000);

    socket.on('connect', () => {
      socket.destroy();
      resolve(true);
    });

    socket.on('timeout', () => {
      socket.destroy();
      resolve(false);
    });

    socket.on('error', () => {
      resolve(false);
    });

    socket.connect(port, '127.0.0.1');
  });
}

/**
 * Read book.yaml and extract title/author/year
 */
function readBookInfo(sourceName: string): BookInfo {
  const bookYamlPath = path.join(CONFIG.projectRoot, 'books', sourceName, 'book.yaml');

  if (!fs.existsSync(bookYamlPath)) {
    throw new Error(`book.yaml not found: ${bookYamlPath}`);
  }

  const yamlContent = fs.readFileSync(bookYamlPath, 'utf-8');
  const bookData = parseYaml(yamlContent) as any;

  // Read from book_info section (correct structure)
  const bookInfo = bookData.book_info || bookData;

  // Try English title first, fallback to base title
  const title = bookInfo.title || bookInfo.title_pl || 'Unknown';
  const author = bookInfo.author || 'Unknown';
  const year = bookInfo.year || undefined;

  return { title, author, year };
}

/**
 * Load prompt file to clipboard using xsel
 */
function loadPromptToClipboard(promptPath: string): void {
  if (!fs.existsSync(promptPath)) {
    throw new Error(`Prompt file not found: ${promptPath}`);
  }

  try {
    execSync(`cat "${promptPath}" | xsel --clipboard`, {
      encoding: 'utf-8',
      timeout: 5000
    });
    console.error('  ✓ Prompt loaded to clipboard');
  } catch (error: any) {
    throw new Error(`Failed to load prompt to clipboard: ${error.message}`);
  }
}

/**
 * Take screenshot with descriptive name
 */
async function takeScreenshot(page: Page, name: string): Promise<void> {
  const timestamp = Date.now();
  const screenshotPath = path.join(CONFIG.screenshotDir, `gemini-deep-research-afa-${name}-${timestamp}.png`);
  await page.screenshot({ path: screenshotPath, fullPage: false });
  console.error(`  → Screenshot: ${screenshotPath}`);
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

async function executeDeepResearchAFA(params: DeepResearchParams): Promise<DeepResearchResult> {
  let browser: BrowserContext | null = null;
  let page: Page | null = null;
  let useCDP = false;

  try {
    // ========================================================================
    // PHASE 0: Read book info
    // ========================================================================

    console.error('[0/11] Reading book information...');
    const bookInfo = readBookInfo(params.sourceName);
    console.error(`  ✓ Title: ${bookInfo.title}`);
    console.error(`  ✓ Author: ${bookInfo.author}`);
    console.error('');

    // ========================================================================
    // PHASE 0.5: Assemble AFA prompt from 17 agents
    // ========================================================================

    console.error('[0.5/11] Assembling AFA research prompt...');

    let promptPath: string;
    try {
      const afaPrompt = await assembleAFAPrompt(params.sourceName, bookInfo);

      // Save to books/{book}/prompts/afa-deep-research-prompt.md
      promptPath = path.join(
        CONFIG.projectRoot,
        'books',
        params.sourceName,
        'prompts',
        'afa-deep-research-prompt.md'
      );

      fs.mkdirSync(path.dirname(promptPath), { recursive: true });
      fs.writeFileSync(promptPath, afaPrompt, 'utf-8');

      console.error(`  ✓ Prompt saved: ${promptPath}`);
      console.error(`  → Total length: ${afaPrompt.length} characters`);
    } catch (error: any) {
      throw new Error(`Failed to assemble AFA prompt: ${error.message}`);
    }

    console.error('');

    // ========================================================================
    // PHASE 1: Browser Setup (with CDP support)
    // ========================================================================

    console.error('[1/11] Launching browser...');

    // Check if CDP port 9222 is open
    const cdpPort = 9222;
    const isCdpAvailable = await isPortOpen(cdpPort);

    if (isCdpAvailable) {
      // Connect to existing browser via CDP
      console.error(`  → Connecting to existing browser on localhost:${cdpPort}`);
      useCDP = true;

      const cdpBrowser = await chromium.connectOverCDP(`http://localhost:${cdpPort}`);
      const contexts = cdpBrowser.contexts();

      if (contexts.length === 0) {
        throw new Error('No browser contexts available in CDP browser');
      }

      browser = contexts[0];
      const pages = browser.pages();

      if (pages.length === 0) {
        page = await browser.newPage();
      } else {
        page = pages[0];
      }

      console.error(`  ✓ Connected to existing browser (${pages.length} pages)`);

    } else {
      // Launch new browser instance
      const headlessMode = params.headless !== undefined ? params.headless : CONFIG.headless;
      console.error(`  → Launching new browser instance`);
      console.error(`  → Headless mode: ${headlessMode}`);

      browser = await chromium.launchPersistentContext(CONFIG.userDataDir, {
        headless: headlessMode,
        viewport: { width: 1920, height: 1080 },
        args: [
          '--no-sandbox',
          '--disable-blink-features=AutomationControlled'
        ]
      });

      page = browser.pages()[0] || await browser.newPage();
    }

    page.setDefaultTimeout(CONFIG.actionTimeout);
    console.error('');

    // ========================================================================
    // PHASE 2: Navigate to Gemini
    // ========================================================================

    console.error('[2/11] Navigating to Gemini...');

    await page.goto('https://gemini.google.com/', {
      timeout: CONFIG.navigationTimeout,
      waitUntil: 'domcontentloaded'
    });

    await page.waitForTimeout(CONFIG.modelCheckWait);
    console.error('  ✓ Navigation complete');
    console.error('');

    // ========================================================================
    // PHASE 3: Check and change model to Gemini 2.5 Pro
    // ========================================================================

    console.error('[3/11] Verifying model...');

    // Find model selector button "2.5 Flash" or "2.5 Pro"
    const modelButton = page.locator('button:has-text("2.5")').first();

    if (await modelButton.isVisible({ timeout: 5000 })) {
      const modelText = await modelButton.textContent();
      console.error(`  → Current model: ${modelText?.trim()}`);

      // ONLY change if NOT already 2.5 Pro
      if (modelText?.includes('2.5 Pro')) {
        console.error('  ✓ Already using 2.5 Pro - skipping change');
      } else {
        console.error('  → Changing to 2.5 Pro...');

        try {
          // Click model selector
          await modelButton.click();
          await page.waitForTimeout(1500);

          // Click "2.5 Pro" option in dropdown
          const proOption = page.locator('text=2.5 Pro').first();

          if (await proOption.isVisible({ timeout: 3000 })) {
            await proOption.click({ timeout: 10000 });
            await page.waitForTimeout(2000);
            console.error('  ✓ Model changed to 2.5 Pro');
          } else {
            console.error('  ⚠ 2.5 Pro option not found - continuing anyway');
          }
        } catch (error: any) {
          console.error(`  ⚠ Failed to change model: ${error.message}`);
          console.error('  → Continuing with current model...');
        }
      }
    } else {
      console.error('  ⚠ Model selector not found - continuing anyway');
    }

    console.error('');

    // ========================================================================
    // PHASE 4: Activate Deep Research
    // ========================================================================

    console.error('[4/11] Activating Deep Research...');

    // Look for Deep Research button
    const deepResearchButton = page.locator('button', { hasText: /Deep Research/i }).first();

    if (await deepResearchButton.isVisible({ timeout: 5000 })) {
      await deepResearchButton.click();
      await page.waitForTimeout(2000);
      console.error('  ✓ Deep Research activated');
    } else {
      throw new Error('Deep Research button not found');
    }

    await takeScreenshot(page, 'after-deep-research-click');
    console.error('');

    // ========================================================================
    // PHASE 5: Load assembled prompt to clipboard
    // ========================================================================

    console.error('[5/11] Loading AFA prompt to clipboard...');
    loadPromptToClipboard(promptPath);
    console.error('');

    // ========================================================================
    // PHASE 6: Paste prompt directly (no manual header)
    // ========================================================================

    console.error('[6/11] Entering prompt...');

    // Find text input area (textarea or contenteditable)
    const textArea = page.locator('textarea, [contenteditable="true"]').first();
    await textArea.click();
    await page.waitForTimeout(3000);

    // Paste full prompt from clipboard (already contains header)
    await page.keyboard.press('Control+v');
    await page.waitForTimeout(3000);

    console.error('  ✓ AFA prompt pasted');

    // Submit with Ctrl+Enter
    await page.keyboard.press('Control+Enter');
    await page.waitForTimeout(2000);

    console.error('  ✓ Prompt submitted');
    console.error('');

    // ========================================================================
    // PHASE 7: Wait for plan generation
    // ========================================================================

    console.error('[7/11] Waiting for plan generation...');
    console.error(`  → Waiting for "Start research" button (max ${CONFIG.planWait / 1000}s)...`);

    // Look for "Start research" or "Start search" or "Zacznij wyszukiwanie" button
    const startSearchButton = page.locator('button', {
      hasText: /(Start research|Start search|Zacznij wyszukiwanie)/i
    }).first();

    try {
      // Wait for button to appear (checks every ~500ms automatically)
      await startSearchButton.waitFor({ state: 'visible', timeout: CONFIG.planWait });
      console.error('  ✓ Plan ready, start button appeared');

      await takeScreenshot(page, 'after-plan-generation');
      console.error('');

      console.error('[8/11] Starting search...');
      await startSearchButton.click();
      await page.waitForTimeout(3000);
      console.error('  ✓ Search started');
    } catch (error) {
      await takeScreenshot(page, 'timeout-waiting-for-plan');
      throw new Error(`Start research button did not appear within ${CONFIG.planWait / 1000}s`);
    }

    await takeScreenshot(page, 'after-search-start');
    console.error('');

    // ========================================================================
    // PHASE 9: Get chat URL
    // ========================================================================

    console.error('[9/11] Getting chat URL...');

    const chatUrl = page.url();
    console.error(`  ✓ URL: ${chatUrl}`);
    console.error('');

    // ========================================================================
    // PHASE 10: Rename chat to book folder
    // ========================================================================

    console.error('[10/11] Renaming chat...');

    try {
      // Look for "Open menu for conversation actions" button (3 dots)
      // IMPORTANT: Must use exact aria-label to avoid clicking "Main menu" (hamburger)
      const menuButton = page.locator('button[aria-label="Open menu for conversation actions"]').first();

      if (await menuButton.isVisible({ timeout: 5000 })) {
        await menuButton.click();
        await page.waitForTimeout(1500);
        console.error('  → Menu opened');

        // Look for "Rename" button in menu
        const renameOption = page.locator('button', { hasText: /^Rename$/i }).first();

        if (await renameOption.isVisible({ timeout: 3000 })) {
          await renameOption.click();
          await page.waitForTimeout(1500);
          console.error('  → Rename dialog opened');

          // Find textbox "Enter new title" in rename dialog
          const nameInput = page.getByRole('textbox', { name: /Enter new title/i });

          if (await nameInput.isVisible({ timeout: 3000 })) {
            // Clear existing text and type new name
            await nameInput.click();
            await nameInput.selectText();
            await nameInput.fill(params.sourceName);
            await page.waitForTimeout(500);
            console.error(`  → Entered new name: ${params.sourceName}`);

            // Click enabled Rename button
            const confirmButton = page.locator('button:has-text("Rename"):not([disabled])').first();

            if (await confirmButton.isVisible({ timeout: 3000 })) {
              await confirmButton.click();
              await page.waitForTimeout(1000);
              console.error(`  ✓ Chat renamed to: ${params.sourceName}`);
            } else {
              console.error('  ⚠ Rename button not enabled');
            }
          } else {
            console.error('  ⚠ Rename input not found');
          }
        } else {
          console.error('  ⚠ Rename option not found in menu');
        }
      } else {
        console.error('  ⚠ Menu button not found');
      }
    } catch (error: any) {
      console.error(`  ⚠ Failed to rename chat: ${error.message}`);
      // Non-critical error - continue
    }

    await takeScreenshot(page, 'final-success');
    console.error('');

    // ========================================================================
    // SUCCESS
    // ========================================================================

    // Don't close CDP browser (leave it running)
    if (!useCDP && browser) {
      await browser.close();
    }

    return {
      success: true,
      searchUrl: chatUrl
    };

  } catch (error: any) {
    console.error('');
    console.error(`✗ Error: ${error.message}`);

    if (page) {
      try {
        await takeScreenshot(page, 'error');
      } catch (screenshotError) {
        // Ignore screenshot errors
      }
    }

    // Don't close CDP browser on error
    if (!useCDP && browser) {
      try {
        await browser.close();
      } catch (closeError) {
        // Ignore close errors
      }
    }

    // Determine error type
    let errorType: DeepResearchResult['errorType'] = 'unknown';
    if (error.message.includes('book.yaml')) {
      errorType = 'file_not_found';
    } else if (error.message.includes('model')) {
      errorType = 'model_error';
    } else if (error.message.includes('clipboard') || error.message.includes('paste')) {
      errorType = 'paste_failed';
    } else if (error.message.includes('navigation') || error.message.includes('timeout')) {
      errorType = 'navigation_failed';
    } else if (error.message.includes('assemble') || error.message.includes('prompt')) {
      errorType = 'prompt_assembly_failed';
    }

    return {
      success: false,
      error: error.message,
      errorType
    };
  }
}

// ============================================================================
// CLI ENTRY POINT
// ============================================================================

async function main() {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.error('Usage: npx ts-node execute-deep-research-afa.ts <sourceName> [headless]');
    console.error('Example: npx ts-node execute-deep-research-afa.ts 0055_of_mice_and_men');
    process.exit(1);
  }

  const params: DeepResearchParams = {
    sourceName: args[0],
    headless: args[1] === 'false' ? false : true
  };

  const result = await executeDeepResearchAFA(params);

  // Output JSON result to stdout
  console.log(JSON.stringify(result));

  // Exit with appropriate code
  process.exit(result.success ? 0 : 1);
}

// Run if executed directly
if (require.main === module) {
  main();
}
