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
import * as fs from 'fs';
import * as path from 'path';


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

function findAudioItemsInSnapshot(node: any, foundItems: AudioItem[] = []): AudioItem[] {
  // Heuristic: Buttons with non-empty names in the accessibility tree are potential audio items.
  // The name is used as both the title for matching and the ref for later interaction.
  if (node.role === 'button' && node.name) {
    foundItems.push({
      title: node.name,
      ref: node.name,
    });
  }

  if (node.children) {
    for (const child of node.children) {
      findAudioItemsInSnapshot(child, foundItems);
    }
  }
  return foundItems;
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

async function collectAudioList(): Promise<any> {
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

    console.error('[2/4] Using active page (navigation is disabled)...');
    /*
    console.error(`  → URL: ${notebookUrl}`);

    await page.goto(notebookUrl, {
      waitUntil: 'load',
      timeout: CONFIG.navigationTimeout
    });

    await page.waitForTimeout(3000);
    */

    const isLoginRequired = await page.locator('text="Sign in"').isVisible().catch(() => false);
    if (isLoginRequired) {
      throw new Error('User not logged in to Google. Please log in manually first.');
    }

    console.error('  ✓ NotebookLM loaded');

    // ========================================================================
    // PHASE 2.1: Detect viewport mode (mobile vs desktop)
    // ========================================================================

    console.error('[2.1/4] Detecting viewport mode...');

    const windowWidth = await page.evaluate(() => window.innerWidth);
    const isMobileMode = windowWidth < 1050;
    const viewportMode = isMobileMode ? 'mobile' : 'desktop';

    console.error(`  → Window width: ${windowWidth}px`);
    console.error(`  → Mode: ${viewportMode} (${isMobileMode ? 'tabs layout' : 'panels layout'})`);

    // ========================================================================
    // PHASE 2.5: Deselect all sources for safety
    // ========================================================================

    console.error('[2.5/4] Deselecting all sources...');

    try {
      if (isMobileMode) {
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
        console.error('  → Desktop mode: Sources panel already visible');
      }

      await page.waitForTimeout(1000);
      const selectAllCheckbox = page.locator('input[type="checkbox"]').first();
      const isCheckboxVisible = await selectAllCheckbox.isVisible().catch(() => false);
      if (isCheckboxVisible) {
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
      console.error('  ⚠ Could not deselect sources (continuing anyway)');
    }

    // ========================================================================
    // PHASE 2.9: Navigate to Studio
    // ========================================================================

    console.error('[2.9/4] Navigating to Studio...');

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
        console.error(`  ⚠ Could not click Studio tab: ${tabError}`);
        throw new Error('Failed to navigate to Studio in mobile mode');
      }
    } else {
      console.error('  → Desktop mode: Studio panel already visible');
      await page.waitForTimeout(1000);
    }

    // ========================================================================
    // PHASE 3: Take JSON snapshot
    // ========================================================================

    console.error('[3/4] Taking JSON snapshot...');
    await page.waitForTimeout(3000);
    const jsonSnapshot = await page.accessibility.snapshot();
    console.error('  ✓ JSON snapshot captured');

    return jsonSnapshot;

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
    console.error('Usage: npx ts-node scripts/gemini/collect-audio-list.ts <workDir>');
    console.error('Example: npx ts-node scripts/gemini/collect-audio-list.ts /tmp/audio-batch-XYZ');
    process.exit(1);
  }

  const workDir = args[0];

  console.error(`\n=== NotebookLM Snapshotting ===`);
  console.error(`Taking snapshot of active tab...`);
  console.error(`Work Dir: ${workDir}`);
  console.error('');

  try {
    const snapshot = await collectAudioList();

    const outputFilename = `snapshot-studio.json`;
    const outputPath = path.join(workDir, outputFilename);

    fs.writeFileSync(outputPath, JSON.stringify(snapshot, null, 2), 'utf-8');

    console.log(outputPath);
    process.exit(0);
  } catch (error: any) {
    console.error(`✗ Error: ${error.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

export { collectAudioList, AudioItem, CollectionResult };
