#!/usr/bin/env python3
"""
37d-c4-todoit — Pobieranie obrazów z ChatGPT na TODOIT (MCP)
Designed to work within Claude Code environment with direct MCP access.
"""

import sys
import os
import re
import glob
import asyncio
from pathlib import Path


async def main():
    """
    37d-c4-todoit — Pobieranie obrazów z ChatGPT na TODOIT (MCP)
    
    Usage: python 37d-c4-todoit.py BOOK_FOLDER-download
    """
    if len(sys.argv) != 2:
        print("❌ Błąd: Musisz podać BOOK_FOLDER-download")
        print("Przykład: python 37d-c4-todoit.py 0022_old_man_and_the_sea-download")
        sys.exit(1)
    
    download_list_arg = sys.argv[1]
    
    if not download_list_arg.endswith("-download"):
        print("❌ Błąd: Argument musi kończyć się na '-download'")
        sys.exit(1)
    
    # Extract book folder
    book_folder = download_list_arg.replace("-download", "")
    download_list = download_list_arg
    source_list = book_folder
    
    print(f"📚 Przetwarzanie książki: {book_folder}")
    print(f"📋 Lista pobierania: {download_list}")
    print(f"📋 Lista źródłowa: {source_list}")
    
    # Check if book folder exists
    book_path = Path(f"/home/xai/DEV/37degrees/books/{book_folder}")
    if not book_path.exists():
        print(f"❌ Błąd: Folder książki nie istnieje: {book_path}")
        sys.exit(1)
    
    await download_images_workflow(source_list, download_list, book_folder)


async def download_images_workflow(source_list, download_list, book_folder):
    """Main workflow for downloading images"""
    
    try:
        # Step 0: Establish context
        print("🔍 Sprawdzanie właściwości listy źródłowej...")
        
        # Get book_folder property from source list
        book_folder_prop = await get_list_property(source_list, "book_folder")
        if not book_folder_prop:
            print(f"❌ Błąd: Brak właściwości 'book_folder' w liście {source_list}")
            return
            
        # Get project_id property from source list  
        project_id = await get_list_property(source_list, "project_id")
        if not project_id:
            print(f"❌ Błąd: Brak właściwości 'project_id' w liście {source_list}")
            print("💡 Musisz uruchomić 37d-a3 aby ustawić project_id")
            return
            
        print(f"✅ Znaleziono project_id: {project_id}")
        print(f"✅ Book folder: {book_folder_prop}")
        
        # Step 1: Get next pending task
        print(f"🔍 Pobieranie następnego zadania z listy {download_list}...")
        next_item = await get_next_pending(download_list)
        
        if not next_item:
            print("✅ Brak oczekujących zadań w liście pobierania")
            return
            
        scene_key = next_item["item_key"]
        print(f"🎬 Przetwarzanie sceny: {scene_key}")
        
        # Get thread_id for this scene from source list
        thread_id = await get_item_property(source_list, scene_key, "thread_id")
        if not thread_id:
            print(f"❌ Błąd: Brak thread_id dla sceny {scene_key}")
            await mark_item_failed(download_list, scene_key)
            return
            
        print(f"🔗 Thread ID: {thread_id}")
        
        # Construct chat URL
        chat_url = f"https://chatgpt.com/g/{project_id}/c/{thread_id}"
        print(f"🌐 URL czatu: {chat_url}")
        
        # Step 2: Navigate to chat and download images
        print("🌐 Otwieranie przeglądarki i nawigacja do czatu...")
        await navigate_to_chat(chat_url)
        
        print("📸 Pobieranie obrazów...")
        await download_chat_images()
        
        # Step 3: Move and rename files
        print("📁 Przenoszenie i nazywanie plików...")
        saved_files = await move_and_rename_files(book_folder, scene_key)
        
        if saved_files:
            print(f"✅ Zapisano pliki: {saved_files}")
            
            # Step 4: Mark task as completed
            print(f"✅ Oznaczanie zadania {scene_key} jako ukończone...")
            await mark_item_completed(download_list, scene_key)
        else:
            print("❌ Nie znaleziono pobranych plików")
            await mark_item_failed(download_list, scene_key)
        
    except Exception as e:
        print(f"❌ Błąd podczas przetwarzania: {e}")
        if 'scene_key' in locals():
            await mark_item_failed(download_list, scene_key)
    finally:
        # Step 5: Cleanup
        print("🧹 Zamykanie przeglądarki...")
        await close_browser()


