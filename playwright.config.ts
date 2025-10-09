import { defineConfig, devices } from '@playwright/test';
import path from 'path';

/**
 * Playwright configuration for 37degrees ChatGPT automation
 *
 * Key features:
 * - Persistent browser profile (maintains ChatGPT login)
 * - Chromium only (ChatGPT works best with Chrome)
 * - Screenshots and traces on failure
 */
export default defineConfig({
  testDir: './tests',

  // Timeout for each test
  timeout: 180000, // 3 minutes (ChatGPT can be slow)

  // Expect timeout for assertions
  expect: {
    timeout: 10000
  },

  // Fail fast on CI, run all tests locally
  fullyParallel: false,

  // Retry failed tests
  retries: 1,

  // Reporter
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report' }]
  ],

  // Global setup/teardown
  use: {
    // Base URL (not used for ChatGPT automation)
    // baseURL: 'https://chatgpt.com',

    // Collect trace on failure
    trace: 'retain-on-failure',

    // Screenshot on failure
    screenshot: 'only-on-failure',

    // Video on failure
    video: 'retain-on-failure',

    // Action timeout
    actionTimeout: 30000, // 30 seconds for each action

    // Navigation timeout
    navigationTimeout: 60000, // 1 minute for page loads
  },

  projects: [
    {
      name: 'chatgpt',
      use: {
        ...devices['Desktop Chrome'],

        // Persistent context for maintaining login
        // This is KEY for ChatGPT automation - keeps user logged in
        launchOptions: {
          args: [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
          ],
        },

        // Browser context options
        viewport: { width: 1280, height: 720 },

        // User agent (optional, makes automation less detectable)
        userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
      },
    },
  ],

  // Output directory for artifacts
  outputDir: 'test-results/',
});
