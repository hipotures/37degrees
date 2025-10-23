#!/usr/bin/env ts-node
/**
 * Standalone Playwright automation for downloading AFA Deep Research from Gemini
 *
 * Workflow (12 phases):
 * 1. Read GEMINI_AFA_URL from TODOIT
 * 2. Navigate to Gemini chat
 * 3. Export to Google Docs
 * 4. Switch to Docs tab
 * 5. Rename document
 * 6. Setup download directory (/tmp/playwright-mcp-output/{book_key})
 * 7. Download as TXT
 * 8. Find downloaded file
 * 9. Move to books/{book}/docs/gemini-afa.txt
 * 10. Verify content
 * 11. Close Docs tab
 * 12. Return to Gemini
 *
 * Usage:
 *   npx ts-node scripts/gemini/execute-deep-research-afa-dwn.ts <sourceName> [headless]
 *
 * Example:
 *   npx ts-node scripts/gemini/execute-deep-research-afa-dwn.ts 0055_of_mice_and_men
 *   npx ts-node scripts/gemini/execute-deep-research-afa-dwn.ts 0055_of_mice_and_men false
 *
 * Output (JSON to stdout):
 *   {"success": true, "filePath": "/path/to/file.txt", "fileSize": 12345}
 *   {"success": false, "error": "Export failed", "errorType": "export_failed"}
 */

import { chromium, BrowserContext, Page } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';
import * as net from 'net';

// ============================================================================
// TYPES
// ============================================================================

interface DownloadParams {
  sourceName: string;
  headless?: boolean;
  format?: 'txt' | 'pdf' | 'docx' | 'odt' | 'rtf' | 'html' | 'epub' | 'md';
}

interface DownloadResult {
  success: boolean;
  filePath?: string;
  fileSize?: number;
  error?: string;
  errorType?: 'url_not_found' | 'export_failed' | 'download_failed' | 'file_move_failed' | 'tab_switch_failed' | 'unknown';
}

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
  // Persistent browser profile for Gemini
  userDataDir: '/home/xai/DEV/ms-playwright/mcp-chrome-profile-gemini',

  // Base paths
  projectRoot: '/home/xai/DEV/37degrees',
  downloadDir: '/tmp/playwright-mcp-output',

  // Timeouts
  navigationTimeout: 30000,     // 30 seconds
  actionTimeout: 15000,          // 15 seconds
  pageLoadWait: 3000,            // 3 seconds after navigation
  exportWait: 5000,              // 5 seconds after export click
  downloadWait: 10000,           // 10 seconds for file download

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
 * Read GEMINI_AFA_URL from TODOIT (MOCK for now)
 */
function readGeminiAfaUrl(sourceName: string): string {
  // TODO: Implement using todoit CLI when list structure is ready
  // For now, return mock URL or read from environment variable for testing

  console.error('[MOCK] Reading GEMINI_AFA_URL from TODOIT');
  console.error(`  → List: gemini-afa-research`);
  console.error(`  → Item: ${sourceName}`);
  console.error(`  → Property: GEMINI_AFA_URL`);

  // Check if URL provided via environment variable for testing
  const mockUrl = process.env.GEMINI_AFA_URL;
  if (mockUrl) {
    console.error(`  ✓ Using URL from environment: ${mockUrl}`);
    return mockUrl;
  }

  throw new Error(
    'GEMINI_AFA_URL not found. ' +
    'Set GEMINI_AFA_URL environment variable or implement TODOIT integration'
  );
}

/**
 * Get file extension for format
 */
function getFileExtension(format: string): string {
  const extensions: Record<string, string> = {
    'txt': '.txt',
    'pdf': '.pdf',
    'docx': '.docx',
    'odt': '.odt',
    'rtf': '.rtf',
    'html': '.zip', // HTML is zipped
    'epub': '.epub',
    'md': '.md'
  };
  return extensions[format] || '.txt';
}

/**
 * Get Google Docs menu text for format
 */
function getDownloadMenuText(format: string): string {
  const menuTexts: Record<string, string> = {
    'txt': 'Plain text',
    'pdf': 'PDF',
    'docx': 'Microsoft Word',
    'odt': 'OpenDocument',
    'rtf': 'Rich Text',
    'html': 'Web page',
    'epub': 'EPUB',
    'md': 'Markdown'
  };
  return menuTexts[format] || 'Plain text';
}

/**
 * Find latest downloaded file in download directory
 */
