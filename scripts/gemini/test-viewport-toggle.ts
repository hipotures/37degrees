#!/usr/bin/env ts-node
/**
 * Test script for viewport toggling between desktop and mobile modes
 *
 * Purpose: Verify that viewport resizing works in CDP browser and triggers
 * mobile/desktop layout changes in Gemini interface.
 *
 * IMPORTANT FINDINGS:
 * - Gemini mobile/desktop boundary: 960px (NOT 1050px like NotebookLM!)
 * - < 960px  = MOBILE mode (shows "3 dots" menu button)
 * - >= 960px = DESKTOP mode (no "3 dots" menu button)
 * - Gemini detects mode ONLY on page load, not on runtime resize
 * - To trigger mode change: setViewportSize() + page.reload()
 *
 * Usage:
 *   npx ts-node scripts/gemini/test-viewport-toggle.ts
 *
 * Prerequisites:
 *   - CDP browser running on localhost:9222 (run: scripts/9222.sh)
 *   - Browser should have Gemini open
 */

import { chromium, Page } from 'playwright';

// ============================================================================
// CONFIGURATION
// ============================================================================

const CDP_ENDPOINT = 'http://localhost:9222';

// CRITICAL: Gemini uses 960px boundary (NOT 1050px like NotebookLM!)
// - < 960px  = MOBILE mode (shows "3 dots" menu button)
// - >= 960px = DESKTOP mode (no "3 dots" menu button)
const VIEWPORT_BOUNDARY = 960; // px

const VIEWPORTS = {
  desktop: { width: 1920, height: 1080 },
  mobile: { width: 412, height: 915 }  // Samsung Galaxy S24 Ultra (same as scripts/9222-mobile.sh)
};

const WAIT_BETWEEN_CHANGES = 5000; // 5 seconds to observe UI changes

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

async function getCurrentViewportInfo(page: Page) {
  const info = await page.evaluate(() => ({
    innerWidth: window.innerWidth,
    innerHeight: window.innerHeight,
    outerWidth: window.outerWidth,
    outerHeight: window.outerHeight
  }));

  const mode = info.innerWidth < VIEWPORT_BOUNDARY ? 'MOBILE' : 'DESKTOP';

  return { ...info, mode };
}

async function setViewportMethod1_CDPWindowBounds(page: Page, mode: 'desktop' | 'mobile') {
  const viewport = VIEWPORTS[mode];
  console.log(`\n→ Method 1: CDP Browser.setWindowBounds (${viewport.width}x${viewport.height})...`);

  try {
    // Get CDP session
    const client = await page.context().newCDPSession(page);

    // Get current window ID
    const { windowId } = await client.send('Browser.getWindowForTarget');

    // Set window bounds
    await client.send('Browser.setWindowBounds', {
      windowId: windowId,
      bounds: {
        width: viewport.width,
        height: viewport.height
      }
    });

    await page.waitForTimeout(2000); // Wait for window to resize and UI to adjust

    const info = await getCurrentViewportInfo(page);
    console.log(`  ✓ Window bounds set: ${info.innerWidth}x${info.innerHeight}`);
    console.log(`  ✓ Detected mode: ${info.mode}`);

    await client.detach();
    return info;
  } catch (error: any) {
    console.log(`  ✗ Failed: ${error.message}`);
    throw error;
  }
}

async function setViewportMethod2_ViewportWithResizeEvent(page: Page, mode: 'desktop' | 'mobile') {
  const viewport = VIEWPORTS[mode];
  console.log(`\n→ Method 2: setViewportSize + resize event (${viewport.width}x${viewport.height})...`);

  await page.setViewportSize(viewport);

  // Trigger resize event to notify page
  await page.evaluate(() => {
    window.dispatchEvent(new Event('resize'));
  });

  await page.waitForTimeout(2000); // Wait for UI to react to resize

  const info = await getCurrentViewportInfo(page);
  console.log(`  ✓ Viewport set + resize event: ${info.innerWidth}x${info.innerHeight}`);
  console.log(`  ✓ Detected mode: ${info.mode}`);

  return info;
}

async function setViewportMethod3_CDPDeviceMetrics(page: Page, mode: 'desktop' | 'mobile') {
  const viewport = VIEWPORTS[mode];
  console.log(`\n→ Method 3: CDP Emulation.setDeviceMetricsOverride (${viewport.width}x${viewport.height})...`);

  try {
    const client = await page.context().newCDPSession(page);

    await client.send('Emulation.setDeviceMetricsOverride', {
      width: viewport.width,
      height: viewport.height,
      deviceScaleFactor: 1,
      mobile: mode === 'mobile'
    });

    await page.waitForTimeout(2000);

    const info = await getCurrentViewportInfo(page);
    console.log(`  ✓ Device metrics set: ${info.innerWidth}x${info.innerHeight}`);
    console.log(`  ✓ Detected mode: ${info.mode}`);

    await client.detach();
    return info;
  } catch (error: any) {
    console.log(`  ✗ Failed: ${error.message}`);
    throw error;
  }
}

