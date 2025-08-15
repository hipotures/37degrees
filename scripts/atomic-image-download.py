#!/usr/bin/env python3
"""
Atomic ChatGPT Image Downloader
Pobiera pojedynczy obrazek używając playwright-cdp

Usage: python atomic-image-download.py BOOK_FOLDER ITEM_KEY
Example: python atomic-image-download.py 0034_to_kill_a_mockingbird item_0005
"""

import sys
import os
import re
import subprocess
import json
import time
from pathlib import Path


def log(message):
    """Simple logging with timestamp"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def run_todoit_command(command_args):
    """Execute todoit CLI command directly"""
    cmd = ["todoit"] + command_args
    log(f"TODOIT CLI: {' '.join(cmd)}")
    
    try:
        env = os.environ.copy()
        env["TODOIT_OUTPUT_FORMAT"] = "json"
        
        result = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            timeout=30,
            env=env
        )
        
        if result.returncode != 0:
            log(f"TODOIT Error: {result.stderr}")
            return None
            
        output = result.stdout.strip()
        if not output:
            log("Empty output from TODOIT")
            return None
            
        try:
            return json.loads(output)
        except json.JSONDecodeError as e:
            log(f"Failed to parse TODOIT JSON: {e}")
            log(f"Raw output: {output}")
            return None
            
    except subprocess.TimeoutExpired:
        log("TODOIT call timed out")
        return None
    except Exception as e:
        log(f"TODOIT call failed: {e}")
        return None


def get_list_property(list_key, property_key):
    """Get property value from TODOIT list"""
    cmd = ["todoit", "list", "property", "get", list_key, property_key]
    log(f"TODOIT CLI: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            timeout=30
        )
        
        if result.returncode != 0:
            log(f"TODOIT Error: {result.stderr}")
            return None
            
        output = result.stdout.strip()
        if not output:
            log("Empty output from TODOIT")
            return None
        
        # Parse format: "property_key: property_value"
        if ":" in output:
            _, value = output.split(":", 1)
            return value.strip()
        else:
            log(f"Unexpected TODOIT output format: {output}")
            return None
            
    except subprocess.TimeoutExpired:
        log("TODOIT call timed out")
        return None
    except Exception as e:
        log(f"TODOIT call failed: {e}")
        return None


def get_item_properties(list_key, item_key):
    """Get all properties for specific item"""
    cmd = ["todoit", "item", "property", "list", list_key]
    log(f"TODOIT CLI: {' '.join(cmd)}")
    
    try:
        env = os.environ.copy()
        env["TODOIT_OUTPUT_FORMAT"] = "json"
        
        result = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            timeout=30,
            env=env
        )
        
        if result.returncode != 0:
            log(f"TODOIT Error: {result.stderr}")
            return {}
            
        output = result.stdout.strip()
        if not output:
            log("Empty output from TODOIT")
            return {}
        
        try:
            data = json.loads(output)
            # Find properties for our specific item
            if item_key in data:
                return data[item_key]
            else:
                log(f"Item {item_key} not found in properties")
                return {}
        except json.JSONDecodeError as e:
            log(f"Failed to parse TODOIT JSON: {e}")
            return {}
            
    except subprocess.TimeoutExpired:
        log("TODOIT call timed out")
        return {}
    except Exception as e:
        log(f"TODOIT call failed: {e}")
        return {}


def set_item_property(list_key, item_key, property_key, property_value):
    """Set property on TODOIT item"""
    result = run_todoit_command([
        "item", "property", "set", list_key, item_key, 
        property_key, property_value
    ])
    
    return result and result.get("success", False)


def update_item_status(list_key, item_key, status):
    """Update item status in TODOIT"""
    result = run_todoit_command([
        "item", "update", list_key, item_key, "--status", status
    ])
    
    return result and result.get("success", False)


def get_item_content(list_key, item_key):
    """Get item content to extract scene number"""
    cmd = ["todoit", "list", "show", list_key]
    log(f"TODOIT CLI: {' '.join(cmd)}")
    
    try:
        env = os.environ.copy()
        env["TODOIT_OUTPUT_FORMAT"] = "json"
        
        result = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            timeout=30,
            env=env
        )
        
        if result.returncode != 0:
            log(f"TODOIT Error: {result.stderr}")
            return ""
            
        output = result.stdout.strip()
        if not output:
            log("Empty output from TODOIT")
            return ""
        
        try:
            # Split by empty lines - TODOIT outputs separate JSON objects
            json_parts = output.split('\n\n')
            
            for i, json_part in enumerate(json_parts):
                json_part = json_part.strip()
                if not json_part:
                    continue
                    
                try:
                    data = json.loads(json_part)
                    log(f"Parsed JSON part {i}: {list(data.keys())}")
                    
                    if 'data' in data and isinstance(data['data'], list):
                        log(f"Found data array with {len(data['data'])} items")
                        # This is the items data
                        for item in data['data']:
                            if item.get('Key') == item_key:
                                task_content = item.get('Task', '')
                                log(f"Found item {item_key} with content: {task_content}")
                                return task_content
                except json.JSONDecodeError as e:
                    log(f"Failed to parse JSON part {i}: {e}")
                    log(f"Content: {json_part[:200]}...")
                    continue
            
            log(f"Item {item_key} not found in list {list_key}")
            return ""
            
        except json.JSONDecodeError as e:
            log(f"Failed to parse TODOIT JSON: {e}")
            return ""
            
    except subprocess.TimeoutExpired:
        log("TODOIT call timed out")
        return ""
    except Exception as e:
        log(f"TODOIT call failed: {e}")
        return ""


def run_claude_mcp_cdp(tool_name, **params):
    """Execute Claude MCP CDP tool via subprocess"""
    log(f"CDP MCP Call: {tool_name}({params})")
    
    # Build the MCP command with JSON output format
    cmd = [
        "claude", 
        "--dangerously-skip-permissions", 
        "-p",
        "--output-format", "json",
        "--mcp-config", "/home/xai/DEV/37degrees/.mcp.json-one_stop_workflow",
        "--allowedTools", tool_name
    ]
    
    # Create the prompt for the MCP tool
    prompt_parts = [f"Use {tool_name} with the following parameters:"]
    for key, value in params.items():
        prompt_parts.append(f"- {key}: {value}")
    
    prompt = "\n".join(prompt_parts)
    
    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=60
        )
        
        if result.returncode != 0:
            log(f"CDP MCP Error: {result.stderr}")
            return False
            
        # For CDP tools, we just check if it was successful
        output = result.stdout.strip()
        if "success" in output.lower() or "completed" in output.lower():
            return True
        else:
            log(f"CDP call may have failed: {output}")
            return False
            
    except subprocess.TimeoutExpired:
        log("CDP MCP call timed out")
        return False
    except Exception as e:
        log(f"CDP MCP call failed: {e}")
        return False


def open_new_tab_and_navigate(url):
    """Open new tab in CDP browser and navigate to URL"""
    log(f"Opening new tab and navigating to: {url}")
    
    # Open new tab
    result = run_claude_mcp_cdp("mcp__playwright-cdp__browser_tab_new", url=url)
    if not result:
        log("Failed to open new tab")
        return False
    
    # Wait for page to load
    time.sleep(5)
    
    return True


def download_images_from_current_page():
    """Download all images from current ChatGPT page"""
    log("Taking snapshot to analyze page content")
    
    # Take snapshot to see the page
    result = run_claude_mcp_cdp("mcp__playwright-cdp__browser_snapshot")
    if not result:
        log("Failed to take snapshot")
        return False
    
    log("Looking for download button and clicking it")
    
    # Try to find and click download button using a simple approach
    # We'll use a generic click approach since we know ChatGPT structure
    try:
        result = run_claude_mcp_cdp(
            "mcp__playwright-cdp__browser_click",
            element="Download this image button",
            ref="download_button"
        )
        
        if result:
            log("Successfully clicked download button")
            time.sleep(3)  # Wait for download to complete
            return True
        else:
            log("Failed to click download button")
            return False
            
    except Exception as e:
        log(f"Error during image download: {e}")
        return False


def find_and_move_downloaded_files(book_folder, scene_number):
    """Find downloaded files and move them to book directory"""
    log(f"Looking for downloaded files for scene {scene_number}")
    
    # Common download locations for CDP
    download_dirs = [
        "/tmp/playwright-mcp-output",
        "/tmp/playwright-mcp-files/cdp", 
        "/tmp/playwright-mcp-files",
        "/home/xai/Downloads"
    ]
    
    moved_files = []
    
    for download_dir in download_dirs:
        download_path = Path(download_dir)
        if not download_path.exists():
            log(f"Directory {download_dir} does not exist")
            continue
            
        # Look for any image files (not just ChatGPT ones)
        patterns = ["ChatGPT-Image*.png", "*.png", "image*.png", "*.jpg", "*.jpeg"]
        all_files = []
        
        for pattern in patterns:
            files = list(download_path.glob(pattern))
            all_files.extend(files)
        
        # Remove duplicates and sort by modification time (newest first)
        all_files = list(set(all_files))
        all_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        log(f"Found {len(all_files)} image files in {download_dir}")
        for f in all_files[:3]:  # Show first 3 files
            log(f"  - {f.name} (modified: {f.stat().st_mtime})")
        
        if all_files:
            dest_dir = Path(f"/home/xai/DEV/37degrees/books/{book_folder}/generated")
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Take only the most recent files (last 1 minute)
            import time
            current_time = time.time()
            recent_files = [f for f in all_files if (current_time - f.stat().st_mtime) < 60]
            
            log(f"Found {len(recent_files)} recent files (last 5 minutes)")
            
            for i, src_file in enumerate(recent_files):
                # Generate target filename
                if i == 0:
                    target_name = f"{book_folder}_scene_{scene_number:02d}.png"
                else:
                    suffix = chr(ord('a') + i - 1)  # a, b, c, etc.
                    target_name = f"{book_folder}_scene_{scene_number:02d}_{suffix}.png"
                
                target_path = dest_dir / target_name
                
                # Avoid overwriting existing files
                counter = 0
                while target_path.exists():
                    counter += 1
                    if i == 0:
                        target_name = f"{book_folder}_scene_{scene_number:02d}_{counter}.png"
                    else:
                        suffix = chr(ord('a') + i - 1)
                        target_name = f"{book_folder}_scene_{scene_number:02d}_{suffix}_{counter}.png"
                    target_path = dest_dir / target_name
                
                # Move the file
                try:
                    src_file.rename(target_path)
                    moved_files.append(str(target_path))
                    log(f"Moved: {src_file.name} -> {target_name}")
                except Exception as e:
                    log(f"Failed to move {src_file}: {e}")
    
    return moved_files


def close_current_tab():
    """Close the current tab in CDP browser"""
    log("Closing current tab")
    result = run_claude_mcp_cdp("mcp__playwright-cdp__browser_tab_close")
    if result:
        log("Tab closed successfully")
    else:
        log("Failed to close tab")


def main():
    """Main function"""
    if len(sys.argv) != 3:
        print("Usage: python atomic-image-download.py BOOK_FOLDER ITEM_KEY")
        print("Example: python atomic-image-download.py 0034_to_kill_a_mockingbird item_0005")
        sys.exit(1)
    
    book_folder = sys.argv[1]
    item_key = sys.argv[2]
    
    log(f"Starting atomic download for {book_folder}, item {item_key}")
    
    try:
        # Step 1: Get list properties
        log("Getting list properties...")
        project_id = get_list_property(book_folder, "project_id")
        if not project_id:
            log(f"ERROR: No project_id property found for list {book_folder}")
            sys.exit(1)
        
        log(f"Found project_id: {project_id}")
        
        # Step 2: Get item properties
        log("Getting item properties...")
        item_props = get_item_properties(book_folder, item_key)
        thread_id = item_props.get("thread_id")
        
        if not thread_id:
            log(f"ERROR: No thread_id property found for item {item_key}")
            sys.exit(1)
        
        log(f"Found thread_id: {thread_id}")
        
        # Check if already downloaded
        download_status = item_props.get("image_downloaded", "pending")
        if download_status == "completed":
            log(f"Item {item_key} already downloaded, skipping")
            sys.exit(0)
        
        # Step 3: Extract scene number from item content
        item_content = get_item_content(book_folder, item_key)
        scene_match = re.search(r'scene_(\d+)', item_content)
        if not scene_match:
            log(f"ERROR: Could not extract scene number from: {item_content}")
            sys.exit(1)
        
        scene_number = int(scene_match.group(1))
        log(f"Processing scene {scene_number}")
        
        # Step 4: Mark download as in_progress
        log("Marking download as in_progress...")
        if not set_item_property(book_folder, item_key, "image_downloaded", "in_progress"):
            log("WARNING: Failed to update status to in_progress")
        
        # Step 5: Build ChatGPT URL and navigate
        chat_url = f"https://chatgpt.com/g/{project_id}/c/{thread_id}"
        log(f"Navigating to: {chat_url}")
        
        if not open_new_tab_and_navigate(chat_url):
            log("ERROR: Failed to open ChatGPT page")
            set_item_property(book_folder, item_key, "image_downloaded", "failed")
            sys.exit(1)
        
        # Step 6: Download images
        log("Attempting to download images...")
        if not download_images_from_current_page():
            log("ERROR: Failed to download images")
            close_current_tab()
            set_item_property(book_folder, item_key, "image_downloaded", "failed")
            sys.exit(1)
        
        # Step 7: Move downloaded files
        log("Moving downloaded files...")
        moved_files = find_and_move_downloaded_files(book_folder, scene_number)
        
        if not moved_files:
            log("ERROR: No files were moved")
            close_current_tab()
            set_item_property(book_folder, item_key, "image_downloaded", "failed")
            sys.exit(1)
        
        log(f"Successfully moved {len(moved_files)} files:")
        for file_path in moved_files:
            log(f"  - {file_path}")
        
        # Step 8: Update TODOIT status
        log("Updating TODOIT status...")
        if not set_item_property(book_folder, item_key, "image_downloaded", "completed"):
            log("WARNING: Failed to update download status to completed")
        
        # Check if both generation and download are completed
        generate_status = item_props.get("image_generated", "pending")
        if generate_status == "completed":
            log("Both generation and download completed, marking item as completed")
            if not update_item_status(book_folder, item_key, "completed"):
                log("WARNING: Failed to update item status to completed")
        
        # Step 9: Clean up
        close_current_tab()
        
        log(f"✅ SUCCESS: Downloaded {len(moved_files)} images for {item_key}")
        sys.exit(0)
        
    except Exception as e:
        log(f"ERROR: Unexpected error: {e}")
        close_current_tab()
        set_item_property(book_folder, item_key, "image_downloaded", "failed")
        sys.exit(1)


if __name__ == "__main__":
    main()