async def get_list_property(list_key, property_key):
    """Get property value for a list using TODOIT MCP"""
    from mcp_client import MCPClient
    
    try:
        client = MCPClient()
        response = await client.call_tool("mcp__todoit__todo_get_list_property", {
            "list_key": list_key,
            "property_key": property_key
        })
        if response.get("success"):
            return response.get("property_value")
        return None
    except Exception as e:
        print(f"❌ Błąd pobierania właściwości listy: {e}")
        return None


async def get_item_property(list_key, item_key, property_key):
    """Get property value for an item using TODOIT MCP"""
    from mcp_client import MCPClient
    
    try:
        client = MCPClient()
        response = await client.call_tool("mcp__todoit__todo_get_item_property", {
            "list_key": list_key,
            "item_key": item_key, 
            "property_key": property_key
        })
        if response.get("success"):
            return response.get("property_value")
        return None
    except Exception as e:
        print(f"❌ Błąd pobierania właściwości elementu: {e}")
        return None


async def get_next_pending(list_key):
    """Get next pending item from a list using TODOIT MCP"""
    from mcp_client import MCPClient
    
    try:
        client = MCPClient()
        response = await client.call_tool("mcp__todoit__todo_get_next_pending", {
            "list_key": list_key
        })
        if response.get("success") and response.get("item"):
            return response.get("item")
        return None
    except Exception as e:
        print(f"❌ Błąd pobierania następnego zadania: {e}")
        return None


async def mark_item_completed(list_key, item_key):
    """Mark item as completed using TODOIT MCP"""
    from mcp_client import MCPClient
    
    try:
        client = MCPClient()
        response = await client.call_tool("mcp__todoit__todo_mark_completed", {
            "list_key": list_key,
            "item_key": item_key
        })
        return response.get("success", False)
    except Exception as e:
        print(f"❌ Błąd oznaczania jako ukończone: {e}")
        return False


async def mark_item_failed(list_key, item_key):
    """Mark item as failed using TODOIT MCP"""
    from mcp_client import MCPClient
    
    try:
        client = MCPClient()
        response = await client.call_tool("mcp__todoit__todo_update_item_status", {
            "list_key": list_key,
            "item_key": item_key,
            "status": "failed"
        })
        return response.get("success", False)
    except Exception as e:
        print(f"❌ Błąd oznaczania jako nieudane: {e}")
        return False


async def navigate_to_chat(chat_url):
    """Navigate to ChatGPT chat URL using Playwright MCP"""
    from mcp_client import MCPClient
    
    try:
        client = MCPClient()
        
        # Navigate to chat URL
        response = await client.call_tool("mcp__playwright-headless__browser_navigate", {
            "url": chat_url
        })
        
        # Take snapshot to verify page loaded
        await client.call_tool("mcp__playwright-headless__browser_snapshot", {})
        
        return response.get("success", False)
    except Exception as e:
        print(f"❌ Błąd nawigacji do czatu: {e}")
        return False


async def download_chat_images():
    """Download all images from the current ChatGPT chat"""
    from mcp_client import MCPClient
    
    try:
        client = MCPClient()
        
        # First, try to download images from current view
        await try_download_single_images(client)
        
        # Then try to navigate through multiple responses using Previous/Next
        await try_download_multiple_responses(client)
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd pobierania obrazów: {e}")
        return False


