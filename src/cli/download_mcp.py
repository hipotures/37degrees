"""ChatGPT image download functionality for 37degrees using TODOIT MCP system"""

import os
import shutil
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

console = Console()


def download_images_mcp(book_folder: str):
    """Download images from ChatGPT for a specific book using direct MCP calls"""
    
    # Parse book folder and validate format
    if not book_folder:
        console.print("[red]Error: BOOK_FOLDER is required[/red]")
        return False
    
    # Remove -download suffix if present
    if book_folder.endswith('-download'):
        book_folder = book_folder.replace('-download', '')
    
    # Validate format (should be like 0009_fahrenheit_451)
    if not book_folder or '_' not in book_folder:
        console.print(f"[red]Error: Invalid BOOK_FOLDER format: {book_folder}[/red]")
        console.print("[yellow]Expected format: NNNN_book_name (e.g., 0009_fahrenheit_451)[/yellow]")
        return False
    
    console.print(f"[cyan]Starting download for book: {book_folder}[/cyan]")
    
    # Define list names
    source_list = book_folder
    download_list = f"{book_folder}-download"
    
    try:
        console.print(f"[yellow]Getting properties for source list: {source_list}[/yellow]")
        
        # This function will be called within Claude Code environment where MCP functions are available
        # The actual implementation will be handled by the assistant using direct MCP function calls
        
        console.print("[blue]This function requires Claude Code environment with MCP functions[/blue]")
        console.print("[blue]Please run this through Claude Code assistant for full functionality[/blue]")
        
        return True
        
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        return False


def download_from_chatgpt_mcp(project_id: str, thread_id: str, scene_key: str, book_folder: str):
    """Download images from a specific ChatGPT thread using direct MCP calls"""
    
    try:
        # Construct ChatGPT URL
        chat_url = f"https://chatgpt.com/g/{project_id}/c/{thread_id}"
        console.print(f"[yellow]Navigating to: {chat_url}[/yellow]")
        
        # This will be handled by direct MCP function calls in Claude Code environment
        console.print("[blue]Browser automation via MCP would happen here[/blue]")
        
        return True
        
    except Exception as e:
        console.print(f"[red]Error downloading from ChatGPT: {e}[/red]")
        return False


def move_and_rename_files_mcp(downloaded_files: list, scene_key: str, book_folder: str):
    """Move and rename downloaded files with proper naming"""
    
    try:
        # Extract scene number from scene_key (e.g., "scene_01" -> "01")
        scene_num = scene_key.split('_')[-1]
        
        # Destination directory
        dest_dir = Path(f"/home/xai/DEV/37degrees/books/{book_folder}/generated")
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        
        for i, src_file in enumerate(sorted(downloaded_files)):
            # Base name: book_folder_scene_XX
            base_name = f"{book_folder}_scene_{scene_num}"
            
            # Add suffix for multiple files (_a, _b, _c, etc.)
            if i == 0:
                filename = f"{base_name}.png"
            else:
                suffix = chr(ord('a') + i)  # a, b, c, etc.
                filename = f"{base_name}_{suffix}.png"
            
            dest_path = dest_dir / filename
            
            # Don't overwrite existing files
            counter = 0
            while dest_path.exists():
                counter += 1
                if i == 0:
                    suffix = chr(ord('a') + counter - 1)
                    filename = f"{base_name}_{suffix}.png"
                else:
                    suffix = chr(ord('a') + i)
                    filename = f"{base_name}_{suffix}{counter}.png"
                dest_path = dest_dir / filename
            
            # Move the file
            try:
                shutil.move(str(src_file), str(dest_path))
                console.print(f"[green]✓ Saved: {dest_path}[/green]")
                saved_files.append(str(dest_path))
            except Exception as e:
                console.print(f"[red]✗ Failed to move {src_file}: {e}[/red]")
        
        if saved_files:
            console.print(f"[green]✓ Successfully saved {len(saved_files)} files[/green]")
            return True
        else:
            console.print("[red]✗ No files were saved[/red]")
            return False
        
    except Exception as e:
        console.print(f"[red]Error moving files: {e}[/red]")
        return False