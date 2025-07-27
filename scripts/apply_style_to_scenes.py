#!/usr/bin/env python3
"""
Universal style applicator for 37degrees project.
Merges scene descriptions with graphic styles and technical specifications.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any


class StyleApplicator:
    """Applies graphic styles to scene descriptions."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.tech_specs_path = base_dir / "config/prompt/technical-specifications.json"
        self.styles_dir = base_dir / "config/prompt/graphics-styles"
        
    def load_json(self, path: Path) -> Dict[str, Any]:
        """Load and parse JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            sys.exit(1)
    
    def save_json(self, data: Dict[str, Any], path: Path) -> None:
        """Save data as JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def find_book_dir(self, book_identifier: str) -> Optional[Path]:
        """Find book directory by number or name."""
        books_dir = self.base_dir / "books"
        
        # Try exact match first (e.g., "0036_treasure_island")
        if (books_dir / book_identifier).exists():
            return books_dir / book_identifier
        
        # Try to find by number or partial name
        for book_dir in books_dir.iterdir():
            if book_dir.is_dir():
                if book_identifier in book_dir.name:
                    return book_dir
        
        return None
    
    def merge_scene_with_style(self, scene_data: Dict[str, Any], 
                              style_data: Dict[str, Any], 
                              tech_specs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge scene, style, and technical specifications."""
        
        # Extract sceneDescription without title
        scene_desc = scene_data.get('sceneDescription', {}).copy()
        if 'title' in scene_desc:
            del scene_desc['title']
        
        # Fields to exclude from style
        style_excludes = {'styleName', 'description', 'aiPrompts'}
        
        # Filter style fields
        style_fields = {k: v for k, v in style_data.items() 
                       if k not in style_excludes}
        
        # Merge all components
        merged = {
            'sceneDescription': scene_desc,
            **style_fields,
            **tech_specs
        }
        
        return merged
    
    def process_scenes(self, book_identifier: str, scene_set: str, 
                      style_name: str, scene_number: Optional[int] = None) -> None:
        """Process scenes with given style."""
        
        # Find book directory
        book_dir = self.find_book_dir(book_identifier)
        if not book_dir:
            print(f"Error: Book '{book_identifier}' not found")
            sys.exit(1)
        
        print(f"Found book: {book_dir.name}")
        
        # Load style
        style_path = self.styles_dir / f"{style_name}.json"
        if not style_path.exists():
            print(f"Error: Style '{style_name}' not found")
            sys.exit(1)
        
        style_data = self.load_json(style_path)
        print(f"Loaded style: {style_name}")
        
        # Load technical specifications
        tech_specs = self.load_json(self.tech_specs_path)
        print("Loaded technical specifications")
        
        # Setup paths
        scenes_dir = book_dir / "prompts/scenes" / scene_set
        output_dir = book_dir / "prompts/genimage"
        
        if not scenes_dir.exists():
            print(f"Error: Scene set '{scene_set}' not found in {book_dir.name}")
            sys.exit(1)
        
        # Determine which scenes to process
        if scene_number:
            scene_files = [f"scene_{scene_number:02d}.json"]
        else:
            scene_files = sorted([f for f in os.listdir(scenes_dir) 
                                if f.startswith('scene_') and f.endswith('.json')])
        
        # Process scenes
        processed_count = 0
        for scene_file in scene_files:
            scene_path = scenes_dir / scene_file
            if not scene_path.exists():
                print(f"Warning: {scene_file} not found, skipping")
                continue
            
            # Load scene
            scene_data = self.load_json(scene_path)
            
            # Merge data
            merged = self.merge_scene_with_style(scene_data, style_data, tech_specs)
            
            # Save output
            output_path = output_dir / scene_file
            self.save_json(merged, output_path)
            
            processed_count += 1
            print(f"Processed: {scene_file}")
        
        print(f"\nCompleted! Processed {processed_count} scene(s)")
        print(f"Output directory: {output_dir}")


def main():
    """Main entry point."""
    
    # Parse arguments
    if len(sys.argv) < 4:
        print("Usage: python apply_style_to_scenes.py <book_identifier> <scene_set> <style_name> [scene_number]")
        print("\nExamples:")
        print("  python apply_style_to_scenes.py 0036_treasure_island emotional-journey victorian-book-illustration-style")
        print("  python apply_style_to_scenes.py 0036 narrative line-art-style 15")
        sys.exit(1)
    
    book_identifier = sys.argv[1]
    scene_set = sys.argv[2]
    style_name = sys.argv[3]
    scene_number = int(sys.argv[4]) if len(sys.argv) > 4 else None
    
    # Get base directory (script is in scripts/ folder)
    base_dir = Path(__file__).parent.parent
    
    # Create applicator and process
    applicator = StyleApplicator(base_dir)
    applicator.process_scenes(book_identifier, scene_set, style_name, scene_number)


if __name__ == "__main__":
    main()