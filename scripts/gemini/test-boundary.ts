import { chromium } from 'playwright';

async function testWidth(width: number) {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const page = browser.contexts()[0].pages()[0];
  
  await page.setViewportSize({ width, height: 1080 });
  await page.waitForTimeout(2000);
  
  // Check if tabs exist (small viewport)
  const hasTabs = await page.locator('tab[name="Studio"]').or(page.locator('tab:has-text("Studio")')).count();
  
  // Check if heading exists (large viewport)
  const hasHeading = await page.locator('heading:has-text("Studio")').or(page.locator('h2:has-text("Studio")')).count();
  
  const format = hasTabs > 0 ? 'TABS' : (hasHeading > 0 ? 'PANELS' : 'UNKNOWN');
  
  console.log(`Width ${width}px: ${format} (tabs=${hasTabs}, headings=${hasHeading})`);
  
  process.exit(0);
}

const width = parseInt(process.argv[2] || '1049');
testWidth(width);
