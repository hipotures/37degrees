#!/usr/bin/env ts-node
/**
 * Standalone Playwright automation for NotebookLM audio generation
 *
 * Usage:
 *   npx ts-node scripts/gemini/generate-audio.ts <sourceName> <languageCode> <notebookUrl> [headless]
 *
 * Example:
 *   npx ts-node scripts/gemini/generate-audio.ts 0055_of_mice_and_men ja https://notebooklm.google.com/notebook/xxx
 *   npx ts-node scripts/gemini/generate-audio.ts 0055_of_mice_and_men ja https://notebooklm.google.com/notebook/xxx false
 *
 * Output (JSON to stdout):
 *   {"success": true, "audioId": "xxx"}
 *   {"success": false, "error": "Daily limit reached", "errorType": "daily_limit"}
 */

import { chromium, BrowserContext, Page } from 'playwright';
import * as path from 'path';
import * as net from 'net';
import { execSync } from 'child_process';

// ============================================================================
// TYPES
// ============================================================================

interface AudioGenParams {
  sourceName: string;
  languageCode: string;
  notebookUrl: string;
  headless?: boolean;
}

interface AudioGenResult {
  success: boolean;
  audioId?: string;
  error?: string;
  errorType?: 'daily_limit' | 'network' | 'source_not_found' | 'generation_failed' | 'unknown';
}

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
  // Persistent browser profile for Gemini/NotebookLM
  userDataDir: '/home/xai/DEV/ms-playwright/mcp-chrome-profile-gemini',

  // Base paths
  projectRoot: '/home/xai/DEV/37degrees',

  // Timeouts
  navigationTimeout: 30000,  // 30 seconds (fast fail for retry)
  actionTimeout: 15000,      // 15 seconds
  generationWait: 5000,      // 5 seconds to verify generation started

  // Screenshots and output
  screenshotDir: '/tmp',

  // Headless mode (set to false for debugging)
  headless: true,

  // Language mapping (NotebookLM UI names)
  languageMapping: {
    'pl': 'polski',
    'en': 'English',
    'es': 'español (Latinoamérica)',
    'pt': 'português (Brasil)',
    'hi': 'हिन्दी',
    'ja': '日本語',
    'ko': '한국어',
    'de': 'Deutsch',
    'fr': 'français'
  } as Record<string, string>
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
 * Generate prompt using Python script
 */
