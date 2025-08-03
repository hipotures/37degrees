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

# Add src to path to import SceneFileHandler and config
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
from scene_file_handler import SceneFileHandlerFactory
from config import get_config


def load_scene_file(file_path, format_type=None):
    """Wczytuje plik sceny w odpowiednim formacie."""
    try:
        if format_type:
            # Użyj jawnie podanego formatu
            handler = SceneFileHandlerFactory.get_handler(format_type=format_type)
            return handler.load(Path(file_path))
        else:
            # Automatyczne wykrycie na podstawie rozszerzenia
            return SceneFileHandlerFactory.load_scene(Path(file_path))
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Błąd odczytu pliku {file_path}: {e}")
        sys.exit(1)


def resolve_style_path(style_input, base_dir="/home/xai/DEV/37degrees"):
    """
    Rozwiązuje ścieżkę do pliku stylu.
    Jeśli to nazwa stylu, szuka w config/prompt/graphics-styles/
    Jeśli to ścieżka, używa bezpośrednio.
    """
    if os.path.isfile(style_input):
        return style_input
    
    # Sprawdź czy to nazwa stylu (bez rozszerzenia)
    if not style_input.endswith('.yaml'):
        style_input += '.yaml'
    
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
    if tech_input == 'technical-specifications' or tech_input == 'technical-specifications.yaml':
        tech_path = os.path.join(base_dir, 'config', 'prompt', 'technical-specifications.yaml')
        if os.path.isfile(tech_path):
            return tech_path
    
    print(f"Błąd: Nie znaleziono pliku specyfikacji technicznych: {tech_input}")
    sys.exit(1)


def merge_scene_with_style(scene_data, style_data, tech_specs_data):
    """
    Łączy dane sceny ze stylem i specyfikacjami technicznymi.
    Tworzy poprawną strukturę 3-poziomową zgodnie z dokumentacją.
    
    Proces:
    1. Wyciąga sceneDescription z scene_data (bez pola 'title')
    2. Dodaje wszystkie pola stylu do sekcji visualElements
    3. Dodaje specyfikacje techniczne do sekcji technicalSpecifications
    """
    
    # Wyciągnij sceneDescription bez title
    scene_desc = scene_data.get('sceneDescription', {}).copy()
    if 'title' in scene_desc:
        del scene_desc['title']
    
    # Przygotuj wynikowy JSON z poprawną strukturą 3-poziomową
    result = {
        'sceneDescription': scene_desc,
        'visualElements': {},
        'technicalSpecifications': {}
    }
    
    # Dodaj elementy wizualne ze stylu
    excluded_style_fields = {'styleName', 'description', 'aiPrompts'}
    
    # Jeśli styl ma strukturę z visualElements, użyj jej
    if 'visualElements' in style_data:
        for key, value in style_data['visualElements'].items():
            result['visualElements'][key] = value
    else:
        # Stara struktura - wszystko poza metadata idzie do visualElements
        for key, value in style_data.items():
            if key not in excluded_style_fields:
                result['visualElements'][key] = value
    
    # Dodaj specyfikacje techniczne do technicalSpecifications
    # Jeśli tech_specs_data ma klucz 'technicalSpecifications', użyj jego zawartości
    if 'technicalSpecifications' in tech_specs_data:
        for key, value in tech_specs_data['technicalSpecifications'].items():
            result['technicalSpecifications'][key] = value
    else:
        # Jeśli nie ma klucza głównego, dodaj wszystko bezpośrednio
        for key, value in tech_specs_data.items():
            result['technicalSpecifications'][key] = value
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description='Łączy pliki scen YAML ze stylem graficznym i specyfikacjami technicznymi',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  %(prog)s scenes/ output/ victorian-book-illustration-style technical-specifications
  %(prog)s /path/scenes/ /path/output/ /path/style.yaml /path/tech.yaml
  %(prog)s scenes/ output/ line-art-style technical-specifications.yaml
        """
    )
    
    parser.add_argument('scenes_dir', 
                        help='Katalog ze scenami YAML (np. prompts/scenes/narrative/)')
    parser.add_argument('output_dir', 
                        help='Katalog wyjściowy (zostanie utworzony jeśli nie istnieje)')
    parser.add_argument('style', 
                        help='Nazwa stylu (np. victorian-book-illustration-style) lub ścieżka do pliku YAML')
    parser.add_argument('tech_specs', 
                        help='Nazwa pliku tech specs (technical-specifications) lub ścieżka do pliku YAML')
    
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
    
    # Wczytaj style i specyfikacje (teraz YAML)
    style_data = load_scene_file(style_path, format_type='yaml')
    tech_specs_data = load_scene_file(tech_specs_path, format_type='yaml')
    
    # Pobierz format z konfiguracji
    config = get_config()
    scene_format = config.get('scene_format', {}).get('format', 'json')
    
    # Znajdź wszystkie pliki scen w odpowiednim formacie
    scene_files = []
    file_extension = f'.{scene_format}'
    for filename in os.listdir(args.scenes_dir):
        if filename.endswith(file_extension) and filename.startswith('scene_'):
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
            scene_data = load_scene_file(scene_path)
            
            # Połącz z stylem i specyfikacjami
            merged_data = merge_scene_with_style(scene_data, style_data, tech_specs_data)
            
            # Zapisz wynik w formacie z konfiguracji
            output_path_with_ext = Path(output_path).with_suffix(f'.{scene_format}')
            SceneFileHandlerFactory.save_scene(merged_data, output_path_with_ext)
            
            print(f"✓ Przetworzono: {scene_filename}")
            processed_count += 1
            
        except Exception as e:
            print(f"✗ Błąd przy przetwarzaniu {scene_filename}: {e}")
    
    print(f"\nUkończono! Przetworzono {processed_count} plików.")
    print(f"Wyniki zapisano w: {args.output_dir}")


if __name__ == '__main__':
    main()