#!/usr/bin/env ts-node
/**
 * Collect list of all audio from NotebookLM Studio panel
 *
 * Usage:
 *   npx ts-node scripts/gemini/collect-audio-list.ts <notebookUrl>
 *
 * Output (JSON to stdout):
 *   {
 *     "notebook_url": "https://...",
 *     "audio": [
 *       {"title": "Audio Title", "ref": "unique-button-ref", "timestamp": "2025-10-10"}
 *     ]
 *   }
 */

import { chromium, BrowserContext, Page } from 'playwright';
import * as net from 'net';

// ============================================================================
// TYPES
// ============================================================================

interface AudioItem {
  title: string;
  ref: string;
  timestamp?: string;
}

interface CollectionResult {
  success: boolean;
  notebook_url: string;
  audio: AudioItem[];
  error?: string;
}

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
  userDataDir: '/home/xai/DEV/ms-playwright/mcp-chrome-profile-gemini',
  navigationTimeout: 30000,
  actionTimeout: 15000,
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

async function collectAudioList(notebookUrl: string): Promise<CollectionResult> {
  let browser: BrowserContext | null = null;
  let page: Page | null = null;
  let useCDP = false;

  try {
    // ========================================================================
    // PHASE 1: Browser Setup
    // ========================================================================

    console.error('[1/4] Launching browser...');

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
        headless: true,
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

    console.error('[2/4] Navigating to NotebookLM...');
    console.error(`  → URL: ${notebookUrl}`);

    await page.goto(notebookUrl, {
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
    // PHASE 2.5: Switch to Studio tab (mobile only)
    // ========================================================================

    const isMobile = await page.evaluate(() => /Mobi|Android/i.test(navigator.userAgent));

    if (isMobile) {
      console.error('[2.5/4] Mobile detected - switching to Studio tab...');

      const studioTab = page.locator('[role="tab"]').filter({ hasText: 'Studio' }).first();

      const studioVisible = await studioTab.isVisible({ timeout: 2000 }).catch(() => false);

      if (studioVisible) {
        await studioTab.click();
        await page.waitForTimeout(1000);
        console.error('  ✓ Switched to Studio tab');
      } else {
        console.error('  ⚠ Studio tab not found (may be already selected)');
      }
    } else {
      console.error('[2.5/4] Desktop mode - Studio panel already visible');
    }

    // ========================================================================
    // PHASE 3: Take snapshot and parse audio list
    // ========================================================================

    console.error('[3/4] Collecting audio list...');

    // Wait for initial load
    await page.waitForTimeout(2000);

    // Scroll to bottom to trigger lazy loading of all audio items
    console.error('  → Scrolling to load all audio items...');
    let previousHeight = 0;
    let currentHeight = await page.evaluate(() => document.body.scrollHeight);
    let scrollAttempts = 0;
    const maxScrollAttempts = 20;

    while (previousHeight !== currentHeight && scrollAttempts < maxScrollAttempts) {
      previousHeight = currentHeight;
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(1000);
      currentHeight = await page.evaluate(() => document.body.scrollHeight);
      scrollAttempts++;
      console.error(`    → Scroll ${scrollAttempts}: height ${currentHeight}`);
    }

    console.error(`  ✓ Scrolling completed after ${scrollAttempts} attempts`);
    await page.waitForTimeout(2000);

    // Take accessibility snapshot
    const snapshot = await page.locator('body').ariaSnapshot();

    console.error('  → Parsing snapshot...');

    // Parse snapshot to find audio buttons
    // Audio appears as: button "Title Deep dive · 1 source · 4h ago Play More"
    const audioList: AudioItem[] = [];

    const lines = snapshot.split('\n');
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      // Look for audio button pattern
      // Pattern: - button "Title Deep dive · ... Play More"
      const buttonMatch = line.match(/^\s*- button "([^"]+)"/);
      if (buttonMatch) {
        const fullText = buttonMatch[1];

        // Audio buttons contain "Deep dive" and end with "Play More"
        if (fullText.includes('Deep dive') && fullText.includes('Play More')) {
          // Extract clean title by removing metadata
          // "Title Deep dive · 1 source · 4h ago Play More" -> "Title"
          const cleanTitle = fullText
            .replace(/\s+Deep dive.*$/, '')  // Remove from "Deep dive" to end
            .trim();

          audioList.push({
            title: cleanTitle,
            ref: `audio-${audioList.length}`,  // Sequential ref
          });
        }
      }
    }

    console.error(`  ✓ Found ${audioList.length} audio items`);

    // ========================================================================
    // PHASE 4: Return result
    // ========================================================================

    console.error('[4/4] Collection completed');

    return {
      success: true,
      notebook_url: notebookUrl,
      audio: audioList
    };

  } catch (error: any) {
    console.error(`✗ Error: ${error.message}`);

    return {
      success: false,
      notebook_url: notebookUrl,
      audio: [],
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

  if (args.length < 1) {
    console.error('Usage: npx ts-node scripts/gemini/collect-audio-list.ts <notebookUrl>');
    console.error('Example: npx ts-node scripts/gemini/collect-audio-list.ts https://notebooklm.google.com/notebook/xxx');
    process.exit(1);
  }

  const notebookUrl = args[0];

  console.error(`\n=== NotebookLM Audio Collection ===`);
  console.error(`Notebook: ${notebookUrl}`);
  console.error('');

  const result = await collectAudioList(notebookUrl);

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

export { collectAudioList, AudioItem, CollectionResult };
