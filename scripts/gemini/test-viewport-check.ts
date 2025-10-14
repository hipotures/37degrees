import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const page = browser.contexts()[0].pages()[0];
  const viewport = page.viewportSize();
  const size = await page.evaluate(() => ({ 
    width: window.innerWidth, 
    height: window.innerHeight 
  }));
  console.log('Viewport:', viewport);
  console.log('Window:', size);
})();
