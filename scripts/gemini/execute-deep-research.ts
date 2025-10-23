#!/usr/bin/env ts-node
/**
 * Standalone Playwright automation for Google Gemini Deep Research
 *
 * Usage:
 *   npx ts-node scripts/gemini/execute-deep-research.ts <sourceName> [headless]
 *
 * Example:
 *   npx ts-node scripts/gemini/execute-deep-research.ts 0055_of_mice_and_men
 *   npx ts-node scripts/gemini/execute-deep-research.ts 0055_of_mice_and_men false
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
  errorType?: 'model_error' | 'file_not_found' | 'paste_failed' | 'navigation_failed' | 'unknown';
}

interface BookInfo {
  title: string;
  author: string;
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
  planWait: 115000,          // 115 seconds for plan generation

  // Screenshots
  screenshotDir: '/tmp',

  // Headless mode
  headless: true,

  // Instruction file
  promptFile: 'docs/audio-research/podcast_research_prompt.md'
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
 * Read book.yaml and extract title/author
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

  return { title, author };
}

/**
 * Load instructions to clipboard using xsel
 */
function loadInstructionsToClipboard(): void {
  const promptPath = path.join(CONFIG.projectRoot, CONFIG.promptFile);

  if (!fs.existsSync(promptPath)) {
    throw new Error(`Prompt file not found: ${promptPath}`);
  }

  try {
    // Skip first 3 lines (example header) and load rest to clipboard
    execSync(`tail -n +4 "${promptPath}" | xsel --clipboard`, {
      encoding: 'utf-8',
      timeout: 5000
    });
    console.error('  ✓ Instructions loaded to clipboard (skipped example header)');
  } catch (error: any) {
    throw new Error(`Failed to load instructions to clipboard: ${error.message}`);
  }
}

/**
 * Take screenshot with descriptive name
 */