// ============================================================================
// MAIN TEST
// ============================================================================

async function testViewportToggle() {
  console.log('========================================');
  console.log('Viewport Toggle Test');
  console.log('========================================');
  console.log(`CDP Endpoint: ${CDP_ENDPOINT}`);
  console.log(`Viewport Boundary: ${VIEWPORT_BOUNDARY}px`);
  console.log('');

  let browser;

  try {
    // ========================================================================
    // Connect to CDP browser
    // ========================================================================

    console.log('[1/6] Connecting to CDP browser...');
    browser = await chromium.connectOverCDP(CDP_ENDPOINT);
    console.log('  ✓ Connected');

    // ========================================================================
    // Get active page
    // ========================================================================

    console.log('\n[2/6] Getting active page...');
    const contexts = browser.contexts();

    if (contexts.length === 0) {
      throw new Error('No browser contexts found');
    }

    const pages = contexts[0].pages();

    if (pages.length === 0) {
      throw new Error('No pages found in browser');
    }

    const page = pages[0];
    const url = page.url();
    console.log(`  ✓ Active page: ${url}`);

    // ========================================================================
    // Show initial state
    // ========================================================================

    console.log('\n[3/6] Checking initial viewport...');
    const initialInfo = await getCurrentViewportInfo(page);
    console.log(`  → Current size: ${initialInfo.innerWidth}x${initialInfo.innerHeight}`);
    console.log(`  → Current mode: ${initialInfo.mode}`);

    // ========================================================================
    // Test Method 1: CDP Browser.setWindowBounds
    // ========================================================================

    console.log('\n========================================');
    console.log('TEST METHOD 1: CDP Browser.setWindowBounds');
    console.log('========================================');

    console.log('\n[4/12] Testing DESKTOP mode (Method 1)...');
    await setViewportMethod1_CDPWindowBounds(page, 'desktop');
    console.log(`  ⏸  Wait ${WAIT_BETWEEN_CHANGES/1000}s - observe browser UI (should show desktop layout)`);
    await page.waitForTimeout(WAIT_BETWEEN_CHANGES);

    console.log('\n[5/12] Testing MOBILE mode (Method 1)...');
    await setViewportMethod1_CDPWindowBounds(page, 'mobile');
    console.log(`  ⏸  Wait ${WAIT_BETWEEN_CHANGES/1000}s - observe browser UI (should show mobile layout with "3 dots" menu)`);
    await page.waitForTimeout(WAIT_BETWEEN_CHANGES);

    console.log('\n[6/12] Restoring DESKTOP mode (Method 1)...');
    await setViewportMethod1_CDPWindowBounds(page, 'desktop');
    console.log(`  ⏸  Wait ${WAIT_BETWEEN_CHANGES/1000}s - observe browser UI`);
    await page.waitForTimeout(WAIT_BETWEEN_CHANGES);

    // ========================================================================
    // Test Method 2: setViewportSize + resize event
    // ========================================================================

    console.log('\n========================================');
    console.log('TEST METHOD 2: setViewportSize + resize event');
    console.log('========================================');

    console.log('\n[7/12] Testing DESKTOP mode (Method 2)...');
    await setViewportMethod2_ViewportWithResizeEvent(page, 'desktop');
    console.log(`  ⏸  Wait ${WAIT_BETWEEN_CHANGES/1000}s - observe browser UI`);
    await page.waitForTimeout(WAIT_BETWEEN_CHANGES);

    console.log('\n[8/12] Testing MOBILE mode (Method 2)...');
    await setViewportMethod2_ViewportWithResizeEvent(page, 'mobile');
    console.log(`  ⏸  Wait ${WAIT_BETWEEN_CHANGES/1000}s - observe browser UI`);
    await page.waitForTimeout(WAIT_BETWEEN_CHANGES);

    console.log('\n[9/12] Restoring DESKTOP mode (Method 2)...');
    await setViewportMethod2_ViewportWithResizeEvent(page, 'desktop');
    console.log(`  ⏸  Wait ${WAIT_BETWEEN_CHANGES/1000}s - observe browser UI`);
    await page.waitForTimeout(WAIT_BETWEEN_CHANGES);

    // ========================================================================
    // Test Method 3: CDP Emulation.setDeviceMetricsOverride
    // ========================================================================

    console.log('\n========================================');
    console.log('TEST METHOD 3: CDP Emulation.setDeviceMetricsOverride');
    console.log('========================================');

    console.log('\n[10/12] Testing DESKTOP mode (Method 3)...');
    await setViewportMethod3_CDPDeviceMetrics(page, 'desktop');
    console.log(`  ⏸  Wait ${WAIT_BETWEEN_CHANGES/1000}s - observe browser UI`);
    await page.waitForTimeout(WAIT_BETWEEN_CHANGES);

    console.log('\n[11/12] Testing MOBILE mode (Method 3)...');
    await setViewportMethod3_CDPDeviceMetrics(page, 'mobile');
    console.log(`  ⏸  Wait ${WAIT_BETWEEN_CHANGES/1000}s - observe browser UI`);
    await page.waitForTimeout(WAIT_BETWEEN_CHANGES);

    console.log('\n[12/12] Restoring DESKTOP mode (Method 3)...');
    await setViewportMethod3_CDPDeviceMetrics(page, 'desktop');
    console.log(`  ⏸  Wait ${WAIT_BETWEEN_CHANGES/1000}s - observe browser UI`);
    await page.waitForTimeout(WAIT_BETWEEN_CHANGES);

    // ========================================================================
    // Test Method 4: Page reload after viewport change (CRITICAL TEST)
    // ========================================================================

    console.log('\n========================================');
    console.log('TEST METHOD 4: Page reload after viewport change');
    console.log('🔥 CRITICAL: This should trigger mobile mode detection');
    console.log('========================================');

    console.log('\n[13/15] Setting MOBILE viewport + reload...');
    console.log('→ Setting viewport to 1049px...');
    await page.setViewportSize({ width: 1049, height: 1080 });
    await page.waitForTimeout(500);

    console.log('→ Reloading page to trigger mode detection...');
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    const mobileInfo = await getCurrentViewportInfo(page);
    console.log(`  ✓ After reload: ${mobileInfo.innerWidth}x${mobileInfo.innerHeight}`);
    console.log(`  ✓ Detected mode: ${mobileInfo.mode}`);
    console.log(`  ⏸  Wait ${WAIT_BETWEEN_CHANGES/1000}s - CHECK BROWSER: Should show MOBILE layout with "3 dots" menu!`);
    await page.waitForTimeout(WAIT_BETWEEN_CHANGES);

    console.log('\n[14/15] Setting DESKTOP viewport + reload...');
    console.log('→ Setting viewport to 1920px...');
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForTimeout(500);

    console.log('→ Reloading page to trigger mode detection...');
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    const desktopInfo = await getCurrentViewportInfo(page);
    console.log(`  ✓ After reload: ${desktopInfo.innerWidth}x${desktopInfo.innerHeight}`);
    console.log(`  ✓ Detected mode: ${desktopInfo.mode}`);
    console.log(`  ⏸  Wait ${WAIT_BETWEEN_CHANGES/1000}s - CHECK BROWSER: Should show DESKTOP layout (no "3 dots")`);
    await page.waitForTimeout(WAIT_BETWEEN_CHANGES);

    console.log('\n[15/15] Final MOBILE test with reload...');
    console.log('→ Setting viewport to 1049px...');
    await page.setViewportSize({ width: 1049, height: 1080 });
    await page.waitForTimeout(500);

    console.log('→ Reloading page...');
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    const finalMobileInfo = await getCurrentViewportInfo(page);
    console.log(`  ✓ After reload: ${finalMobileInfo.innerWidth}x${finalMobileInfo.innerHeight}`);
    console.log(`  ✓ Detected mode: ${finalMobileInfo.mode}`);
    console.log(`  ⏸  Wait ${WAIT_BETWEEN_CHANGES/1000}s - CHECK BROWSER: Should show MOBILE layout again!`);
    await page.waitForTimeout(WAIT_BETWEEN_CHANGES);

    // ========================================================================
    // Final state
    // ========================================================================

    console.log('\n========================================');
    console.log('✅ All tests completed');
    console.log('========================================');

    const finalInfo = await getCurrentViewportInfo(page);
    console.log(`Final viewport: ${finalInfo.innerWidth}x${finalInfo.innerHeight} (${finalInfo.mode})`);
    console.log('');
    console.log('Methods tested:');
    console.log('  1. CDP Browser.setWindowBounds - changes physical window size');
    console.log('  2. setViewportSize + resize event - changes viewport + triggers resize');
    console.log('  3. CDP Emulation.setDeviceMetricsOverride - device emulation');
    console.log('');
    console.log('Configuration:');
    console.log(`  - Desktop viewport: ${VIEWPORTS.desktop.width}x${VIEWPORTS.desktop.height} (>= ${VIEWPORT_BOUNDARY}px)`);
    console.log(`  - Mobile viewport: ${VIEWPORTS.mobile.width}x${VIEWPORTS.mobile.height} (< ${VIEWPORT_BOUNDARY}px)`);
    console.log('');
    console.log('Expected behavior:');
    console.log('  - MOBILE mode: "3 dots" menu button visible, mobile layout');
    console.log('  - DESKTOP mode: No "3 dots" menu, desktop layout');
    console.log('');
    console.log('Which method worked?');
    console.log('  → Check browser UI during each test phase');
    console.log('  → Look for layout changes and "3 dots" menu appearance');
    console.log('');

  } catch (error: any) {
    console.error('\n✗ Test failed');
    console.error('Error:', error.message);
    console.error('');
    console.error('Troubleshooting:');
    console.error('  1. Make sure CDP browser is running: scripts/9222.sh');
    console.error('  2. Make sure browser has at least one page open');
    console.error('  3. Check that localhost:9222 is accessible');
    process.exit(1);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// ============================================================================
// RUN TEST
// ============================================================================

testViewportToggle();
