#!/bin/bash

# Playwright codegen with preserved user profile
# Usage: ./browser.sh [url]

URL="${1:-https://chatgpt.com}"

# Kill any existing Chrome with this profile
pkill -f "chrome.*chrome-profile-codegen" 2>/dev/null

# Start Playwright codegen with anti-detection flags  
PLAYWRIGHT_BROWSERS_PATH=0 PLAYWRIGHT_CHROMIUM_LAUNCH_ARGS="--disable-blink-features=AutomationControlled --disable-dev-shm-usage --disable-web-security --no-first-run --no-sandbox --disable-extensions --disable-infobars --disable-notifications" npx playwright codegen \
  --browser chromium \
  --channel chrome \
  --user-data-dir /home/xai/DEV/ms-playwright/chrome-profile-codegen \
  --output /tmp/codegen-output.js \
  --device "Galaxy S24" \
  --target javascript \
  --user-agent "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36" \
  --ignore-https-errors \
  --viewport-size=412,915 \
  "$URL"
