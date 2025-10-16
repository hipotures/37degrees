#!/usr/bin/env ts-node
/**
 * Single audio download with timestamp tracking (no file move)
 *
 * Usage:
 *   npx ts-node scripts/gemini/download-single-audio.ts <match.json>
 *   echo '{"book_key":"...","audio_title":"..."}' | npx ts-node scripts/gemini/download-single-audio.ts --stdin
 *
 * Output (JSON to stdout):
 *   {
 *     "success": true,
 *     "book_key": "0057_east_of_eden",
 *     "language_code": "pt",
 *     "file_path": "/tmp/playwright-mcp-output/NotebookLM_audio_123.mp4",
 *     "timestamp_before": 1696934400,
 *     "timestamp_after": 1696934430
 *   }
 */

import { chromium, BrowserContext, Page } from 'playwright';
import * as path from 'path';
import * as fs from 'fs';
import * as net from 'net';

// ============================================================================
// TYPES
// ============================================================================

interface Match {
  book_key: string;
  language_code: string;
  audio_title: string;
  audio_ref?: string;
  notebook_url: string;
}

interface DownloadResult {
  success: boolean;
  book_key: string;
  language_code: string;
  file_path?: string;
  timestamp_before?: number;
  timestamp_after?: number;
  error?: string;
  errorType?: 'not_found' | 'download_timeout' | 'network' | 'unknown';
}

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
  userDataDir: '/home/xai/DEV/ms-playwright/mcp-chrome-profile-gemini',
  downloadDirBase: '/tmp/playwright-mcp-output',
  navigationTimeout: 30000,
  actionTimeout: 15000,
  downloadWaitMax: 10,  // 10 seconds max wait for download
  screenshotDir: '/tmp',
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

function buildDownloadDir(bookKey: string, languageCode: string): string {
  return path.join(CONFIG.downloadDirBase, `${bookKey}_${languageCode}`);
}

function findNewestDownloadSubdir(): string | null {
  if (!fs.existsSync(CONFIG.downloadDirBase)) {
    return null;
  }

  const subdirs = fs.readdirSync(CONFIG.downloadDirBase)
    .filter(name => {
      const fullPath = path.join(CONFIG.downloadDirBase, name);
      return fs.statSync(fullPath).isDirectory();
    })
    .map(name => ({
      name,
      path: path.join(CONFIG.downloadDirBase, name),
      mtime: fs.statSync(path.join(CONFIG.downloadDirBase, name)).mtime.getTime()
    }))
    .sort((a, b) => b.mtime - a.mtime);

  return subdirs.length > 0 ? subdirs[0].path : null;
}