function findLatestDownload(downloadDir: string, format: string): string | null {
  if (!fs.existsSync(downloadDir)) {
    console.error(`  ⚠ Download directory not found: ${downloadDir}`);
    return null;
  }

  const expectedExt = getFileExtension(format);

  // Search for files with expected extension
  const files = fs.readdirSync(downloadDir)
    .filter(f => {
      const fullPath = path.join(downloadDir, f);
      return !fs.statSync(fullPath).isDirectory() && f.endsWith(expectedExt);
    })
    .sort((a, b) => {
      // Sort by modification time (newest first)
      const aPath = path.join(downloadDir, a);
      const bPath = path.join(downloadDir, b);
      return fs.statSync(bPath).mtime.getTime() - fs.statSync(aPath).mtime.getTime();
    });

  if (files.length > 0) {
    const filePath = path.join(downloadDir, files[0]);
    console.error(`  ✓ Found file: ${filePath}`);
    return filePath;
  }

  console.error(`  ⚠ No .txt files found in ${downloadDir}`);
  return null;
}

/**
 * Take screenshot with descriptive name
 */
async function takeScreenshot(page: Page, name: string): Promise<void> {
  const timestamp = Date.now();
  const screenshotPath = path.join(CONFIG.screenshotDir, `gemini-afa-download-${name}-${timestamp}.png`);
  await page.screenshot({ path: screenshotPath, fullPage: false });
  console.error(`  → Screenshot: ${screenshotPath}`);
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

async function downloadAfaResearch(params: DownloadParams): Promise<DownloadResult> {
  let browser: BrowserContext | null = null;
  let page: Page | null = null;
  let useCDP = false;

  try {
    // ========================================================================
    // PHASE 0: Read GEMINI_AFA_URL from TODOIT
    // ========================================================================

    console.error('[0/12] Reading GEMINI_AFA_URL from TODOIT...');
    const geminiAfaUrl = readGeminiAfaUrl(params.sourceName);
    console.error(`  ✓ URL: ${geminiAfaUrl}`);

    const format = params.format || 'txt';
    console.error(`  ✓ Format: ${format} (${getDownloadMenuText(format)})`);
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
    // PHASE 2: Navigate to Gemini chat
    // ========================================================================

    console.error('[2/11] Navigating to Gemini chat...');

    await page.goto(geminiAfaUrl, {
      timeout: CONFIG.navigationTimeout,
      waitUntil: 'domcontentloaded'
    });

    await page.waitForTimeout(CONFIG.pageLoadWait);
    console.error('  ✓ Navigation complete');
    console.error('');

    // ========================================================================
    // PHASE 3: Export to Google Docs (blind click)
    // ========================================================================

    console.error('[3/11] Exporting to Google Docs...');
    console.error('  → Clicking export menu button');

    try {
      // Click export menu button
      await page.click('button[data-test-id="export-menu-button"]', {
        timeout: CONFIG.actionTimeout
      });
      await page.waitForTimeout(2000);
      console.error('  ✓ Export menu opened');

      // Click export to docs button
      console.error('  → Clicking export to docs button');
      await page.click('button[data-test-id="export-to-docs-button"]', {
        timeout: CONFIG.actionTimeout
      });
      await page.waitForTimeout(CONFIG.exportWait);
      console.error('  ✓ Export to Docs initiated');

    } catch (error: any) {
      throw new Error(`Export failed: ${error.message}`);
    }

    console.error('');

    // ========================================================================
    // PHASE 4: Switch to Google Docs tab
    // ========================================================================

    console.error('[4/11] Switching to Google Docs tab...');

    await page.waitForTimeout(3000); // Wait for tab to open

    const allPages = browser.pages();
    console.error(`  → Found ${allPages.length} tabs`);

    if (allPages.length < 2) {
      await takeScreenshot(page, 'no-docs-tab');
      throw new Error('Google Docs tab did not open');
    }

    const docsPage = allPages[1]; // New tab
    await docsPage.bringToFront();
    console.error('  ✓ Switched to Google Docs tab');
    console.error('');

    // ========================================================================
    // PHASE 5: Rename document
    // ========================================================================

    console.error('[5/11] Renaming document...');
    console.error(`  → New name: ${params.sourceName}`);

    try {
      // Wait for document to load
      await docsPage.waitForTimeout(3000);

      // Option A: Click on title (try first)
      try {
        const titleInput = docsPage.locator('input.docs-title-input').first();

        if (await titleInput.isVisible({ timeout: 5000 })) {
          await titleInput.click();
          await docsPage.keyboard.press('Control+a');
          await titleInput.fill(params.sourceName);
          await docsPage.keyboard.press('Enter');
          console.error('  ✓ Document renamed (via title click)');
        } else {
          throw new Error('Title input not visible');
        }
      } catch (error: any) {
        // Option B: Use File menu
        console.error('  → Trying File menu method...');

        // Click File menu
        await docsPage.click('text=/^(File|Plik)$/i');
        await docsPage.waitForTimeout(1000);

        // Click Rename
        await docsPage.click('text=/^(Rename|Zmień nazwę)$/i');
        await docsPage.waitForTimeout(1000);

        // Type new name (old name should be selected)
        await docsPage.keyboard.type(params.sourceName);
        await docsPage.keyboard.press('Enter');

        console.error('  ✓ Document renamed (via File menu)');
      }

    } catch (error: any) {
      console.error(`  ⚠ Rename failed: ${error.message}`);
      console.error('  → Continuing without rename...');
    }

    console.error('');

    // ========================================================================
    // PHASE 6: Setup download directory
    // ========================================================================

    console.error('[6/11] Setting up download directory...');

    // Create dedicated subfolder for this download
    const downloadSubdir = path.join(CONFIG.downloadDir, params.sourceName);
    fs.mkdirSync(downloadSubdir, { recursive: true });
    console.error(`  → Download directory: ${downloadSubdir}`);

    // Configure CDP download behavior (if using CDP)
    if (useCDP && browser) {
      try {
        const cdpSession = await browser.newCDPSession(docsPage);
        await cdpSession.send('Browser.setDownloadBehavior', {
          behavior: 'allow',
          downloadPath: downloadSubdir
        });
        console.error(`  ✓ CDP download path configured`);
      } catch (cdpError: any) {
        console.error(`  ⚠ Could not configure CDP download path: ${cdpError.message}`);
      }
    }

    console.error('');

    // ========================================================================
    // PHASE 7: Download as TXT
    // ========================================================================

    console.error('[7/11] Downloading as TXT...');

    try {
      // Click File menu
      console.error('  → Opening File menu');
      await docsPage.click('text=/^(File|Plik)$/i', {
        timeout: CONFIG.actionTimeout
      });
      await docsPage.waitForTimeout(1500);

      // Click Download
      console.error('  → Clicking Download');
      await docsPage.click('text=/^(Download|Pobierz)$/i', {
        timeout: CONFIG.actionTimeout
      });
      await docsPage.waitForTimeout(1500);

      // Click selected format
      const menuText = getDownloadMenuText(format);
      console.error(`  → Selecting ${menuText} format`);
      await docsPage.click(`text=/${menuText}/i`, {
        timeout: CONFIG.actionTimeout
      });

      console.error(`  → Waiting ${CONFIG.downloadWait / 1000}s for download...`);
      await docsPage.waitForTimeout(CONFIG.downloadWait);

      console.error('  ✓ Download initiated');

    } catch (error: any) {
      throw new Error(`Download failed: ${error.message}`);
    }

    console.error('');

    // ========================================================================
    // PHASE 8: Find downloaded file
    // ========================================================================

    console.error('[8/12] Locating downloaded file...');

    const downloadedFile = findLatestDownload(downloadSubdir, format);

    if (!downloadedFile) {
      await takeScreenshot(docsPage, 'download-not-found');
      throw new Error('Downloaded file not found in /tmp/playwright-mcp-output');
    }

    console.error('');

    // ========================================================================
    // PHASE 9: Move file to target location
    // ========================================================================

    console.error('[9/12] Moving file to project structure...');

    const fileExtension = getFileExtension(format);
    const targetPath = path.join(
      CONFIG.projectRoot,
      'books',
      params.sourceName,
      'docs',
      `gemini-afa${fileExtension}`
    );

    console.error(`  → Target: ${targetPath}`);

    // Create directory if needed
    fs.mkdirSync(path.dirname(targetPath), { recursive: true });

    // Copy file (renameSync doesn't work across filesystems)
    fs.copyFileSync(downloadedFile, targetPath);

    // Remove original file
    fs.unlinkSync(downloadedFile);

    console.error('  ✓ File moved successfully');
    console.error('');

    // ========================================================================
    // PHASE 10: Verify file content
    // ========================================================================

    console.error('[10/12] Verifying file content...');

    const fileSize = fs.statSync(targetPath).size;
    console.error(`  → File size: ${fileSize} bytes`);

    // Read first 10 lines
    const content = fs.readFileSync(targetPath, 'utf-8');
    const lines = content.split('\n');
    const firstLines = lines.slice(0, 10).join('\n');

    console.error('  → First 10 lines:');
    console.error('  ' + '-'.repeat(60));
    firstLines.split('\n').forEach(line => {
      console.error('  ' + line.substring(0, 80));
    });
    console.error('  ' + '-'.repeat(60));

    console.error('');

    // ========================================================================
    // PHASE 11: Close Google Docs tabs
    // ========================================================================

    console.error('[11/12] Closing Google Docs tabs...');

    // Close the main Docs tab
    await docsPage.close();
    console.error('  ✓ Primary Docs tab closed');

    // Check for any remaining docs.google.com tabs and close them
    const remainingPages = browser.pages();
    let docsTabsClosed = 0;

    for (const p of remainingPages) {
      const url = p.url();
      if (url.includes('docs.google.com')) {
        await p.close();
        docsTabsClosed++;
        console.error(`  ✓ Closed extra Docs tab: ${url.substring(0, 50)}...`);
      }
    }

    if (docsTabsClosed > 0) {
      console.error(`  → Closed ${docsTabsClosed} additional Docs tab(s)`);
    }

    const finalPages = browser.pages();
    console.error(`  → Remaining tabs: ${finalPages.length}`);
    console.error('');

    // ========================================================================
    // PHASE 12: Return to Gemini tab
    // ========================================================================

    console.error('[12/12] Returning to Gemini tab...');

    await page.bringToFront();
    console.error('  ✓ Back to Gemini');
    console.error('');

    // ========================================================================
    // CLEANUP: Remove empty download directory
    // ========================================================================

    try {
      // Try to remove the download subdirectory (will only work if empty)
      fs.rmdirSync(downloadSubdir);
      console.error(`  ✓ Cleaned up empty directory: ${downloadSubdir}`);
    } catch (error) {
      // Directory not empty or other error - ignore
    }

    // ========================================================================
    // SUCCESS
    // ========================================================================

    // Don't close CDP browser (leave it running)
    if (!useCDP && browser) {
      await browser.close();
    }

    return {
      success: true,
      filePath: targetPath,
      fileSize: fileSize
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
    let errorType: DownloadResult['errorType'] = 'unknown';
    if (error.message.includes('URL') || error.message.includes('TODOIT')) {
      errorType = 'url_not_found';
    } else if (error.message.includes('Export')) {
      errorType = 'export_failed';
    } else if (error.message.includes('Download')) {
      errorType = 'download_failed';
    } else if (error.message.includes('Move') || error.message.includes('file')) {
      errorType = 'file_move_failed';
    } else if (error.message.includes('tab')) {
      errorType = 'tab_switch_failed';
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
    console.error('Usage: npx ts-node execute-deep-research-afa-dwn.ts <sourceName> [options]');
    console.error('');
    console.error('Arguments:');
    console.error('  <sourceName>          Book folder name (e.g., 0055_of_mice_and_men)');
    console.error('');
    console.error('Options:');
    console.error('  --headless=false      Run browser in visible mode');
    console.error('  --format=<format>     Download format (default: txt)');
    console.error('');
    console.error('Formats:');
    console.error('  txt      Plain text (.txt) - default');
    console.error('  pdf      PDF document (.pdf)');
    console.error('  docx     Microsoft Word (.docx)');
    console.error('  odt      OpenDocument format (.odt)');
    console.error('  rtf      Rich Text Format (.rtf)');
    console.error('  html     Web page (.zip)');
    console.error('  epub     EPUB publication (.epub)');
    console.error('  md       Markdown (.md)');
    console.error('');
    console.error('Environment variables:');
    console.error('  GEMINI_AFA_URL - URL to Gemini chat (for testing without TODOIT)');
    console.error('');
    console.error('Examples:');
    console.error('  npx ts-node execute-deep-research-afa-dwn.ts 0055_of_mice_and_men');
    console.error('  npx ts-node execute-deep-research-afa-dwn.ts 0055_of_mice_and_men --format=pdf');
    console.error('  npx ts-node execute-deep-research-afa-dwn.ts 0055_of_mice_and_men --headless=false --format=md');
    process.exit(1);
  }

  // Parse arguments
  const sourceName = args[0];
  let headless = true;
  let format: DownloadParams['format'] = 'txt';

  // Parse optional arguments
  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--headless=false' || arg === 'false') {
      headless = false;
    } else if (arg.startsWith('--format=')) {
      const formatValue = arg.split('=')[1] as DownloadParams['format'];
      if (['txt', 'pdf', 'docx', 'odt', 'rtf', 'html', 'epub', 'md'].includes(formatValue)) {
        format = formatValue;
      } else {
        console.error(`Invalid format: ${formatValue}`);
        process.exit(1);
      }
    }
  }

  const params: DownloadParams = {
    sourceName,
    headless,
    format
  };

  const result = await downloadAfaResearch(params);

  // Output JSON result to stdout
  console.log(JSON.stringify(result));

  // Exit with appropriate code
  process.exit(result.success ? 0 : 1);
}

// Run if executed directly
if (require.main === module) {
  main();
}
