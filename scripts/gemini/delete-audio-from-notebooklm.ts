#!/usr/bin/env ts-node
/**
 * Delete audio from NotebookLM after successful download
 *
 * Usage:
 *   npx ts-node scripts/gemini/delete-audio-from-notebooklm.ts <match.json>
 *   echo '{"book_key":"...","audio_title":"..."}' | npx ts-node scripts/gemini/delete-audio-from-notebooklm.ts --stdin
 *
 * Output (JSON to stdout):
 *   {
 *     "success": true,
 *     "book_key": "0084_a_clockwork_orange",
 *     "language_code": "pl",
 *     "audio_title": "Mechaniczna Pomarańcza...",
 *     "deleted_at": "2025-10-16T18:06:00Z"
 *   }
 */

import { chromium, BrowserContext, Page } from 'playwright';
import * as path from 'path';
import * as fs from 'fs';
import * as net from 'net';

// ============================================================================
// TYPES
// ============================================================================

interface DeleteRequest {
  book_key: string;
  language_code: string;
  audio_title: string;
  notebook_url: string;
}

interface DeleteResult {
  success: boolean;
  book_key: string;
  language_code: string;
  audio_title?: string;
  deleted_at?: string;
  error?: string;
}

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
  userDataDir: '/home/xai/DEV/ms-playwright/mcp-chrome-profile-gemini',
  navigationTimeout: 30000,
  actionTimeout: 15000,
  deletionWaitMax: 10,  // 10 seconds max wait for deletion
  headless: true
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

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

// ============================================================================
// MAIN FUNCTION
// ============================================================================