async function waitForDownload(downloadDir: string, maxWaitSeconds: number): Promise<string | null> {
  const startTime = Date.now();
  let lastStatus = '';

  while ((Date.now() - startTime) / 1000 < maxWaitSeconds) {
    const elapsed = Math.round((Date.now() - startTime) / 1000);

    if (!fs.existsSync(downloadDir)) {
      if (lastStatus !== 'waiting_dir') {
        console.error(`  ↳ [${elapsed}s] Waiting for download directory...`);
        lastStatus = 'waiting_dir';
      }
      await new Promise(resolve => setTimeout(resolve, 500));
      continue;
    }

    try {
      const files = fs.readdirSync(downloadDir)
        .filter(f => {
          const fullPath = path.join(downloadDir, f);
          try {
            return !fs.statSync(fullPath).isDirectory() && (f.endsWith('.mp4') || f.endsWith('.m4a'));
          } catch {
            return false;
          }
        });

      if (files.length === 1) {
        const filePath = path.join(downloadDir, files[0]);
        const fileSize = fs.statSync(filePath).size;
        console.error(`  ✓ [${elapsed}s] Found file: ${files[0]} (${(fileSize / 1024 / 1024).toFixed(1)} MB)`);
        return filePath;
      } else if (files.length > 1) {
        // Multiple files - this shouldn't happen with isolated download dirs
        console.error(`  ⚠ [${elapsed}s] Found ${files.length} files (should be 1):`);
        files.forEach(f => console.error(`    - ${f}`));
        // Return the newest one
        const newest = files
          .map(f => ({
            name: f,
            path: path.join(downloadDir, f),
            mtime: fs.statSync(path.join(downloadDir, f)).mtime.getTime()
          }))
          .sort((a, b) => b.mtime - a.mtime)[0];
        return newest.path;
      } else {
        // No files yet
        if (lastStatus !== 'waiting_files') {
          console.error(`  ↳ [${elapsed}s] Waiting for files in directory...`);
          lastStatus = 'waiting_files';
        }
      }
    } catch (e) {
      console.error(`  ⚠ [${elapsed}s] Error reading directory: ${e}`);
    }

    await new Promise(resolve => setTimeout(resolve, 500));
  }

  console.error(`  ✗ Timeout after ${maxWaitSeconds}s - no file found`);
  return null;
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

async function downloadSingleAudio(match: Match): Promise<DownloadResult> {
  let browser: BrowserContext | null = null;
  let page: Page | null = null;
  let useCDP = false;
  let timestampBefore = 0;
  let timestampAfter = 0;

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

      console.error(`  ✓ Connected to existing browser`);

    } else {
      console.error(`  → Launching new browser instance (headless)`);

      browser = await chromium.launchPersistentContext(CONFIG.userDataDir, {
        headless: CONFIG.headless,
        viewport: { width: 1920, height: 1080 },
        acceptDownloads: true,
        args: [
          '--no-sandbox',
          '--disable-blink-features=AutomationControlled'
        ]
      });

      page = browser.pages()[0] || await browser.newPage();
    }

    // ========================================================================
    // PHASE 2: Navigate to NotebookLM (skip if already on page)
    // ========================================================================

    console.error('[2/8] Checking page URL...');

    const currentUrl = page.url();
    const needsNavigation = !currentUrl.includes(match.notebook_url);

    if (needsNavigation) {
      console.error(`  → Navigating to: ${match.notebook_url}`);
      await page.goto(match.notebook_url, {
        waitUntil: 'load',
        timeout: CONFIG.navigationTimeout
      });
      await page.waitForTimeout(2000);
    } else {
      console.error('  → Already on correct page, skipping navigation');
      await page.waitForTimeout(500);
    }

    const isLoginRequired = await page.locator('text="Sign in"').isVisible().catch(() => false);
    if (isLoginRequired) {
      throw new Error('User not logged in to Google. Please log in manually first.');
    }

    console.error('  ✓ Page ready');

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
    // PHASE 2.9: Navigate to Studio
    // ========================================================================

    console.error('[2.9/8] Navigating to Studio...');

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
    // PHASE 3: Find audio in Studio panel
    // ========================================================================

    console.error('[3/8] Finding audio...');
    console.error(`  → Searching for: ${match.audio_title.substring(0, 80)}...`);

    await page.waitForTimeout(2000);

    // Find audio button using partial text match (first 40 chars)
    const searchText = match.audio_title.substring(0, 40);

    const audioButton = page.locator('button').filter({ hasText: searchText }).first();

    const audioExists = await audioButton.isVisible({ timeout: 5000 }).catch(() => false);

    if (!audioExists) {
      throw new Error(`Audio not found for "${match.audio_title}"`);
    }

    console.error('  ✓ Audio found');

    // ========================================================================
    // PHASE 4: Open More menu and click Download
    // ========================================================================

    console.error('[4/8] Downloading audio...');

    // Record timestamp BEFORE download
    timestampBefore = Date.now();

    // Find More button - navigate to parent container and find More button there
    const parentContainer = audioButton.locator('..');
    const moreButton = parentContainer.locator('button[aria-label*="More"]').first();

    await moreButton.click();
    console.error('  → More menu opened, waiting...');
    await page.waitForTimeout(1000);

    // Find Download menuitem using role
    const downloadMenuItem = page.getByRole('menuitem', { name: 'Download' });

    // Wait for download button to be visible
    console.error('  → Waiting for Download button...');
    await downloadMenuItem.waitFor({ state: 'visible', timeout: 5000 });

    // Build download directory specific to this book and language
    const downloadSubdir = buildDownloadDir(match.book_key, match.language_code);

    // Create download directory if it doesn't exist
    if (!fs.existsSync(downloadSubdir)) {
      fs.mkdirSync(downloadSubdir, { recursive: true });
    }

    console.error(`  → Download directory: ${downloadSubdir}`);

    // Set download behavior for CDP browser (BEFORE clicking download)
    if (useCDP && browser) {
      try {
        const cdpSession = await browser.newCDPSession(page);
        await cdpSession.send('Browser.setDownloadBehavior', {
          behavior: 'allow',
          downloadPath: downloadSubdir
        });
        console.error(`  → CDP download path configured`);
      } catch (cdpError) {
        console.error(`  ⚠ Could not configure CDP download path: ${cdpError}`);
      }
    }

    await downloadMenuItem.click();
    await page.waitForTimeout(2000);

    console.error('  → Download started...');

    // ========================================================================
    // PHASE 5: Wait for download completion
    // ========================================================================

    console.error('[5/8] Waiting for download...');

    const downloadedFile = await waitForDownload(downloadSubdir, CONFIG.downloadWaitMax);

    timestampAfter = Date.now();

    if (!downloadedFile) {
      throw new Error(`Download timeout after ${CONFIG.downloadWaitMax} seconds`);
    }

    console.error(`  ✓ Downloaded: ${path.basename(downloadedFile)}`);

    const stats = fs.statSync(downloadedFile);
    const fileSizeMB = (stats.size / (1024 * 1024)).toFixed(2);
    console.error(`  → Size: ${fileSizeMB} MB`);

    // ========================================================================
    // PHASE 6: Success
    // ========================================================================

    console.error('[6/8] Download completed successfully');

    return {
      success: true,
      book_key: match.book_key,
      language_code: match.language_code,
      file_path: downloadedFile,
      timestamp_before: Math.floor(timestampBefore / 1000),
      timestamp_after: Math.floor(timestampAfter / 1000)
    };

  } catch (error: any) {
    console.error(`✗ Error: ${error.message}`);

    timestampAfter = Date.now();

    // Categorize error type
    let errorType: 'not_found' | 'download_timeout' | 'network' | 'unknown' = 'unknown';

    if (error.message.includes('not found')) {
      errorType = 'not_found';
    } else if (error.message.includes('timeout') || error.message.includes('Timeout')) {
      if (error.message.includes('Download timeout')) {
        errorType = 'download_timeout';
      } else {
        errorType = 'network';
      }
    }

    return {
      success: false,
      book_key: match.book_key,
      language_code: match.language_code,
      error: error.message,
      errorType: errorType,
      timestamp_before: timestampBefore > 0 ? Math.floor(timestampBefore / 1000) : undefined,
      timestamp_after: Math.floor(timestampAfter / 1000)
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

  let matchData: Match;

  // Read from stdin or file
  if (args.includes('--stdin') || args.length === 0) {
    // Read from stdin
    const stdinData = fs.readFileSync(0, 'utf-8');
    matchData = JSON.parse(stdinData);

  } else {
    // Read from file
    const matchPath = args[0];
    matchData = JSON.parse(fs.readFileSync(matchPath, 'utf-8'));
  }

  console.error(`\n=== Single Audio Download ===`);
  console.error(`Book: ${matchData.book_key}`);
  console.error(`Language: ${matchData.language_code}`);
  console.error(`Audio: ${matchData.audio_title}`);
  console.error('');

  const result = await downloadSingleAudio(matchData);

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

export { downloadSingleAudio, Match, DownloadResult };
