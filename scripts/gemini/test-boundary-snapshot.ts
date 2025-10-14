import { chromium } from 'playwright';

async function testWidth(width: number) {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const page = browser.contexts()[0].pages()[0];
  
  await page.setViewportSize({ width, height: 1080 });
  await page.waitForTimeout(2000);
  
  // Get page content to check format
  const snapshot = await page.accessibility.snapshot();
  const yamlContent = JSON.stringify(snapshot);
  
  const hasTabs = yamlContent.includes('tab "Studio"') || yamlContent.includes('"role":"tab"') && yamlContent.includes('Studio');
  const hasHeading = yamlContent.includes('heading "Studio"') || (yamlContent.includes('"role":"heading"') && yamlContent.includes('Studio'));
  
  const format = hasTabs ? 'TABS (compact mode)' : (hasHeading ? 'PANELS (expanded mode)' : 'UNKNOWN');
  
  console.log(`Width ${width}px: ${format}`);
  
  process.exit(0);
}

const width = parseInt(process.argv[2] || '1049');
testWidth(width);
