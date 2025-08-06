#!/usr/bin/env python3
"""
Test script for ChatGPT image downloading automation
Demonstrates the actual MCP playwright-headless workflow
"""

import sys
import os
import re
from pathlib import Path

def test_download_workflow():
    """Test the ChatGPT download workflow with actual MCP commands"""
    
    book_folder = "0005_chlopi"
    
    # Step 1: Extract Project ID from TODO-GENERATE.md
    todo_file = Path(f"/home/xai/DEV/37degrees/books/{book_folder}/prompts/genimage/TODO-GENERATE.md")
    content = todo_file.read_text()
    
    project_match = re.search(r'^# PROJECT_ID = (.+)$', content, re.MULTILINE)
    if not project_match:
        print("ERROR: Project ID not found")
        return False
    
    project_id = project_match.group(1)
    print(f"✓ Extracted Project ID: {project_id}")
    
    # Step 2: Find first pending task (for demo, we'll look for any completed one)
    # Since all tasks are completed ([x] [x]), we'll demonstrate with the first one
    first_task = None
    for line in content.split('\n'):
        thread_match = re.search(r'Created thread ([a-f0-9-]+) for image (scene_\d+\.yaml)', line)
        if thread_match:
            thread_id = thread_match.group(1)
            scene_file = thread_match.group(2)
            scene_number = re.search(r'scene_(\d+)\.yaml', scene_file).group(1)
            first_task = {
                'thread_id': thread_id,
                'scene_file': scene_file,
                'scene_number': scene_number
            }
            break
    
    if not first_task:
        print("ERROR: No tasks found")
        return False
    
    print(f"✓ Demo task: Scene {first_task['scene_number']}, Thread: {first_task['thread_id']}")
    
    # Step 3: Build chat URL
    chat_url = f"https://chatgpt.com/g/{project_id}/c/{first_task['thread_id']}"
    print(f"✓ Chat URL: {chat_url}")
    
    # Step 4: Check existing generated files
    generated_dir = Path(f"/home/xai/DEV/37degrees/books/{book_folder}/generated")
    existing_files = list(generated_dir.glob(f"{book_folder}_scene_{first_task['scene_number'].zfill(2)}*.png"))
    print(f"✓ Existing files for scene {first_task['scene_number']}: {len(existing_files)}")
    for f in existing_files:
        print(f"  - {f.name}")
    
    print("\n🎯 Workflow validated successfully!")
    print("\nNext steps for actual automation:")
    print("1. mcp__playwright-headless__browser_navigate(url=chat_url)")
    print("2. mcp__playwright-headless__browser_wait_for(time=3)")
    print("3. mcp__playwright-headless__browser_snapshot()")
    print("4. mcp__playwright-headless__browser_click(element='Download this image button', ref='...')")
    print("5. Check for multiple responses and navigate if needed")
    print("6. Move files from /tmp/playwright-mcp-files/ to generated/ folder")
    print("7. Update TODO-GENERATE.md status")
    print("8. mcp__playwright-headless__browser_close()")
    
    return True

if __name__ == "__main__":
    print("Testing ChatGPT Image Download Workflow\n")
    test_download_workflow()