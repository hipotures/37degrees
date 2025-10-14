import { chromium } from 'playwright';

(async () => {
  try {
    const browser = await chromium.connectOverCDP('http://localhost:9222');
    const page = browser.contexts()[0].pages()[0];
    
    const size = await page.evaluate(() => ({ 
      width: window.innerWidth, 
      height: window.innerHeight 
    }));
    
    console.log(`Current window size: ${size.width} x ${size.height}`);
    
  } catch (error: any) {
    console.error('Error:', error.message);
  } finally {
    process.exit(0);
  }
})();