async function takeScreenshot(page: Page, name: string): Promise<void> {
  const timestamp = Date.now();
  const screenshotPath = path.join(CONFIG.screenshotDir, `gemini-deep-research-${name}-${timestamp}.png`);
  await page.screenshot({ path: screenshotPath, fullPage: false });
  console.error(`  → Screenshot: ${screenshotPath}`);
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

async function executeDeepResearch(params: DeepResearchParams): Promise<DeepResearchResult> {
  let browser: BrowserContext | null = null;
  let page: Page | null = null;
  let useCDP = false;

  try {
    // ========================================================================
    // PHASE 0: Read book info
    // ========================================================================

    console.error('[0/10] Reading book information...');
    const bookInfo = readBookInfo(params.sourceName);
    console.error(`  ✓ Title: ${bookInfo.title}`);
    console.error(`  ✓ Author: ${bookInfo.author}`);
    console.error('');

    // ========================================================================
    // PHASE 1: Browser Setup (with CDP support)
    // ========================================================================

    console.error('[1/10] Launching browser...');

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

    console.error('[2/10] Navigating to Gemini...');

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

    console.error('[3/10] Setting model to 2.5 Pro...');

    // Find model selector button "2.5 Flash" or similar
    const modelButton = page.locator('button:has-text("2.5")').first();
    await modelButton.click();
    await page.waitForTimeout(1000);

    // Click "2.5 Pro" option in dropdown
    const proOption = page.locator('text=2.5 Pro').first();
    await proOption.click();
    await page.waitForTimeout(2000);

    console.error('  ✓ Model set to 2.5 Pro');

    console.error('');

    // ========================================================================
    // PHASE 4: Activate Deep Research
    // ========================================================================

    console.error('[4/10] Activating Deep Research...');

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
    // PHASE 5: Load instructions to clipboard
    // ========================================================================

    console.error('[5/10] Loading instructions to clipboard...');
    loadInstructionsToClipboard();
    console.error('');

    // ========================================================================
    // PHASE 6: Focus on text field and paste instructions
    // ========================================================================

    console.error('[6/10] Entering prompt...');

    // Find text input area (textarea or contenteditable)
    const textArea = page.locator('textarea, [contenteditable="true"]').first();
    await textArea.click();
    await page.waitForTimeout(3000);

    // Type header with book info (use Shift+Enter for newlines)
    await textArea.fill('## BADANA KSIĄŻKA');
    await page.keyboard.press('Shift+Enter');
    await textArea.pressSequentially(`title: ${bookInfo.title}`);
    await page.keyboard.press('Shift+Enter');
    await textArea.pressSequentially(`author: ${bookInfo.author}`);
    await page.keyboard.press('Shift+Enter');
    await page.keyboard.press('Shift+Enter');
    await page.waitForTimeout(2000);

    console.error('  ✓ Header typed with Shift+Enter');

    // DEBUG: Show what will be pasted from clipboard
    try {
      const promptPath = path.join(CONFIG.projectRoot, CONFIG.promptFile);
      const promptContent = fs.readFileSync(promptPath, 'utf-8');
      // Skip first 3 lines (example header)
      const promptLines = promptContent.split('\n');
      const promptWithoutExample = promptLines.slice(3).join('\n');
      const headerText = `## BADANA KSIĄŻKA\ntitle: ${bookInfo.title}\nauthor: ${bookInfo.author}\n\n`;
      const fullPrompt = headerText + promptWithoutExample;

      console.error('');
      console.error('='.repeat(80));
      console.error('DEBUG: Full prompt (header + clipboard content):');
      console.error('='.repeat(80));
      console.error(fullPrompt);
      console.error('='.repeat(80));
      console.error(`Total length: ${fullPrompt.length} characters`);
      console.error('='.repeat(80));
      console.error('');
    } catch (err) {
      console.error('  ⚠ Could not read prompt file for debug');
    }

    // Paste instructions from clipboard
    await page.keyboard.press('Control+v');
    await page.waitForTimeout(3000);

    console.error('  ✓ Instructions pasted');

    // Submit with Ctrl+Enter
    await page.keyboard.press('Control+Enter');
    await page.waitForTimeout(2000);

    console.error('  ✓ Prompt submitted');
    console.error('');

    // ========================================================================
    // PHASE 7: Wait for plan and start search
    // ========================================================================

    console.error('[7/10] Waiting for plan generation...');
    console.error(`  → Waiting ${CONFIG.planWait / 1000} seconds...`);

    await page.waitForTimeout(CONFIG.planWait);

    console.error('  ✓ Plan should be ready');
    await takeScreenshot(page, 'after-plan-generation');
    console.error('');

    console.error('[8/10] Starting search...');

    // Look for "Start search" or "Zacznij wyszukiwanie" button
    const startSearchButton = page.locator('button', {
      hasText: /(Start search|Zacznij wyszukiwanie)/i
    }).first();

    if (await startSearchButton.isVisible({ timeout: 10000 })) {
      await startSearchButton.click();
      await page.waitForTimeout(3000);
      console.error('  ✓ Search started');
    } else {
      throw new Error('Start search button not found');
    }

    await takeScreenshot(page, 'after-search-start');
    console.error('');

    // ========================================================================
    // PHASE 9: Get chat URL
    // ========================================================================

    console.error('[9/10] Getting chat URL...');

    const chatUrl = page.url();
    console.error(`  ✓ URL: ${chatUrl}`);
    console.error('');

    // ========================================================================
    // PHASE 10: Rename chat to book folder
    // ========================================================================

    console.error('[10/10] Renaming chat...');

    try {
      // Look for menu button (usually 3 dots or similar)
      const menuButton = page.locator('[aria-label*="More"], button[aria-haspopup="menu"]').first();

      if (await menuButton.isVisible({ timeout: 5000 })) {
        await menuButton.click();
        await page.waitForTimeout(1000);

        // Look for "Rename" option
        const renameOption = page.locator('[role="menuitem"]', { hasText: /Rename|Zmień nazwę/i }).first();

        if (await renameOption.isVisible({ timeout: 3000 })) {
          await renameOption.click();
          await page.waitForTimeout(1000);

          // Find input field and enter book folder name
          const nameInput = page.locator('input[type="text"], textarea').first();
          await nameInput.fill(params.sourceName);
          await page.waitForTimeout(500);

          // Confirm (look for button with "Rename" or similar)
          const confirmButton = page.locator('button', { hasText: /Rename|Zmień nazwę|OK|Save/i }).first();
          await confirmButton.click();
          await page.waitForTimeout(1000);

          console.error(`  ✓ Chat renamed to: ${params.sourceName}`);
        } else {
          console.error('  ⚠ Rename option not found');
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
    console.error('Usage: npx ts-node execute-deep-research.ts <sourceName> [headless]');
    console.error('Example: npx ts-node execute-deep-research.ts 0055_of_mice_and_men');
    process.exit(1);
  }

  const params: DeepResearchParams = {
    sourceName: args[0],
    headless: args[1] === 'false' ? false : true
  };

  const result = await executeDeepResearch(params);

  // Output JSON result to stdout
  console.log(JSON.stringify(result));

  // Exit with appropriate code
  process.exit(result.success ? 0 : 1);
}

// Run if executed directly
if (require.main === module) {
  main();
}
