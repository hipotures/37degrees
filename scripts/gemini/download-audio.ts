#!/usr/bin/env ts-node
/**
 * Standalone Playwright automation for downloading audio from NotebookLM
 *
 * Usage:
 *   npx ts-node scripts/gemini/download-audio.ts <bookKey> <languageCode> <notebookUrl> [audioTitle] [headless]
 *
 * Example:
 *   npx ts-node scripts/gemini/download-audio.ts 0055_of_mice_and_men ja https://notebooklm.google.com/notebook/xxx
 *   npx ts-node scripts/gemini/download-audio.ts 0055_of_mice_and_men ja https://notebooklm.google.com/notebook/xxx "Audio Title" false
 *
 * Output (JSON to stdout):
 *   {"success": true, "filePath": "/path/to/file.mp4"}
 *   {"success": false, "error": "Audio not found", "errorType": "not_found"}
 */

import { chromium, BrowserContext, Page } from 'playwright';
import * as path from 'path';
import * as fs from 'fs';
import * as net from 'net';

// ============================================================================
// TYPES
// ============================================================================

interface DownloadParams {
  bookKey: string;
  languageCode: string;
  notebookUrl: string;
  audioTitle?: string;
  headless?: boolean;
}

interface DownloadResult {
  success: boolean;
  filePath?: string;
  error?: string;
  errorType?: 'not_found' | 'download_timeout' | 'move_failed' | 'network' | 'unknown';
}

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
  // Persistent browser profile for Gemini/NotebookLM
  userDataDir: '/home/xai/DEV/ms-playwright/mcp-chrome-profile-gemini',

  // Base paths
  projectRoot: '/home/xai/DEV/37degrees',
  downloadDir: '/tmp/playwright-mcp-output',

  // Timeouts
  navigationTimeout: 30000,  // 30 seconds
  actionTimeout: 15000,      // 15 seconds
  downloadWaitMax: 120,      // 2 minutes max wait for download

  // Screenshots
  screenshotDir: '/tmp',

  // Headless mode
  headless: true,

  // Viewport size (affects NotebookLM UI layout)
  // CRITICAL: NotebookLM layout boundary at 1050px width:
  //   - < 1050px: Mobile mode with tabs (Sources/Chat/Studio) - requires clicking tab
  //   - >= 1050px: Desktop mode with panels - all sections visible at once
  // Default 1920x1080 ensures desktop mode for reliable automation
  viewport: {
    width: 1920,
    height: 1080
  }
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
 * Find newest subdirectory in download directory
 */
function findNewestDownloadSubdir(): string | null {
  if (!fs.existsSync(CONFIG.downloadDir)) {
    return null;
  }

  const subdirs = fs.readdirSync(CONFIG.downloadDir)
    .filter(name => {
      const fullPath = path.join(CONFIG.downloadDir, name);
      return fs.statSync(fullPath).isDirectory();
    })
    .map(name => ({
      name,
      path: path.join(CONFIG.downloadDir, name),
      mtime: fs.statSync(path.join(CONFIG.downloadDir, name)).mtime.getTime()
    }))
    .sort((a, b) => b.mtime - a.mtime);

  return subdirs.length > 0 ? subdirs[0].path : null;
}

/**
 * Wait for MP4 file to appear in download directory
 */
