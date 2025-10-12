#!/usr/bin/env ts-node
/**
 * Diagnostic script to inspect buttons in NotebookLM Studio panel
 */

import { chromium } from 'playwright';

async function diagnoseButtons() {
  console.log('Connecting to CDP browser...');

  const cdpBrowser = await chromium.connectOverCDP('http://localhost:9222');
  const contexts = cdpBrowser.contexts();
  const browser = contexts[0];
  const page = browser.pages()[0];

  console.log('\n=== Current URL ===');
  console.log(page.url());

  console.log('\n=== All buttons on page ===');
  const buttons = await page.locator('button').all();

  for (let i = 0; i < Math.min(buttons.length, 50); i++) {
    const button = buttons[i];

    const ariaLabel = await button.getAttribute('aria-label').catch(() => null);
    const text = await button.textContent().catch(() => null);
    const classes = await button.getAttribute('class').catch(() => null);
    const isVisible = await button.isVisible().catch(() => false);

    if (isVisible && (ariaLabel || text)) {
      console.log(`\n[Button ${i}]`);
      console.log(`  aria-label: ${ariaLabel}`);
      console.log(`  text: ${text?.substring(0, 50)}`);
      console.log(`  class: ${classes?.substring(0, 80)}`);
    }
  }

  console.log('\n=== Studio panel buttons (right side) ===');
  // Try to find buttons in the Studio section
  const studioButtons = await page.locator('[role="button"], button').all();

  for (const button of studioButtons.slice(0, 30)) {
    const ariaLabel = await button.getAttribute('aria-label').catch(() => null);
    const text = await button.textContent().catch(() => '');

    if (ariaLabel?.toLowerCase().includes('edit') ||
        ariaLabel?.toLowerCase().includes('customize') ||
        text?.toLowerCase().includes('edit') ||
        text?.toLowerCase().includes('customize') ||
        ariaLabel?.toLowerCase().includes('audio')) {

      console.log('\n=== POTENTIAL MATCH ===');
      console.log(`aria-label: ${ariaLabel}`);
      console.log(`text: ${text?.substring(0, 100)}`);
      console.log(`class: ${await button.getAttribute('class').catch(() => null)}`);

      // Check for SVG/icon inside
      const hasSvg = await button.locator('svg').count() > 0;
      console.log(`has SVG: ${hasSvg}`);
    }
  }

  console.log('\n=== Done ===');
}

diagnoseButtons().catch(console.error);
