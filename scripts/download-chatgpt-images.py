#!/usr/bin/env python3
"""
Automatic ChatGPT Image Downloader for 37degrees project
Uses MCP playwright-headless to automate image downloading from ChatGPT conversations.

Usage: python scripts/download-chatgpt-images.py 0005_chlopi
"""

import sys
import os
import re
import time
import subprocess
from pathlib import Path

def run_mcp_command(command_func, *args, **kwargs):
    """Run an MCP playwright command (placeholder for actual MCP integration)"""
    print(f"MCP Command: {command_func}({args}, {kwargs})")
    return True

def extract_project_and_thread_info(book_folder):
    """Extract Project ID and pending Thread IDs from TODO-GENERATE.md"""
    todo_file = Path(f"/home/xai/DEV/37degrees/books/{book_folder}/prompts/genimage/TODO-GENERATE.md")
    
    if not todo_file.exists():
        print(f"ERROR: TODO-GENERATE.md not found for {book_folder}")
        return None, []
    
    content = todo_file.read_text()
    
    # Extract Project ID
    project_match = re.search(r'^# PROJECT_ID = (.+)$', content, re.MULTILINE)
    if not project_match:
        print("ERROR: Project ID not found in TODO-GENERATE.md")
        return None, []
    
    project_id = project_match.group(1)
    print(f"Project ID: {project_id}")
    
    # Find tasks ready to download: [x] [ ] (thread created, image not downloaded)
    pending_tasks = []
    for line_num, line in enumerate(content.split('\n'), 1):
        if re.match(r'^\s*\[x\] \[ \] Created thread', line):
            thread_match = re.search(r'Created thread ([a-f0-9-]+) for image (scene_\d+\.yaml)', line)
            if thread_match:
                thread_id = thread_match.group(1)
                scene_file = thread_match.group(2)
                scene_number = re.search(r'scene_(\d+)\.yaml', scene_file).group(1)
                pending_tasks.append({
                    'line_num': line_num,
                    'thread_id': thread_id,
                    'scene_file': scene_file,
                    'scene_number': scene_number,
                    'line': line
                })
    
    if not pending_tasks:
        print("INFO: No tasks pending download - all images already downloaded or no threads created")
        return project_id, []
    
    print(f"Found {len(pending_tasks)} tasks ready for download")
    return project_id, pending_tasks

def get_next_available_filename(book_folder, scene_number):
    """Get next available filename to avoid overwriting existing files"""
    base_name = f"{book_folder}_scene_{scene_number:02d}"
    generated_dir = Path(f"/home/xai/DEV/37degrees/books/{book_folder}/generated")
    
    # Check base name first
    base_file = generated_dir / f"{base_name}.png"
    if not base_file.exists():
        return str(base_file)
    
    # Try suffixes: _a, _b, _c, etc.
    for suffix in 'abcdefghijklmnopqrstuvwxyz':
        candidate = generated_dir / f"{base_name}_{suffix}.png"
        if not candidate.exists():
            return str(candidate)
    
    # If all suffixes are taken, use timestamp
    import time
    timestamp = int(time.time())
    return str(generated_dir / f"{base_name}_{timestamp}.png")

