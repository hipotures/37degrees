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
  downloadDir: '/tmp/playwright-mcp-output',
  navigationTimeout: 30000,
  actionTimeout: 15000,
  downloadWaitMax: 120,  // 2 minutes max wait for download
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

async function waitForDownload(downloadDir: string, maxWaitSeconds: number, timestampBefore: number): Promise<string | null> {
  const startTime = Date.now();

  while ((Date.now() - startTime) / 1000 < maxWaitSeconds) {
    if (!fs.existsSync(downloadDir)) {
      await new Promise(resolve => setTimeout(resolve, 2000));
      continue;
    }

    const files = fs.readdirSync(downloadDir)
      .filter(f => f.endsWith('.mp4') || f.endsWith('.m4a'))
      .map(f => ({
        name: f,
        path: path.join(downloadDir, f),
        mtime: fs.statSync(path.join(downloadDir, f)).mtime.getTime()
      }))
      .filter(f => f.mtime >= timestampBefore)  // Only files newer than timestamp_before
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

    console.error('[1/6] Launching browser...');

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
    // PHASE 2: Navigate to NotebookLM
    // ========================================================================

    console.error('[2/6] Navigating to NotebookLM...');
    console.error(`  → URL: ${match.notebook_url}`);

    await page.goto(match.notebook_url, {
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
    // PHASE 3: Find audio in Studio panel
    // ========================================================================

    console.error('[3/6] Finding audio...');
    console.error(`  → Searching for: ${match.audio_title}`);

    await page.waitForTimeout(1000);

    const audioElement = page.locator('button').filter({ hasText: match.audio_title }).first();
    const audioExists = await audioElement.isVisible().catch(() => false);

    if (!audioExists) {
      throw new Error(`Audio not found for "${match.audio_title}"`);
    }

    console.error('  ✓ Audio found');

    // ========================================================================
    // PHASE 4: Open More menu and click Download
    // ========================================================================

    console.error('[4/6] Downloading audio...');

    // Record timestamp BEFORE download
    timestampBefore = Date.now();

    const moreButton = audioElement.locator('..').locator('button').filter({ hasText: /more/i }).or(
      audioElement.locator('..').locator('button[aria-label*="More"]')
    ).first();

    await moreButton.click();
    await page.waitForTimeout(1000);

    const downloadMenuItem = page.locator('text="Download"').or(
      page.locator('[role="menuitem"]').filter({ hasText: /download/i })
    ).first();

    const downloadSubdir = findNewestDownloadSubdir() || CONFIG.downloadDir;
    console.error(`  → Download directory: ${downloadSubdir}`);

    await downloadMenuItem.click();
    await page.waitForTimeout(2000);

    console.error('  → Download started...');

    // ========================================================================
    // PHASE 5: Wait for download completion
    // ========================================================================

    console.error('[5/6] Waiting for download...');

    const downloadedFile = await waitForDownload(downloadSubdir, CONFIG.downloadWaitMax, timestampBefore);

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

    console.error('[6/6] Download completed successfully');

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
