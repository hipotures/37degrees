#!/usr/bin/env ts-node
/**
 * Take snapshot of currently open page in CDP browser
 *
 * Usage:
 *   npx ts-node scripts/gemini/snapshot-cdp-page.ts
 *
 * Output:
 *   /tmp/playwright-snapshot-TIMESTAMP.txt
 */

import { chromium } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';

async function takeSnapshot() {
  try {
    console.error('Connecting to CDP browser...');

    const browser = await chromium.connectOverCDP('http://localhost:9222');
    const contexts = browser.contexts();

    if (contexts.length === 0) {
      throw new Error('No browser contexts available');
    }

    const context = contexts[0];
    const pages = context.pages();

    if (pages.length === 0) {
      throw new Error('No pages open');
    }

    const page = pages[0];
    const url = page.url();

    console.error(`Connected to page: ${url}`);
    console.error('Taking snapshot...');

    // Generate timestamp filename
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');

    // Take both text and JSON snapshots
    console.error('  → Text snapshot...');
    const textSnapshot = await page.locator('body').ariaSnapshot();
    const textFilename = `/tmp/playwright-snapshot-${timestamp}.txt`;
    fs.writeFileSync(textFilename, textSnapshot, 'utf-8');

    console.error('  → JSON snapshot...');
    const jsonSnapshot = await page.accessibility.snapshot();
    const jsonFilename = `/tmp/playwright-snapshot-${timestamp}.json`;
    fs.writeFileSync(jsonFilename, JSON.stringify(jsonSnapshot, null, 2), 'utf-8');

    const textStats = fs.statSync(textFilename);
    const jsonStats = fs.statSync(jsonFilename);

    console.error(`✓ Snapshots saved:`);
    console.error(`  → Text: ${textFilename} (${(textStats.size / 1024).toFixed(2)} KB)`);
    console.error(`  → JSON: ${jsonFilename} (${(jsonStats.size / 1024).toFixed(2)} KB)`);

    console.log(jsonFilename);

    process.exit(0);

  } catch (error: any) {
    console.error(`✗ Error: ${error.message}`);
    process.exit(1);
  }
}

takeSnapshot().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