def download_images_from_chat(project_id, thread_id, book_folder, scene_number):
    """Download all images from a specific ChatGPT conversation"""
    chat_url = f"https://chatgpt.com/g/{project_id}/c/{thread_id}"
    print(f"Navigating to chat URL: {chat_url}")
    
    # Navigate directly to chat
    run_mcp_command("mcp__playwright-headless__browser_navigate", url=chat_url)
    
    # Wait for chat to load
    run_mcp_command("mcp__playwright-headless__browser_wait_for", time=3)
    
    # Take snapshot to see chat structure
    run_mcp_command("mcp__playwright-headless__browser_snapshot")
    
    # Download images - handle different chat scenarios:
    # 1. Single image - one prompt, one response, one "Download this image"
    # 2. Multiple responses - one prompt, X/Y responses, "Previous/Next response" buttons
    # 3. Multiple prompts - several user prompts in one chat
    
    downloaded_files = []
    
    # Strategy: Find all "Download this image" buttons and click them
    # For multiple responses, navigate through Previous/Next response buttons
    
    # First, download from current view
    download_result = run_mcp_command("mcp__playwright-headless__browser_click", 
                                    element="Download this image button", 
                                    ref="download-button-ref")
    
    # Check if there are Previous/Next response buttons indicating multiple responses
    has_multiple_responses = run_mcp_command("mcp__playwright-headless__browser_evaluate",
        function="""() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            const prevButton = buttons.find(btn => {
                const label = btn.getAttribute('aria-label') || '';
                return label.includes('Previous response');
            });
            return prevButton !== undefined;
        }""")
    
    if has_multiple_responses:
        print("Multiple responses detected - navigating to previous responses")
        # Navigate to first response and download
        run_mcp_command("mcp__playwright-headless__browser_evaluate",
            function="""() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                const prevButton = buttons.find(btn => {
                    const label = btn.getAttribute('aria-label') || '';
                    return label.includes('Previous response');
                });
                if (prevButton && !prevButton.disabled) {
                    prevButton.click();
                    return 'Moved to previous response';
                }
                return 'Already at first response';
            }""")
        
        # Download from first response
        run_mcp_command("mcp__playwright-headless__browser_click",
                       element="Download this image button",
                       ref="download-button-first-response")
    
    # Wait for downloads to complete
    run_mcp_command("mcp__playwright-headless__browser_wait_for", time=5)
    
    return ["ChatGPT-Image-1.png", "ChatGPT-Image-2.png"]  # Placeholder

def move_and_rename_files(downloaded_files, book_folder, scene_number):
    """Move downloaded files to proper location with correct naming"""
    moved_files = []
    
    # Check both possible download directories
    download_dirs = [
        "/tmp/playwright-mcp-files/headless/",
        "/tmp/playwright-mcp-files/browser/"
    ]
    
    for download_dir in download_dirs:
        download_path = Path(download_dir)
        if download_path.exists():
            # Find ChatGPT-Image*.png files, sorted by modification time (newest first)
            chatgpt_files = sorted(download_path.glob("ChatGPT-Image*.png"), 
                                 key=lambda x: x.stat().st_mtime, reverse=True)
            
            for i, source_file in enumerate(chatgpt_files[:len(downloaded_files)]):
                # Get next available filename
                target_file = get_next_available_filename(book_folder, int(scene_number))
                
                # Move file
                print(f"Moving {source_file} -> {target_file}")
                source_file.rename(target_file)
                moved_files.append(target_file)
    
    return moved_files

def update_todo_status(book_folder, thread_id):
    """Update TODO-GENERATE.md to mark task as completed"""
    todo_file = Path(f"/home/xai/DEV/37degrees/books/{book_folder}/prompts/genimage/TODO-GENERATE.md")
    content = todo_file.read_text()
    
    # Change [x] [ ] to [x] [x] for the specific thread
    updated_content = re.sub(
        rf'^\[x\] \[ \] Created thread {thread_id}',
        rf'[x] [x] Created thread {thread_id}',
        content,
        flags=re.MULTILINE
    )
    
    todo_file.write_text(updated_content)
    print(f"Updated TODO status for thread {thread_id}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/download-chatgpt-images.py BOOK_FOLDER")
        print("Example: python scripts/download-chatgpt-images.py 0005_chlopi")
        sys.exit(1)
    
    book_folder = sys.argv[1]
    print(f"Starting automatic ChatGPT image download for: {book_folder}")
    
    # Extract project and thread information
    project_id, pending_tasks = extract_project_and_thread_info(book_folder)
    
    if not project_id:
        sys.exit(1)
    
    if not pending_tasks:
        print("All images already downloaded!")
        sys.exit(0)
    
    # Process each pending task
    for task in pending_tasks:
        print(f"\nProcessing scene {task['scene_number']} (Thread: {task['thread_id']})")
        
        try:
            # Download images from chat
            downloaded_files = download_images_from_chat(
                project_id, task['thread_id'], book_folder, task['scene_number']
            )
            
            # Move and rename files
            moved_files = move_and_rename_files(downloaded_files, book_folder, task['scene_number'])
            
            # Update TODO status
            update_todo_status(book_folder, task['thread_id'])
            
            print(f"Successfully downloaded {len(moved_files)} images for scene {task['scene_number']}")
            
        except Exception as e:
            print(f"ERROR processing scene {task['scene_number']}: {e}")
            continue
    
    # Close browser
    run_mcp_command("mcp__playwright-headless__browser_close")
    print("\nDownload process completed!")

if __name__ == "__main__":
    main()