async function waitForDownload(downloadDir: string, maxWaitSeconds: number): Promise<string | null> {
  const startTime = Date.now();

  while ((Date.now() - startTime) / 1000 < maxWaitSeconds) {
    if (!fs.existsSync(downloadDir)) {
      await new Promise(resolve => setTimeout(resolve, 2000));
      continue;
    }

    const files = fs.readdirSync(downloadDir)
      .filter(f => f.endsWith('.mp4'))
      .map(f => ({
        name: f,
        path: path.join(downloadDir, f),
        mtime: fs.statSync(path.join(downloadDir, f)).mtime.getTime()
      }))
      .sort((a, b) => b.mtime - a.mtime);

    if (files.length > 0) {
      return files[0].path;
    }

    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  return null;
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

async function downloadAudio(params: DownloadParams): Promise<DownloadResult> {
  let browser: BrowserContext | null = null;
  let page: Page | null = null;
  let useCDP = false;

  try {
    // ========================================================================
    // PHASE 1: Browser Setup
    // ========================================================================

    console.error('[1/8] Launching browser...');

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

      console.error(`  ✓ Connected to existing browser (${pages.length} pages)`);

    } else {
      const headlessMode = params.headless !== undefined ? params.headless : CONFIG.headless;
      console.error(`  → Launching new browser instance`);
      console.error(`  → Headless mode: ${headlessMode}`);
      console.error(`  → Viewport: ${CONFIG.viewport.width}x${CONFIG.viewport.height}`);

      browser = await chromium.launchPersistentContext(CONFIG.userDataDir, {
        headless: headlessMode,
        viewport: CONFIG.viewport,
        acceptDownloads: true,
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
      waitUntil: 'load',
      timeout: CONFIG.navigationTimeout
    });

    await page.waitForTimeout(3000);

    const isLoginRequired = await page.locator('text="Sign in"').isVisible().catch(() => false);
    if (isLoginRequired) {
      throw new Error('User not logged in to Google. Please log in manually first.');
    }

    console.error('  ✓ NotebookLM loaded');

    // ========================================================================
    // PHASE 2.1: Detect viewport mode (mobile vs desktop)
    // ========================================================================

    console.error('[2.1/8] Detecting viewport mode...');

    const windowWidth = await page.evaluate(() => window.innerWidth);
    const isMobileMode = windowWidth < 1050;
    const viewportMode = isMobileMode ? 'mobile' : 'desktop';

    console.error(`  → Window width: ${windowWidth}px`);
    console.error(`  → Mode: ${viewportMode} (${isMobileMode ? 'tabs layout' : 'panels layout'})`);

    // ========================================================================
    // PHASE 2.5: Deselect all sources for safety
    // ========================================================================

    console.error('[2.5/8] Deselecting all sources...');

    // NOTE: By default all sources are selected in NotebookLM
    // Uncheck all sources using main "Select all sources" checkbox (for security)
    // This prevents accidental audio generation when clicking buttons

    try {
      if (isMobileMode) {
        // Mobile mode: Navigate to Sources tab first
        console.error('  → Mobile mode: navigating to Sources tab');

        const sourcesTab = page.locator('[role="tab"]').filter({ hasText: /sources/i }).first();
        const sourcesTabExists = await sourcesTab.isVisible().catch(() => false);

        if (sourcesTabExists) {
          await sourcesTab.click();
          await page.waitForTimeout(1000);
          console.error('  ✓ Sources tab opened');
        } else {
          console.error('  ⚠ Sources tab not found');
        }
      } else {
        // Desktop mode: Sources panel already visible
        console.error('  → Desktop mode: Sources panel already visible');
      }

      // Wait for checkboxes to be available
      await page.waitForTimeout(1000);

      // Find and click the "Select all sources" checkbox to deselect all
      const selectAllCheckbox = page.locator('input[type="checkbox"]').first();
      const isCheckboxVisible = await selectAllCheckbox.isVisible().catch(() => false);

      if (isCheckboxVisible) {
        // Check if currently selected (checked)
        const isChecked = await selectAllCheckbox.isChecked().catch(() => false);

        if (isChecked) {
          await selectAllCheckbox.click();
          await page.waitForTimeout(500);
          console.error('  ✓ All sources deselected');
        } else {
          console.error('  → Sources already deselected');
        }
      } else {
        console.error('  → Select all checkbox not found (might be optional)');
      }
    } catch (deselectError) {
      // Non-critical error, continue with download
      console.error('  ⚠ Could not deselect sources (continuing anyway)');
    }

    // ========================================================================
    // PHASE 3: Navigate to Studio
    // ========================================================================

    console.error('[3/8] Navigating to Studio...');

    if (isMobileMode) {
      // Mobile mode: Click Studio tab
      console.error('  → Mobile mode: clicking Studio tab');

      try {
        // Wait for tabs to be available
        await page.waitForTimeout(1000);

        // Find and click Studio tab
        const studioTab = page.locator('[role="tab"]').filter({ hasText: /studio/i }).first();
        const tabExists = await studioTab.isVisible().catch(() => false);

        if (!tabExists) {
          throw new Error('Studio tab not found in mobile mode');
        }

        await studioTab.click();
        await page.waitForTimeout(1000);

        console.error('  ✓ Studio tab clicked');
      } catch (tabError) {
        console.error(`  ⚠ Could not click Studio tab: ${tabError}`);
        throw new Error('Failed to navigate to Studio in mobile mode');
      }
    } else {
      // Desktop mode: Studio panel already visible
      console.error('  → Desktop mode: Studio panel already visible');
      await page.waitForTimeout(1000);
    }

    // ========================================================================
    // PHASE 4: Find audio in Studio panel
    // ========================================================================

    console.error('[4/8] Finding audio...');

    // Find audio by title or book key
    const searchText = params.audioTitle || params.bookKey;
    console.error(`  → Searching for: ${searchText}`);

    // Look for audio element containing search text
    const audioElement = page.locator('button').filter({ hasText: searchText }).first();
    const audioExists = await audioElement.isVisible().catch(() => false);

    if (!audioExists) {
      throw new Error(`Audio not found for "${searchText}"`);
    }

    console.error('  ✓ Audio found');

    // ========================================================================
    // PHASE 5: Open More menu and click Download
    // ========================================================================

    console.error('[5/8] Downloading audio...');

    // Find More button (three dots) near the audio
    const moreButton = audioElement.locator('..').locator('button').filter({ hasText: /more/i }).or(
      audioElement.locator('..').locator('button[aria-label*="More"]')
    ).first();

    await moreButton.click();
    await page.waitForTimeout(1000);

    // Click Download in menu
    const downloadMenuItem = page.locator('text="Download"').or(
      page.locator('[role="menuitem"]').filter({ hasText: /download/i })
    ).first();

    // Get download subdirectory before clicking
    const downloadSubdir = findNewestDownloadSubdir() || CONFIG.downloadDir;
    console.error(`  → Download directory: ${downloadSubdir}`);

    await downloadMenuItem.click();
    await page.waitForTimeout(2000);

    console.error('  → Download started...');

    // ========================================================================
    // PHASE 6: Wait for download completion
    // ========================================================================

    console.error('[6/8] Waiting for download...');

    const downloadedFile = await waitForDownload(downloadSubdir, CONFIG.downloadWaitMax);

    if (!downloadedFile) {
      throw new Error(`Download timeout after ${CONFIG.downloadWaitMax} seconds`);
    }

    console.error(`  ✓ Downloaded: ${path.basename(downloadedFile)}`);

    // ========================================================================
    // PHASE 7: Move file to target location
    // ========================================================================

    console.error('[7/8] Moving file...');

    const targetDir = path.join(CONFIG.projectRoot, 'books', params.bookKey, 'audio');
    const targetFilename = `${params.bookKey}_${params.languageCode}.mp4`;
    const targetPath = path.join(targetDir, targetFilename);

    // Check if directory exists
    if (!fs.existsSync(targetDir)) {
      throw new Error(`Target directory does not exist: ${targetDir}`);
    }

    // Move file
    fs.renameSync(downloadedFile, targetPath);

    // Verify
    if (!fs.existsSync(targetPath)) {
      throw new Error(`Failed to move file to ${targetPath}`);
    }

    const stats = fs.statSync(targetPath);
    const fileSizeMB = (stats.size / (1024 * 1024)).toFixed(2);

    console.error(`  ✓ File moved: ${targetPath}`);
    console.error(`  → Size: ${fileSizeMB} MB`);

    // ========================================================================
    // PHASE 8: Success
    // ========================================================================

    const screenshotPath = path.join(CONFIG.screenshotDir, `gemini-download-success-${params.bookKey}-${params.languageCode}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });

    console.error('[8/8] Download completed successfully');
    console.error(`  → Screenshot: ${screenshotPath}`);

    return {
      success: true,
      filePath: targetPath
    };

  } catch (error: any) {
    console.error(`✗ Error: ${error.message}`);

    if (page) {
      try {
        const screenshotPath = path.join(CONFIG.screenshotDir, `gemini-download-error-${Date.now()}.png`);
        await page.screenshot({ path: screenshotPath, fullPage: true });
        console.error(`  → Screenshot: ${screenshotPath}`);
      } catch (screenshotError) {
        // Ignore screenshot errors
      }
    }

    // Categorize error type
    let errorType: 'not_found' | 'download_timeout' | 'move_failed' | 'network' | 'unknown' = 'unknown';

    if (error.message.includes('not found')) {
      errorType = 'not_found';
    } else if (error.message.includes('timeout') || error.message.includes('Timeout')) {
      if (error.message.includes('Download timeout')) {
        errorType = 'download_timeout';
      } else {
        errorType = 'network';
      }
    } else if (error.message.includes('move') || error.message.includes('directory')) {
      errorType = 'move_failed';
    }

    return {
      success: false,
      error: error.message,
      errorType: errorType
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

  if (args.length < 3) {
    console.error('Usage: npx ts-node scripts/gemini/download-audio.ts <bookKey> <languageCode> <notebookUrl> [audioTitle] [headless]');
    console.error('Example: npx ts-node scripts/gemini/download-audio.ts 0055_of_mice_and_men ja https://notebooklm.google.com/notebook/xxx');
    console.error('Example: npx ts-node scripts/gemini/download-audio.ts 0055_of_mice_and_men ja https://notebooklm.google.com/notebook/xxx "Audio Title" false');
    process.exit(1);
  }

  const params: DownloadParams = {
    bookKey: args[0],
    languageCode: args[1],
    notebookUrl: args[2],
    audioTitle: args[3] && args[3] !== 'undefined' && args[3] !== '' ? args[3] : undefined,
    headless: args[4] === 'false' ? false : args[4] === 'true' ? true : undefined
  };

  console.error(`\n=== NotebookLM Audio Download ===`);
  console.error(`Book: ${params.bookKey}`);
  console.error(`Language: ${params.languageCode}`);
  console.error(`NotebookLM: ${params.notebookUrl}`);
  if (params.audioTitle) {
    console.error(`Audio title: ${params.audioTitle}`);
  }
  console.error('');

  const result = await downloadAudio(params);

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

export { downloadAudio, DownloadParams, DownloadResult };
