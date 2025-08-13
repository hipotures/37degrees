"""ChatGPT image download functionality for 37degrees using TODOIT MCP system (simplified)"""

import os
import shutil
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

console = Console()


def download_images(book_folder: str):
    """Download images from ChatGPT for a specific book using TODOIT MCP system"""
    
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
        
        # Get list properties using the actual MCP functions available in Claude Code
        # These should work directly since we're running in Claude Code environment
        book_folder_prop = mcp__todoit__todo_get_list_property(
            list_key=source_list,
            property_key="book_folder"
        )
        project_id_prop = mcp__todoit__todo_get_list_property(
            list_key=source_list, 
            property_key="project_id"
        )
        
        if not book_folder_prop.get('success') or not project_id_prop.get('success'):
            console.print(f"[red]Error: Missing required properties for list '{source_list}'[/red]")
            console.print("[yellow]Required: book_folder, project_id[/yellow]")
            return False
        
        book_folder_value = book_folder_prop.get('property_value')
        project_id = project_id_prop.get('property_value')
        
        console.print(f"[green]✓ Found book_folder: {book_folder_value}[/green]")
        console.print(f"[green]✓ Found project_id: {project_id}[/green]")
        
        # Process download tasks
        processed = 0
        errors = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            main_task = progress.add_task("Processing download tasks...", total=None)
            
            while True:
                # Get next pending task from download list
                progress.update(main_task, description="Getting next task...")
                
                try:
                    next_task = mcp__todoit__todo_get_next_pending(
                        list_key=download_list
                    )
                    
                    if not next_task.get('success') or not next_task.get('item'):
                        console.print("[yellow]No more pending tasks in download list[/yellow]")
                        break
                    
                    item = next_task['item']
                    scene_key = item['item_key']
                    
                    progress.update(main_task, description=f"Processing {scene_key}...")
                    console.print(f"\\n[cyan]Processing scene: {scene_key}[/cyan]")
                    
                    # Get thread_id from source list
                    try:
                        thread_id_prop = mcp__todoit__todo_get_item_property(
                            list_key=source_list,
                            item_key=scene_key,
                            property_key="thread_id"
                        )
                        
                        if not thread_id_prop.get('success') or not thread_id_prop.get('property_value'):
                            console.print(f"[red]✗ No thread_id found for {scene_key}[/red]")
                            # Mark as failed
                            mcp__todoit__todo_update_item_status(
                                list_key=download_list,
                                item_key=scene_key,
                                status="failed"
                            )
                            errors += 1
                            continue
                        
                        thread_id = thread_id_prop['property_value']
                        console.print(f"[green]✓ Found thread_id: {thread_id}[/green]")
                        
                        # Mark as in progress
                        mcp__todoit__todo_update_item_status(
                            list_key=download_list,
                            item_key=scene_key, 
                            status="in_progress"
                        )
                        
                        # Download images from ChatGPT
                        success = download_from_chatgpt(project_id, thread_id, scene_key, book_folder_value)
                        
                        if success:
                            # Mark as completed
                            mcp__todoit__todo_update_item_status(
                                list_key=download_list,
                                item_key=scene_key,
                                status="completed"
                            )
                            console.print(f"[green]✓ Completed: {scene_key}[/green]")
                            processed += 1
                        else:
                            # Mark as failed
                            mcp__todoit__todo_update_item_status(
                                list_key=download_list,
                                item_key=scene_key,
                                status="failed"
                            )
                            console.print(f"[red]✗ Failed: {scene_key}[/red]")
                            errors += 1
                            
                    except Exception as e:
                        console.print(f"[red]✗ Error processing {scene_key}: {e}[/red]")
                        errors += 1
                        
                        # Mark as failed
                        try:
                            mcp__todoit__todo_update_item_status(
                                list_key=download_list,
                                item_key=scene_key,
                                status="failed"
                            )
                        except:
                            pass
                
                except Exception as e:
                    console.print(f"[red]Error getting next task: {e}[/red]")
                    break
    
        # Summary
        console.print(f"\\n[bold]Download Summary:[/bold]")
        console.print(f"  [green]✅ Processed: {processed}[/green]")
        if errors > 0:
            console.print(f"  [red]❌ Errors: {errors}[/red]")
        console.print(f"  [dim]Total: {processed + errors}[/dim]")
        
        return processed > 0
        
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        return False


