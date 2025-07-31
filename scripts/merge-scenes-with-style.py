#!/usr/bin/env python3
"""
Skrypt do łączenia plików scen JSON ze stylem graficznym i specyfikacjami technicznymi.
Implementuje funkcjonalność polecenia 37d-apply-style-step2.
"""

import json
import os
import sys
import argparse
from pathlib import Path


def load_json_file(file_path):
    """Wczytuje plik JSON i zwraca dane."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Błąd JSON w pliku {file_path}: {e}")
        sys.exit(1)


def resolve_style_path(style_input, base_dir="/home/xai/DEV/37degrees"):
    """
    Rozwiązuje ścieżkę do pliku stylu.
    Jeśli to nazwa stylu, szuka w config/prompt/graphics-styles/
    Jeśli to ścieżka, używa bezpośrednio.
    """
    if os.path.isfile(style_input):
        return style_input
    
    # Sprawdź czy to nazwa stylu (bez .json)
    if not style_input.endswith('.json'):
        style_input += '.json'
    
    # Szukaj w standardowym katalogu stylów
    style_path = os.path.join(base_dir, 'config', 'prompt', 'graphics-styles', style_input)
    
    if os.path.isfile(style_path):
        return style_path
    
    print(f"Błąd: Nie znaleziono pliku stylu: {style_input}")
    print(f"Sprawdzono: {style_path}")
    sys.exit(1)


def resolve_tech_specs_path(tech_input, base_dir="/home/xai/DEV/37degrees"):
    """
    Rozwiązuje ścieżkę do pliku specyfikacji technicznych.
    """
    if os.path.isfile(tech_input):
        return tech_input
    
    # Sprawdź czy to standardowy plik
    if tech_input == 'technical-specifications' or tech_input == 'technical-specifications.json':
        tech_path = os.path.join(base_dir, 'config', 'prompt', 'technical-specifications.json')
        if os.path.isfile(tech_path):
            return tech_path
    
    print(f"Błąd: Nie znaleziono pliku specyfikacji technicznych: {tech_input}")
    sys.exit(1)


def merge_scene_with_style(scene_data, style_data, tech_specs_data):
    """
    Łączy dane sceny ze stylem i specyfikacjami technicznymi.
    
    Proces:
    1. Wyciąga sceneDescription z scene_data (bez pola 'title')
    2. Dodaje wszystkie pola z style_data (poza wykluczonymi metadata)
    3. Dodaje specyfikacje techniczne
    """
    
    # Wyciągnij sceneDescription bez title
    scene_desc = scene_data.get('sceneDescription', {}).copy()
    if 'title' in scene_desc:
        del scene_desc['title']
    
    # Przygotuj wynikowy JSON
    result = {
        'sceneDescription': scene_desc
    }
    
    # Dodaj wszystkie pola ze stylu POZA metadata
    excluded_style_fields = {'styleName', 'description', 'aiPrompts'}
    
    for key, value in style_data.items():
        if key not in excluded_style_fields:
            result[key] = value
    
    # Dodaj specyfikacje techniczne
    for key, value in tech_specs_data.items():
        result[key] = value
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description='Łączy pliki scen JSON ze stylem graficznym i specyfikacjami technicznymi',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  %(prog)s scenes/ output/ victorian-book-illustration-style technical-specifications
  %(prog)s /path/scenes/ /path/output/ /path/style.json /path/tech.json
  %(prog)s scenes/ output/ line-art-style technical-specifications.json
        """
    )
    
    parser.add_argument('scenes_dir', 
                        help='Katalog ze scenami JSON (np. prompts/scenes/narrative/)')
    parser.add_argument('output_dir', 
                        help='Katalog wyjściowy (zostanie utworzony jeśli nie istnieje)')
    parser.add_argument('style', 
                        help='Nazwa stylu (np. victorian-book-illustration-style) lub ścieżka do pliku JSON')
    parser.add_argument('tech_specs', 
                        help='Nazwa pliku tech specs (technical-specifications) lub ścieżka do pliku JSON')
    
    args = parser.parse_args()
    
    # Sprawdź katalog scen
    if not os.path.isdir(args.scenes_dir):
        print(f"Błąd: Katalog scen nie istnieje: {args.scenes_dir}")
        sys.exit(1)
    
    # Utwórz katalog wyjściowy
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Rozwiąż ścieżki do plików stylu i specyfikacji
    style_path = resolve_style_path(args.style)
    tech_specs_path = resolve_tech_specs_path(args.tech_specs)
    
    print(f"Używam stylu: {style_path}")
    print(f"Używam specyfikacji: {tech_specs_path}")
    
    # Wczytaj style i specyfikacje
    style_data = load_json_file(style_path)
    tech_specs_data = load_json_file(tech_specs_path)
    
    # Znajdź wszystkie pliki scen
    scene_files = []
    for filename in os.listdir(args.scenes_dir):
        if filename.endswith('.json') and filename.startswith('scene_'):
            scene_files.append(filename)
    
    scene_files.sort()  # Sortuj alfabetycznie
    
    if not scene_files:
        print(f"Błąd: Nie znaleziono plików scen w katalogu: {args.scenes_dir}")
        sys.exit(1)
    
    print(f"Znaleziono {len(scene_files)} plików scen")
    
    # Przetwórz każdy plik sceny
    processed_count = 0
    for scene_filename in scene_files:
        scene_path = os.path.join(args.scenes_dir, scene_filename)
        output_path = os.path.join(args.output_dir, scene_filename)
        
        try:
            # Wczytaj scenę
            scene_data = load_json_file(scene_path)
            
            # Połącz z stylem i specyfikacjami
            merged_data = merge_scene_with_style(scene_data, style_data, tech_specs_data)
            
            # Zapisz wynik
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Przetworzono: {scene_filename}")
            processed_count += 1
            
        except Exception as e:
            print(f"✗ Błąd przy przetwarzaniu {scene_filename}: {e}")
    
    print(f"\nUkończono! Przetworzono {processed_count} plików.")
    print(f"Wyniki zapisano w: {args.output_dir}")


if __name__ == '__main__':
    main()