async def try_download_single_images(client):
    """Try to download images from single response"""
    try:
        # Look for download buttons and click them
        download_buttons = await client.call_tool("mcp__playwright-headless__browser_evaluate", {
            "function": """() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                return buttons.filter(b => 
                    b.textContent.includes('Download') || 
                    b.getAttribute('aria-label')?.includes('Download') ||
                    b.querySelector('[data-testid*="download"]')
                ).length;
            }"""
        })
        
        if download_buttons:
            # Click all download buttons
            await client.call_tool("mcp__playwright-headless__browser_evaluate", {
                "function": """() => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const downloadBtns = buttons.filter(b => 
                        b.textContent.includes('Download') || 
                        b.getAttribute('aria-label')?.includes('Download') ||
                        b.querySelector('[data-testid*="download"]')
                    );
                    downloadBtns.forEach(btn => btn.click());
                    return downloadBtns.length;
                }"""
            })
            
            # Wait a bit for downloads to start
            await asyncio.sleep(2)
            
    except Exception as e:
        print(f"⚠️  Błąd pobierania pojedynczych obrazów: {e}")


async def try_download_multiple_responses(client):
    """Try to navigate through multiple responses and download images"""
    try:
        # Keep trying to go to previous response and download
        while True:
            moved = await client.call_tool("mcp__playwright-headless__browser_evaluate", {
                "function": """() => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const prevBtn = buttons.find(b => 
                        (b.getAttribute('aria-label') || '').toLowerCase().includes('previous')
                    );
                    if (prevBtn && !prevBtn.disabled) {
                        prevBtn.click();
                        return true;
                    }
                    return false;
                }"""
            })
            
            if not moved:
                break
                
            # Wait for page to update
            await asyncio.sleep(1)
            
            # Try to download images from this response
            await try_download_single_images(client)
            
    except Exception as e:
        print(f"⚠️  Błąd nawigacji przez odpowiedzi: {e}")


async def move_and_rename_files(book_folder, scene_key):
    """Move and rename downloaded files"""
    try:
        # Extract scene number from scene_key (e.g., "scene_01" -> "01")
        scene_match = re.search(r'scene_(\d{2})', scene_key)
        if not scene_match:
            print(f"❌ Nie można wyodrębnić numeru sceny z: {scene_key}")
            return []
            
        scene_num = scene_match.group(1)
        base_name = f"{book_folder}_scene_{scene_num}"
        
        # Create destination directory
        dest_dir = Path(f"/home/xai/DEV/37degrees/books/{book_folder}/generated")
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Find downloaded files
        download_dir = Path("/tmp/playwright-mcp-files/headless")
        if not download_dir.exists():
            download_dir = Path("/tmp/playwright-mcp-files")
            
        downloaded_files = list(download_dir.glob("ChatGPT-Image*.png"))
        if not downloaded_files:
            # Try alternative patterns
            downloaded_files = list(download_dir.glob("*.png"))
            
        if not downloaded_files:
            print(f"❌ Nie znaleziono pobranych plików w {download_dir}")
            return []
            
        print(f"📁 Znaleziono {len(downloaded_files)} pobranych plików")
        
        saved_files = []
        for i, src_file in enumerate(sorted(downloaded_files, key=lambda f: f.stat().st_mtime)):
            # Generate target filename with suffix if needed
            if i == 0:
                target_name = f"{base_name}.png"
            else:
                suffix = chr(ord('a') + i - 1)  # a, b, c, ...
                target_name = f"{base_name}_{suffix}.png"
                
            target_path = dest_dir / target_name
            
            # Don't overwrite existing files
            counter = 0
            while target_path.exists():
                counter += 1
                if i == 0:
                    target_name = f"{base_name}_{chr(ord('a') + counter - 1)}.png"
                else:
                    suffix = chr(ord('a') + i - 1)
                    target_name = f"{base_name}_{suffix}_{counter}.png"
                target_path = dest_dir / target_name
            
            # Move file
            try:
                src_file.rename(target_path)
                saved_files.append(str(target_path))
                print(f"📁 Przeniesiono: {src_file.name} -> {target_name}")
            except Exception as e:
                print(f"❌ Błąd przenoszenia {src_file}: {e}")
                
        return saved_files
        
    except Exception as e:
        print(f"❌ Błąd przenoszenia plików: {e}")
        return []


async def close_browser():
    """Close the browser using Playwright MCP"""
    from mcp_client import MCPClient
    
    try:
        client = MCPClient()
        await client.call_tool("mcp__playwright-headless__browser_close", {})
        return True
    except Exception as e:
        print(f"❌ Błąd zamykania przeglądarki: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(main())