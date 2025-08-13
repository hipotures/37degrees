#!/usr/bin/env python3

import sys
import os
import re
import asyncio
from pathlib import Path


def main():
    """
    37d-c4-todoit — Pobieranie obrazów z ChatGPT na TODOIT (MCP)
    
    Usage: python 37d-c4-todoit-runner.py BOOK_FOLDER-download
    """
    if len(sys.argv) != 2:
        print("❌ Błąd: Musisz podać BOOK_FOLDER-download")
        print("Przykład: python 37d-c4-todoit-runner.py 0022_old_man_and_the_sea-download")
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
    
    print("✅ Podstawowa walidacja zakończona pomyślnie")
    print("🔍 Ten skrypt wymaga uruchomienia przez Claude Code z integracją MCP")
    print(f"💡 Aby kontynuować, użyj Claude Code do wykonania kroków dla: {book_folder}")
    
    # Print the workflow steps that need to be executed
    print_workflow_steps(source_list, download_list, book_folder)


def print_workflow_steps(source_list, download_list, book_folder):
    """Print the workflow steps that need to be executed by Claude Code"""
    
    print(f"\n📋 Kroki do wykonania dla książki {book_folder}:")
    print("=" * 60)
    
    print("\n🔍 KROK 1: Sprawdzenie właściwości listy źródłowej")
    print(f"   - Sprawdź właściwość 'book_folder' w liście '{source_list}'")
    print(f"   - Sprawdź właściwość 'project_id' w liście '{source_list}'")
    
    print("\n📋 KROK 2: Pobranie następnego zadania")
    print(f"   - Pobierz następne oczekujące zadanie z listy '{download_list}'")
    print(f"   - Pobierz thread_id dla zadania z listy '{source_list}'")
    
    print("\n🌐 KROK 3: Nawigacja i pobieranie obrazów")
    print("   - Otwórz przeglądarkę i przejdź do URL czatu ChatGPT")
    print("   - Znajdź i kliknij przyciski pobierania obrazów")
    print("   - Nawiguj przez poprzednie odpowiedzi (Previous/Next)")
    
    print("\n📁 KROK 4: Przenoszenie plików")
    print("   - Znajdź pobrane pliki w /tmp/playwright-mcp-files/")
    print(f"   - Przenieś je do books/{book_folder}/generated/")
    print("   - Nazwij zgodnie z wzorcem: [BOOK_FOLDER]_scene_[NN].png")
    
    print("\n✅ KROK 5: Aktualizacja statusu")
    print("   - Oznacz zadanie jako 'completed' w liście pobierania")
    print("   - Zamknij przeglądarkę")
    
    print("\n" + "=" * 60)
    
    # Generate specific file naming pattern
    print(f"\n📄 Wzorzec nazw plików:")
    print(f"   Wzorzec: {book_folder}_scene_[NN].png")
    print(f"   Przykład: {book_folder}_scene_01.png")
    print(f"   Sufiksy: {book_folder}_scene_01_a.png, {book_folder}_scene_01_b.png, ...")


def move_and_rename_files(book_folder, scene_key):
    """Move and rename downloaded files - utility function"""
    
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
        download_dirs = [
            Path("/tmp/playwright-mcp-files/headless"),
            Path("/tmp/playwright-mcp-files"),
            Path("/tmp/playwright-mcp-output")
        ]
        
        downloaded_files = []
        for download_dir in download_dirs:
            if download_dir.exists():
                files = list(download_dir.glob("ChatGPT-Image*.png"))
                if not files:
                    files = list(download_dir.glob("*.png"))
                downloaded_files.extend(files)
                break
        
        if not downloaded_files:
            print(f"❌ Nie znaleziono pobranych plików w katalogach: {download_dirs}")
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


if __name__ == "__main__":
    main()