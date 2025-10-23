#!/usr/bin/env ts-node
/**
 * Test script for Gemini chat rename functionality
 * Connects to existing CDP browser and tests rename flow
 */

import { chromium, BrowserContext, Page } from 'playwright';

async function testRename() {
  let browser: BrowserContext | null = null;
  let page: Page | null = null;

  try {
    console.log('Connecting to CDP browser on port 9222...');
    const cdpBrowser = await chromium.connectOverCDP('http://localhost:9222');
    const contexts = cdpBrowser.contexts();

    if (contexts.length === 0) {
      throw new Error('No browser contexts available');
    }

    browser = contexts[0];
    const pages = browser.pages();

    if (pages.length === 0) {
      throw new Error('No pages open');
    }

    page = pages[0];
    console.log(`✓ Connected to browser (${pages.length} pages)`);
    console.log(`  Current URL: ${page.url()}`);
    console.log('');

    // Test rename flow
    const testName = '0041_macbeth';

    console.log('[1/5] Looking for conversation actions menu button (3 dots)...');
    // Must be "Open menu for conversation actions" with more_vert icon, NOT "Main menu"
    const menuButton = page.locator('button[aria-label="Open menu for conversation actions"]').first();

    if (await menuButton.isVisible({ timeout: 5000 })) {
      console.log('  ✓ Menu button found');
      await menuButton.click();
      await page.waitForTimeout(1500);
      console.log('  ✓ Menu clicked');
    } else {
      throw new Error('Menu button not found');
    }

    console.log('');
    console.log('[2/5] Looking for Rename option...');
    const renameOption = page.locator('button', { hasText: /^Rename$/i }).first();

    if (await renameOption.isVisible({ timeout: 3000 })) {
      console.log('  ✓ Rename option found');
      await renameOption.click();
      await page.waitForTimeout(1500);
      console.log('  ✓ Rename option clicked');
    } else {
      throw new Error('Rename option not found');
    }

    console.log('');
    console.log('[3/5] Looking for text input...');
    const nameInput = page.getByRole('textbox', { name: /Enter new title/i });

    if (await nameInput.isVisible({ timeout: 3000 })) {
      console.log('  ✓ Text input found');
      const currentValue = await nameInput.inputValue();
      console.log(`  → Current value: "${currentValue}"`);
    } else {
      throw new Error('Text input not found');
    }

    console.log('');
    console.log('[4/5] Entering new name...');
    await nameInput.click();
    await nameInput.selectText();
    await nameInput.fill(testName);
    await page.waitForTimeout(500);
    console.log(`  ✓ Entered: "${testName}"`);

    console.log('');
    console.log('[5/5] Looking for Rename button...');
    const confirmButton = page.locator('button:has-text("Rename"):not([disabled])').first();

    if (await confirmButton.isVisible({ timeout: 3000 })) {
      console.log('  ✓ Rename button found (enabled)');
      await confirmButton.click();
      await page.waitForTimeout(1000);
      console.log('  ✓ Rename button clicked');
    } else {
      throw new Error('Rename button not enabled');
    }

    console.log('');
    console.log('========================================');
    console.log('✓ Rename test completed successfully!');
    console.log('========================================');

  } catch (error: any) {
    console.error('');
    console.error('✗ Test failed:', error.message);
    process.exit(1);
  }
}

testRename();
