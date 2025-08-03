#!/usr/bin/env python3
"""
Skrypt do naprawy struktury plików stylów - przeniesienie elementów wizualnych pod klucz visualElements
"""

import yaml
import os
from pathlib import Path

def fix_style_structure(style_data):
    """Naprawia strukturę stylu - przenosi elementy wizualne pod visualElements"""
    
    # Elementy które powinny być w visualElements
    visual_elements_keys = {
        'colorPalette', 'lineArt', 'lighting', 'rendering', 
        'perspective', 'mood', 'stylePrecedents'
    }
    
    # Elementy które zostają na głównym poziomie
    top_level_keys = {'styleName', 'description', 'aiPrompts'}
    
    # Sprawdź czy już ma visualElements
    if 'visualElements' in style_data:
        print("  - Styl już ma poprawną strukturę")
        return style_data
    
    # Nowa struktura
    fixed_style = {}
    visual_elements = {}
    
    # Przenieś elementy do odpowiednich sekcji
    for key, value in style_data.items():
        if key in top_level_keys:
            fixed_style[key] = value
        elif key in visual_elements_keys:
            visual_elements[key] = value
        else:
            # Nieznane klucze idą też do visualElements
            print(f"  - Przenoszę nieznany klucz '{key}' do visualElements")
            visual_elements[key] = value
    
    # Dodaj visualElements jeśli nie jest pusty
    if visual_elements:
        fixed_style['visualElements'] = visual_elements
    
    return fixed_style

def process_style_file(file_path):
    """Przetwarza pojedynczy plik stylu"""
    print(f"Przetwarzam: {file_path}")
    
    try:
        # Wczytaj plik
        with open(file_path, 'r', encoding='utf-8') as f:
            style_data = yaml.safe_load(f)
        
        # Napraw strukturę
        fixed_data = fix_style_structure(style_data)
        
        # Zapisz poprawiony plik
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(fixed_data, f, 
                     default_flow_style=False,
                     allow_unicode=True,
                     sort_keys=False,
                     width=120)
        
        print(f"  ✓ Poprawiono strukturę")
        return True
        
    except Exception as e:
        print(f"  ✗ Błąd: {e}")
        return False

def main():
    """Główna funkcja - przetwarza wszystkie style"""
    styles_dir = Path("config/prompt/graphics-styles")
    
    if not styles_dir.exists():
        print(f"Katalog stylów nie istnieje: {styles_dir}")
        return
    
    # Znajdź wszystkie pliki YAML
    style_files = list(styles_dir.glob("*.yaml"))
    
    if not style_files:
        print("Nie znaleziono plików stylów YAML")
        return
    
    print(f"Znaleziono {len(style_files)} plików stylów do przetworzenia\n")
    
    processed = 0
    errors = 0
    
    for style_file in sorted(style_files):
        if process_style_file(style_file):
            processed += 1
        else:
            errors += 1
        print()
    
    print(f"Ukończono!")
    print(f"Przetworzono: {processed} plików")
    print(f"Błędy: {errors} plików")

if __name__ == "__main__":
    main()