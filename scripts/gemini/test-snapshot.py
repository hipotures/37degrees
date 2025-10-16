import asyncio
import json
import yaml # Import the yaml library
from playwright.async_api import Playwright, async_playwright, TimeoutError

async def main():
    async with async_playwright() as p:
        print("Connecting to existing browser via CDP on http://localhost:9222...")
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")

        pages = browser.contexts[0].pages
        if not pages:
            print("No pages found in the connected browser context. Creating a new page.")
            page = await browser.contexts[0].new_page()
        else:
            page = pages[0] # Use the first available page
        print(f"Connected to page with URL: {page.url}")

        print("Taking accessibility snapshot...")
        snapshot = await page.accessibility.snapshot()

        # Save as JSON (for debugging/comparison)
        json_output_filename = "test_snapshot.json"
        with open(json_output_filename, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)
        print(f"Snapshot saved to {json_output_filename} (JSON format)")

        # Save as YAML (as requested by the user)
        yaml_output_filename = "test_snapshot.yaml"
        with open(yaml_output_filename, "w", encoding="utf-8") as f:
            yaml.dump(snapshot, f, allow_unicode=True, indent=2, sort_keys=False) # sort_keys=False to preserve order
        print(f"Snapshot saved to {yaml_output_filename} (YAML format)")

if __name__ == "__main__":
    asyncio.run(main())
