"""37d-c4-todoit: Download images from ChatGPT using TODOIT MCP

This module is designed to be executed from Claude Code environment
where MCP functions are directly available.
"""

import os
import re
import glob
from pathlib import Path
import click
from typing import Optional, List
import time


def move_and_rename_files(book_folder: str, scene_key: str) -> List[str]:
    """Move and rename downloaded files
    
    Args:
        book_folder: Book folder name (e.g., '0014_jane_eyre')
        scene_key: Scene key (e.g., 'item_0015' or 'scene_15')
    
    Returns:
        List of moved file paths
    """
    # Extract scene number from scene_key
    # Handle both 'item_0015' and 'scene_15' formats
    if scene_key.startswith('item_'):
        scene_num = scene_key[5:].zfill(2)  # item_0015 -> 15 -> 15
    elif scene_key.startswith('scene_'):
        scene_num = scene_key[6:].zfill(2)  # scene_15 -> 15 -> 15
    else:
        # Try to extract number from anywhere in the string
        match = re.search(r'(\d+)', scene_key)
        if match:
            scene_num = match.group(1).zfill(2)
        else:
            click.echo(f"Invalid scene key format: {scene_key}")
            return []
    
    base_name = f"{book_folder}_scene_{scene_num}"
    
    # Create destination directory
    dest_dir = Path(f"/home/xai/DEV/37degrees/books/{book_folder}/generated")
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Find downloaded files in common locations
    download_patterns = [
        "/tmp/playwright-mcp-files/headless/ChatGPT-Image*.png",
        "/tmp/playwright-mcp-files/*/ChatGPT-Image*.png",
        "/tmp/playwright-mcp-files/ChatGPT-Image*.png",
        "/tmp/ChatGPT-Image*.png",
        "/home/*/Downloads/ChatGPT-Image*.png"
    ]
    
    downloaded_files = []
    for pattern in download_patterns:
        found_files = glob.glob(pattern)
        downloaded_files.extend(found_files)
    
    if not downloaded_files:
        click.echo("No downloaded files found. Searched patterns:")
        for pattern in download_patterns:
            click.echo(f"  - {pattern}")
        return []
    
    # Sort by modification time (newest first)
    downloaded_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    click.echo(f"Found {len(downloaded_files)} downloaded files")
    
    moved_files = []
    for i, src_file in enumerate(downloaded_files):
        # Generate unique filename
        if i == 0:
            dest_name = f"{base_name}.png"
        else:
            suffix = chr(ord('a') + i - 1)  # a, b, c, ...
            dest_name = f"{base_name}_{suffix}.png"
        
        dest_path = dest_dir / dest_name
        
        # Don't overwrite existing files - find next available suffix
        counter = 0
        while dest_path.exists():
            counter += 1
            if i == 0:
                suffix = chr(ord('a') + counter - 1)
                dest_name = f"{base_name}_{suffix}.png"
            else:
                suffix = chr(ord('a') + i - 1 + counter)
                dest_name = f"{base_name}_{suffix}.png"
            dest_path = dest_dir / dest_name
        
        try:
            # Move file
            os.rename(src_file, dest_path)
            moved_files.append(str(dest_path))
            click.echo(f"✅ Moved: {dest_path}")
        except Exception as e:
            click.echo(f"❌ Error moving {src_file}: {e}")
    
    return moved_files


@click.command()
@click.argument('download_list')
def download_todoit_cmd(download_list):
    """37d-c4-todoit: Download images from ChatGPT using TODOIT MCP
    
    This command is designed to be run from Claude Code environment.
    
    Args:
        download_list: Book folder with -download suffix (e.g., 0014_jane_eyre-download)
    """
    click.echo("⚠️  This command is designed to be executed from Claude Code environment")
    click.echo("    where MCP functions are directly available.")
    click.echo(f"📋 Download list: {download_list}")
    
    if not download_list.endswith("-download"):
        click.echo(f"❌ Error: Parameter must end with '-download', got: {download_list}")
        return
    
    book_folder = download_list[:-9]  # Remove "-download"
    click.echo(f"📁 Book folder: {book_folder}")
    
    # This would be the implementation when run from Claude Code:
    click.echo("\n🔧 To execute this command properly:")
    click.echo("   1. Run from Claude Code environment")
    click.echo("   2. Use: /37d-c4 0014_jane_eyre-download")
    click.echo("   3. Or integrate with Claude Code agents")


def download_todoit(download_list_param: str):
    """Main download function - intended for Claude Code environment"""
    return download_todoit_cmd.callback(download_list_param)


if __name__ == "__main__":
    download_todoit_cmd()