def download_from_chatgpt(project_id: str, thread_id: str, scene_key: str, book_folder: str):
    """Download images from a specific ChatGPT thread using Playwright MCP"""
    
    try:
        # Construct ChatGPT URL
        chat_url = f"https://chatgpt.com/g/{project_id}/c/{thread_id}"
        console.print(f"[yellow]Navigating to: {chat_url}[/yellow]")
        
        # Navigate to the chat using Playwright headless MCP (correct function name with dashes)
        mcp__playwright_headless__browser_navigate(url=chat_url)
        mcp__playwright_headless__browser_snapshot()
        
        # Wait for page to load
        mcp__playwright_headless__browser_wait_for(time=3)
        
        # Look for download buttons and download images
        downloaded_files = []
        
        try:
            console.print("[yellow]Looking for download buttons...[/yellow]")
            
            # Use JavaScript to find and click download buttons
            click_result = mcp__playwright_headless__browser_evaluate(
                function=\"\"\"() => {
                    // Find all buttons with download-related attributes or text
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const downloadButtons = buttons.filter(btn => {
                        const text = btn.textContent || '';
                        const ariaLabel = btn.getAttribute('aria-label') || '';
                        const title = btn.getAttribute('title') || '';
                        return text.toLowerCase().includes('download') || 
                               ariaLabel.toLowerCase().includes('download') ||
                               title.toLowerCase().includes('download') ||
                               btn.querySelector('[data-icon="download"]') ||
                               btn.querySelector('.download-icon');
                    });
                    
                    let clicked = 0;
                    downloadButtons.forEach(btn => {
                        try {
                            btn.click();
                            clicked++;
                        } catch(e) {
                            console.log('Failed to click button:', e);
                        }
                    });
                    
                    return { found: downloadButtons.length, clicked: clicked };
                }\"\"\"
            )
            
            if click_result and click_result.get('clicked', 0) > 0:
                console.print(f"[green]✓ Clicked {click_result['clicked']} download button(s)[/green]")
            else:
                console.print("[yellow]No download buttons found or clicked[/yellow]")
            
            # Also try to handle multiple responses by looking for Previous/Next buttons
            try:
                nav_result = mcp__playwright_headless__browser_evaluate(
                    function=\"\"\"() => {
                        const responses = [];
                        let moved = true;
                        let attempts = 0;
                        
                        // First, try to go to the first response
                        while (moved && attempts < 10) {
                            const buttons = Array.from(document.querySelectorAll('button'));
                            const prevBtn = buttons.find(b => {
                                const ariaLabel = b.getAttribute('aria-label') || '';
                                return ariaLabel.includes('Previous response') && !b.disabled;
                            });
                            
                            if (prevBtn && !prevBtn.disabled) {
                                prevBtn.click();
                                attempts++;
                                // Small delay
                                setTimeout(() => {}, 500);
                            } else {
                                moved = false;
                            }
                        }
                        
                        // Now go through each response
                        let hasNext = true;
                        attempts = 0;
                        
                        while (hasNext && attempts < 10) {
                            // Click download buttons in current response
                            const buttons = Array.from(document.querySelectorAll('button'));
                            const downloadButtons = buttons.filter(btn => {
                                const text = btn.textContent || '';
                                const ariaLabel = btn.getAttribute('aria-label') || '';
                                return text.toLowerCase().includes('download') || 
                                       ariaLabel.toLowerCase().includes('download');
                            });
                            
                            downloadButtons.forEach(btn => {
                                try {
                                    btn.click();
                                    responses.push('downloaded');
                                } catch(e) {}
                            });
                            
                            // Try to move to next response
                            const nextBtn = buttons.find(b => {
                                const ariaLabel = b.getAttribute('aria-label') || '';
                                return ariaLabel.includes('Next response') && !b.disabled;
                            });
                            
                            if (nextBtn && !nextBtn.disabled) {
                                nextBtn.click();
                                attempts++;
                                // Small delay
                                setTimeout(() => {}, 500);
                            } else {
                                hasNext = false;
                            }
                        }
                        
                        return { responses: responses.length, attempts: attempts };
                    }\"\"\"
                )
                
                if nav_result and nav_result.get('responses', 0) > 0:
                    console.print(f"[green]✓ Processed {nav_result['responses']} response(s)[/green]")
                    
            except Exception as e:
                console.print(f"[yellow]Error navigating responses: {e}[/yellow]")
            
            # Wait for downloads to complete
            mcp__playwright_headless__browser_wait_for(time=3)
            
            # Check for downloaded files
            downloads_dir = Path("/tmp/playwright-mcp-files/headless")
            if downloads_dir.exists():
                # Look for ChatGPT image files (most recent ones)
                chatgpt_images = sorted(
                    downloads_dir.glob("ChatGPT-Image*.png"),
                    key=lambda x: x.stat().st_mtime,
                    reverse=True
                )
                if chatgpt_images:
                    console.print(f"[green]✓ Found {len(chatgpt_images)} downloaded images[/green]")
                    downloaded_files = chatgpt_images
                else:
                    console.print("[yellow]No ChatGPT images found in downloads[/yellow]")
            
        except Exception as e:
            console.print(f"[yellow]Error during download process: {e}[/yellow]")
        
        # Close browser
        mcp__playwright_headless__browser_close()
        
        # Move and rename files if we found any
        if downloaded_files:
            return move_and_rename_files(downloaded_files, scene_key, book_folder)
        else:
            console.print(f"[yellow]No images downloaded for {scene_key}[/yellow]")
            return False
        
    except Exception as e:
        console.print(f"[red]Error downloading from ChatGPT: {e}[/red]")
        return False


def move_and_rename_files(downloaded_files: list, scene_key: str, book_folder: str):
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