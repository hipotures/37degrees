const { chromium, devices } = require('playwright');

(async () => {
  const context = await chromium.launchPersistentContext('/home/xai/DEV/ms-playwright/mcp-chrome-profile-2', {
    channel: 'chrome',
    headless: false,
    args: [
      '--disable-blink-features=AutomationControlled',
      '--disable-web-security',
      '--no-sandbox'
    ],
    ...devices['Galaxy S24'],
    ignoreHTTPSErrors: true,
    userAgent: 'Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36',
    viewport: {
      height: 915,
      width: 412
    }
  });
  
  // Ukryj navigator.webdriver
  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
  });
  
  const page = await context.newPage();
  
  console.log('Navigating to Gemini...');
  await page.goto('https://gemini.google.com/app/0f61fddc68967fa6');
  
  console.log('Waiting for page to load...');
  await page.waitForLoadState('networkidle');
  
  try {
    console.log('Looking for side nav button...');
    await page.waitForSelector('[data-test-id="side-nav-menu-button"]', { timeout: 10000 });
    await page.locator('[data-test-id="side-nav-menu-button"]').click();
    
    console.log('Looking for text...');
    await page.waitForSelector('text=Pełny, oryginalny tytuł dzieł', { timeout: 10000 });
    await page.getByText('Pełny, oryginalny tytuł dzieł').click();
    
    console.log('Actions completed successfully!');
  } catch (error) {
    console.log('Error:', error.message);
    console.log('Taking screenshot...');
    await page.screenshot({ path: '/tmp/playwright-mcp-files/error.png' });
  }
  
  // Czekaj 5 sekund żeby zobaczyć wynik
  await page.waitForTimeout(5000);
  
  await context.close();
})();