function generatePrompt(sourceName: string, languageCode: string): string {
  try {
    const cmd = `python scripts/afa/afa-prompt-generator.py ${sourceName} ${languageCode}`;
    const result = execSync(cmd, {
      cwd: CONFIG.projectRoot,
      encoding: 'utf-8',
      timeout: 30000
    });

    if (!result || result.trim() === '') {
      throw new Error('Python script returned empty output');
    }

    return result.trim();
  } catch (error: any) {
    throw new Error(`Failed to generate prompt: ${error.message}`);
  }
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

async function generateAudio(params: AudioGenParams): Promise<AudioGenResult> {
  let browser: BrowserContext | null = null;
  let page: Page | null = null;
  let useCDP = false;

  try {
    // ========================================================================
    // PHASE 1: Browser Setup
    // ========================================================================

    console.error('[1/8] Launching browser...');

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

    // ========================================================================
    // PHASE 2: Navigate to NotebookLM
    // ========================================================================

    console.error('[2/8] Navigating to NotebookLM...');
    console.error(`  → URL: ${params.notebookUrl}`);

    await page.goto(params.notebookUrl, {
      waitUntil: 'load',  // Use 'load' instead of 'networkidle' for better reliability
      timeout: CONFIG.navigationTimeout
    });

    await page.waitForTimeout(3000);  // Wait for UI to settle (NotebookLM is slow)

    // Check if logged in
    const isLoginRequired = await page.locator('text="Sign in"').isVisible().catch(() => false);
    if (isLoginRequired) {
      throw new Error('User not logged in to Google. Please log in manually first.');
    }

    console.error('  ✓ NotebookLM loaded');

    // ========================================================================
    // PHASE 3: Select source (Desktop: panels visible, Mobile: tabs)
    // ========================================================================

    console.error('[3/8] Selecting source...');

    // Desktop version: Sources panel always visible on left, no tabs needed
    // Let UI settle after navigation
    await page.waitForTimeout(1000);

    // Uncheck all sources first (click "Select all" checkbox to toggle off)
    const selectAllCheckbox = page.locator('input[type="checkbox"]').first();
    const isChecked = await selectAllCheckbox.isChecked();

    if (isChecked) {
      console.error('  → Unchecking all sources...');
      await selectAllCheckbox.click();
      await page.waitForTimeout(500);
    }

    // Find and select target source checkbox
    console.error(`  → Selecting source: ${params.sourceName}`);

    // Find checkbox by base name (ignore extension: .md, .txt, .docx, etc.)
    // Filter checkboxes to find one whose aria-label starts with sourceName
    const allCheckboxes = page.locator('input[type="checkbox"]');
    let sourceCheckbox = null;

    const count = await allCheckboxes.count();
    for (let i = 0; i < count; i++) {
      const checkbox = allCheckboxes.nth(i);
      const ariaLabel = await checkbox.getAttribute('aria-label');

      // Check if aria-label starts with sourceName (ignore extension)
      if (ariaLabel && ariaLabel.startsWith(params.sourceName)) {
        sourceCheckbox = checkbox;
        console.error(`  → Found: ${ariaLabel}`);
        break;
      }
    }

    if (!sourceCheckbox) {
      throw new Error(`Source "${params.sourceName}" not found in NotebookLM`);
    }

    await sourceCheckbox.click();
    await page.waitForTimeout(1000);

    console.error('  ✓ Source selected');

    // ========================================================================
    // PHASE 4: Studio panel (Desktop: always visible, no tabs)
    // ========================================================================

    console.error('[4/8] Accessing Studio panel...');

    // Desktop version: Studio panel always visible on right, no need to click tabs
    await page.waitForTimeout(500);

    console.error('  ✓ Studio panel ready');

    // ========================================================================
    // PHASE 5: Open customization dialog
    // ========================================================================

    console.error('[5/8] Opening customization...');

    // Find and click the Edit button (pencil icon) within Audio overview button
    const editButton = page.locator('button').filter({ hasText: /edit|customize/i }).first();
    const editExists = await editButton.isVisible().catch(() => false);

    if (!editExists) {
      throw new Error('Edit/Customize button not found in Studio');
    }

    await editButton.click();
    await page.waitForTimeout(2000);  // Wait for dialog to open

    console.error('  ✓ Customization dialog opened');

    // ========================================================================
    // PHASE 6: Select language
    // ========================================================================

    console.error('[6/8] Selecting language...');

    const targetLanguageUI = CONFIG.languageMapping[params.languageCode];
    if (!targetLanguageUI) {
      throw new Error(`Unsupported language code: ${params.languageCode}`);
    }

    console.error(`  → Language: ${params.languageCode} (${targetLanguageUI})`);

    // Find language combobox in the dialog
    const languageCombobox = page.locator('[role="combobox"]').first();
    const comboboxExists = await languageCombobox.isVisible().catch(() => false);

    if (comboboxExists) {
      // Click to open dropdown
      await languageCombobox.click();
      await page.waitForTimeout(1000);

      // Find and click the language option
      const languageOption = page.locator(`[role="option"]`).filter({ hasText: targetLanguageUI }).first();
      const optionExists = await languageOption.isVisible().catch(() => false);

      if (optionExists) {
        await languageOption.click();
        await page.waitForTimeout(500);
        console.error('  ✓ Language selected');
      } else {
        console.error(`  ⚠ Language option "${targetLanguageUI}" not found, using default`);
      }
    } else {
      console.error('  ⚠ Language dropdown not found, using default');
    }

    // ========================================================================
    // PHASE 7: Generate and enter prompt
    // ========================================================================

    console.error('[7/8] Generating and entering prompt...');

    // Generate prompt using Python script
    console.error('  → Calling afa-prompt-generator.py...');
    const promptText = generatePrompt(params.sourceName, params.languageCode);

    if (!promptText || promptText.length < 50) {
      throw new Error('Generated prompt is too short or empty');
    }

    console.error(`  ✓ Generated prompt (${promptText.length} chars)`);

    // Find textarea in customization dialog
    // There are 2 textareas on page: [0] = Chat query box, [1] = Customization dialog
    // Take the last one (most recent, in dialog)
    const textarea = page.locator('textarea').last();
    await textarea.waitFor({ state: 'visible', timeout: 5000 });

    // Focus and fill
    await textarea.focus();
    await page.waitForTimeout(300);
    await textarea.fill(promptText);
    await page.waitForTimeout(1000);

    console.error('  ✓ Prompt entered');

    // Click Generate button
    const generateButton = page.locator('button').filter({ hasText: /generate/i }).first();
    await generateButton.click();

    console.error('  → Generation started...');

    // ========================================================================
    // PHASE 8: Verify generation and check for errors
    // ========================================================================

    console.error('[8/8] Verifying generation...');

    await page.waitForTimeout(CONFIG.generationWait);

    // Check for daily limit error
    const dailyLimitText = await page.locator('text=/daily.*limit|limit.*reached/i').isVisible().catch(() => false);

    if (dailyLimitText) {
      const errorText = await page.locator('text=/daily.*limit|limit.*reached/i').textContent();

      // Take screenshot
      const screenshotPath = path.join(CONFIG.screenshotDir, `gemini-limit-${params.sourceName}.png`);
      await page.screenshot({ path: screenshotPath, fullPage: true });

      console.error('  ✗ Daily limit reached');
      console.error(`  → Screenshot: ${screenshotPath}`);

      return {
        success: false,
        error: errorText || 'You have reached your daily Audio Overview limits. Come back later.',
        errorType: 'daily_limit'
      };
    }

    // Check for other errors
    const errorElement = page.locator('[role="alert"], .error').first();
    const hasError = await errorElement.isVisible().catch(() => false);

    if (hasError) {
      const errorText = await errorElement.textContent();

      const screenshotPath = path.join(CONFIG.screenshotDir, `gemini-error-${params.sourceName}.png`);
      await page.screenshot({ path: screenshotPath, fullPage: true });

      console.error('  ✗ Generation error');
      console.error(`  → Screenshot: ${screenshotPath}`);

      return {
        success: false,
        error: errorText || 'Unknown error during generation',
        errorType: 'generation_failed'
      };
    }

    // Success - generation started
    const screenshotPath = path.join(CONFIG.screenshotDir, `gemini-success-${params.sourceName}-${params.languageCode}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });

    console.error('  ✓ Generation completed successfully');
    console.error(`  → Screenshot: ${screenshotPath}`);

    return {
      success: true,
      audioId: `${params.sourceName}_${params.languageCode}_${Date.now()}`
    };

  } catch (error: any) {
    console.error(`✗ Error: ${error.message}`);

    // Take error screenshot if page exists
    if (page) {
      try {
        const screenshotPath = path.join(CONFIG.screenshotDir, `gemini-exception-${Date.now()}.png`);
        await page.screenshot({ path: screenshotPath, fullPage: true });
        console.error(`  → Screenshot: ${screenshotPath}`);
      } catch (screenshotError) {
        // Ignore screenshot errors
      }
    }

    // Categorize error type
    let errorType: 'network' | 'unknown' = 'unknown';

    // Check if this is a network/timeout error (should be retried)
    if (error.message.includes('Timeout') ||
        error.message.includes('timeout') ||
        error.message.includes('Navigation') ||
        error.message.includes('net::ERR') ||
        error.message.includes('ECONNREFUSED')) {
      errorType = 'network';
    }

    return {
      success: false,
      error: error.message,
      errorType: errorType
    };

  } finally {
    // ========================================================================
    // Cleanup
    // ========================================================================

    if (browser && !useCDP) {
      // Only close browser if we launched it ourselves
      console.error('  → Closing browser');
      await browser.close();
    } else if (useCDP) {
      console.error('  → Keeping CDP browser open');
    }
  }
}

// ============================================================================
// CLI ENTRY POINT
// ============================================================================

async function main() {
  // Parse arguments
  const args = process.argv.slice(2);

  if (args.length < 3) {
    console.error('Usage: npx ts-node scripts/gemini/generate-audio.ts <sourceName> <languageCode> <notebookUrl> [headless]');
    console.error('Example: npx ts-node scripts/gemini/generate-audio.ts 0055_of_mice_and_men ja https://notebooklm.google.com/notebook/xxx');
    console.error('Example: npx ts-node scripts/gemini/generate-audio.ts 0055_of_mice_and_men ja https://notebooklm.google.com/notebook/xxx false');
    process.exit(1);
  }

  const params: AudioGenParams = {
    sourceName: args[0],
    languageCode: args[1],
    notebookUrl: args[2],
    headless: args[3] === 'false' ? false : args[3] === 'true' ? true : undefined
  };

  console.error(`\n=== NotebookLM Audio Generation ===`);
  console.error(`Source: ${params.sourceName}`);
  console.error(`Language: ${params.languageCode}`);
  console.error(`NotebookLM: ${params.notebookUrl}`);
  console.error('');

  // Run audio generation
  const result = await generateAudio(params);

  // Output JSON to stdout (for parent script to parse)
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

export { generateAudio, AudioGenParams, AudioGenResult };