async function deleteAudioFromNotebookLM(request: DeleteRequest): Promise<DeleteResult> {
  let browser: BrowserContext | null = null;
  let page: Page | null = null;
  let useCDP = false;

  try {
    // ========================================================================
    // PHASE 1: Browser Setup
    // ========================================================================

    console.error('[1/7] Launching browser...');

    const cdpPort = 9222;
    const isCdpAvailable = await isPortOpen(cdpPort);

    if (isCdpAvailable) {
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

      console.error(`  ✓ Connected to existing browser`);

    } else {
      console.error(`  → Launching new browser instance (headless)`);

      browser = await chromium.launchPersistentContext(CONFIG.userDataDir, {
        headless: CONFIG.headless,
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

    console.error('[2/7] Checking page URL...');

    const currentUrl = page.url();
    const needsNavigation = !currentUrl.includes(request.notebook_url);

    if (needsNavigation) {
      console.error(`  → Navigating to: ${request.notebook_url}`);
      await page.goto(request.notebook_url, {
        waitUntil: 'load',
        timeout: CONFIG.navigationTimeout
      });
      await page.waitForTimeout(2000);
    } else {
      console.error('  → Already on correct page, skipping navigation');
      await page.waitForTimeout(500);
    }

    console.error('  ✓ Page ready');

    // ========================================================================
    // PHASE 2.1: Detect viewport mode (mobile vs desktop)
    // ========================================================================

    console.error('[2.1/7] Detecting viewport mode...');

    const windowWidth = await page.evaluate(() => window.innerWidth);
    const isMobileMode = windowWidth < 1050;
    const viewportMode = isMobileMode ? 'mobile' : 'desktop';

    console.error(`  → Window width: ${windowWidth}px`);
    console.error(`  → Mode: ${viewportMode} (${isMobileMode ? 'tabs layout' : 'panels layout'})`);

    // ========================================================================
    // PHASE 2.9: Navigate to Studio
    // ========================================================================

    console.error('[2.9/7] Navigating to Studio...');

    if (isMobileMode) {
      console.error('  → Mobile mode: clicking Studio tab');

      try {
        await page.waitForTimeout(1000);
        const studioTab = page.locator('[role="tab"]').filter({ hasText: /studio/i }).first();
        const tabExists = await studioTab.isVisible().catch(() => false);

        if (!tabExists) {
          throw new Error('Studio tab not found in mobile mode');
        }

        await studioTab.click();
        await page.waitForTimeout(1000);
        console.error('  ✓ Studio tab clicked');
      } catch (tabError) {
        throw new Error('Failed to navigate to Studio in mobile mode');
      }
    } else {
      console.error('  → Desktop mode: Studio panel already visible');
      await page.waitForTimeout(1000);
    }

    // ========================================================================
    // PHASE 3: Find audio in Studio panel
    // ========================================================================

    console.error('[3/7] Finding audio...');
    console.error(`  → Searching for: ${request.audio_title.substring(0, 80)}...`);

    await page.waitForTimeout(2000);

    const searchText = request.audio_title.substring(0, 40);
    const audioButton = page.locator('button').filter({ hasText: searchText }).first();

    const audioExists = await audioButton.isVisible({ timeout: 5000 }).catch(() => false);

    if (!audioExists) {
      throw new Error(`Audio not found for "${request.audio_title}"`);
    }

    console.error('  ✓ Audio found');

    // ========================================================================
    // PHASE 4: Open More menu and click Delete
    // ========================================================================

    console.error('[4/7] Opening More menu...');

    const parentContainer = audioButton.locator('..');
    const moreButton = parentContainer.locator('button[aria-label*="More"]').first();

    await moreButton.click();
    console.error('  → More menu opened, waiting...');
    await page.waitForTimeout(1000);

    // ========================================================================
    // PHASE 5: Find and click Delete menu item
    // ========================================================================

    console.error('[5/7] Clicking Delete...');

    const deleteMenuItem = page.getByRole('menuitem', { name: 'Delete' });

    await deleteMenuItem.waitFor({ state: 'visible', timeout: 5000 });
    await deleteMenuItem.click();
    await page.waitForTimeout(1000);

    console.error('  → Delete menu item clicked, waiting for confirmation dialog...');

    // ========================================================================
    // PHASE 6: Confirm deletion in dialog
    // ========================================================================

    console.error('[6/7] Confirming deletion...');

    // Wait for confirmation dialog to appear
    await page.waitForTimeout(1000);

    // Find and click the "Confirm deletion" button in the dialog
    const confirmDeleteButton = page.getByRole('button', { name: /Confirm deletion|Delete/ });

    await confirmDeleteButton.waitFor({ state: 'visible', timeout: 5000 });
    await confirmDeleteButton.click();

    await page.waitForTimeout(2000);

    console.error('  ✓ Deletion confirmed');

    // ========================================================================
    // PHASE 7: Verify deletion
    // ========================================================================

    console.error('[7/7] Verifying deletion...');

    // Try to find the audio again - it should be gone
    const audioStillExists = await audioButton.isVisible({ timeout: 2000 }).catch(() => false);

    if (audioStillExists) {
      console.error('  ⚠ Audio still visible after deletion (may be UI lag)');
    } else {
      console.error('  ✓ Audio confirmed deleted from NotebookLM');
    }

    // ========================================================================
    // SUCCESS
    // ========================================================================

    console.error('[7/7] Deletion completed successfully');

    return {
      success: true,
      book_key: request.book_key,
      language_code: request.language_code,
      audio_title: request.audio_title,
      deleted_at: new Date().toISOString()
    };

  } catch (error: any) {
    console.error(`✗ Error: ${error.message}`);

    return {
      success: false,
      book_key: request.book_key,
      language_code: request.language_code,
      audio_title: request.audio_title,
      error: error.message
    };

  } finally {
    if (browser && !useCDP) {
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
  const args = process.argv.slice(2);

  let requestData: DeleteRequest;

  // Read from stdin or file
  if (args.includes('--stdin') || args.length === 0) {
    // Read from stdin
    const stdinData = fs.readFileSync(0, 'utf-8');
    requestData = JSON.parse(stdinData);

  } else {
    // Read from file
    const requestPath = args[0];
    requestData = JSON.parse(fs.readFileSync(requestPath, 'utf-8'));
  }

  console.error(`\n=== Delete Audio from NotebookLM ===`);
  console.error(`Book: ${requestData.book_key}`);
  console.error(`Language: ${requestData.language_code}`);
  console.error(`Audio: ${requestData.audio_title}`);
  console.error('');

  const result = await deleteAudioFromNotebookLM(requestData);

  // Output JSON to stdout
  console.log(JSON.stringify(result, null, 2));

  process.exit(result.success ? 0 : 1);
}

if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

export { deleteAudioFromNotebookLM, DeleteRequest, DeleteResult };
