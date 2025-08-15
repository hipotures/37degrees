#!/usr/bin/env python3
"""
37d-set-list-2-download.py

Skrypt do przygotowania listy TODOIT do pobierania obrazów.
Ustawia status itemów na in_progress i właściwość image_downloaded na pending.

Usage:
    python scripts/37d-set-list-2-download.py <list_key>

Example:
    python scripts/37d-set-list-2-download.py 0034_to_kill_a_mockingbird
"""

import sys
import subprocess
import json
from typing import List, Dict, Any


def run_todoit_command(cmd: List[str]) -> Dict[str, Any]:
    """Uruchom komendę todoit i zwróć wynik jako JSON."""
    try:
        env = {"TODOIT_OUTPUT_FORMAT": "json"}
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            env={**subprocess.os.environ, **env},
            check=True
        )
        
        # TODOIT może zwracać multiple JSON objects - weź pierwszy
        output_lines = result.stdout.strip().split('\n')
        json_objects = []
        current_json = ""
        
        for line in output_lines:
            current_json += line + "\n"
            try:
                obj = json.loads(current_json)
                json_objects.append(obj)
                current_json = ""
            except json.JSONDecodeError:
                continue
        
        # Zwróć pierwszy obiekt JSON (powinien zawierać items)
        if json_objects:
            return json_objects[0]
        else:
            return json.loads(result.stdout)
            
    except subprocess.CalledProcessError as e:
        print(f"Błąd wywołania todoit: {e}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Błąd parsowania JSON: {e}")
        print(f"Raw output: {result.stdout[:200]}...")
        sys.exit(1)


def get_list_items(list_key: str) -> List[Dict[str, Any]]:
    """Pobierz wszystkie itemy z listy."""
    cmd = ["todoit", "list", "show", list_key]
    result = run_todoit_command(cmd)
    
    # TODOIT zwraca strukture z "data" zamiast "items"
    if "data" not in result:
        print(f"Błąd: brak danych dla listy {list_key}")
        sys.exit(1)
    
    # Konwertuj strukturę "data" na listę itemów z kluczami "item_key"
    items = []
    for item_data in result["data"]:
        # Każdy item w "data" ma klucz "Key" - zmień na "item_key"
        items.append({
            "item_key": item_data.get("Key", ""),
            "content": item_data.get("Task", ""),
            "status": item_data.get("Status", "")
        })
    
    return items


def update_item_status(list_key: str, item_key: str, status: str) -> None:
    """Aktualizuj status itemu."""
    cmd = ["todoit", "item", "status", list_key, item_key, "--status", status]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Status {item_key}: {status}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Błąd aktualizacji statusu {item_key}: {e.stderr}")


def set_item_property(list_key: str, item_key: str, property_key: str, property_value: str) -> None:
    """Ustaw właściwość itemu."""
    cmd = ["todoit", "item", "property", "set", list_key, item_key, property_key, property_value]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Property {item_key}.{property_key}: {property_value}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Błąd ustawiania właściwości {item_key}.{property_key}: {e.stderr}")


def main():
    """Główna funkcja skryptu."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/37d-set-list-2-download.py <list_key>")
        print("Example: python scripts/37d-set-list-2-download.py 0034_to_kill_a_mockingbird")
        sys.exit(1)
    
    list_key = sys.argv[1]
    print(f"🔧 Przygotowywanie listy {list_key} do pobierania obrazów...")
    
    # Pobierz wszystkie itemy z listy
    items = get_list_items(list_key)
    print(f"📋 Znaleziono {len(items)} itemów")
    
    # Przetwarzaj wszystkie itemy z listy (klucze mogą się dowolnie nazywać)
    target_items = items
    target_items.sort(key=lambda x: x.get("item_key", ""))
    print(f"🎯 Będzie przetworzonych {len(target_items)} itemów")
    
    # Aktualizuj każdy item
    for item in target_items:
        item_key = item.get("item_key", "")
        print(f"\n🔄 Przetwarzam {item_key}...")
        
        # 1. Ustaw status na in_progress
        update_item_status(list_key, item_key, "in_progress")
        
        # 2. Ustaw image_downloaded na pending
        set_item_property(list_key, item_key, "image_downloaded", "pending")
        
        # Uwaga: image_generated pozostaje bez zmian
    
    print(f"\n🎉 Zakończono przygotowanie listy {list_key}")
    print("📋 Wszystkie itemy mają teraz:")
    print("   - Status: in_progress")
    print("   - Property image_downloaded: pending")
    print("   - Property image_generated: bez zmian")


if __name__ == "__main__":
    main()