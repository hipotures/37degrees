#!/usr/bin/env python3
"""Apply text overlays to generated images"""

import os
import sys
import yaml
from pathlib import Path
from PIL import Image
from src.text_overlay import TextOverlay

def apply_overlays_to_book(book_path: str):
    """Apply text overlays to all generated images for a book"""
    book_dir = Path(book_path)
    config_file = book_dir / "book.yaml"
    
    if not config_file.exists():
        print(f"Error: {config_file} not found")
        return
    
    # Load book configuration
    with open(config_file, 'r', encoding='utf-8') as f:
        book_config = yaml.safe_load(f)
    
    # Initialize text overlay
    text_config = book_config.get('text_overlay', {})
    overlay = TextOverlay(text_config)
    
    # Process each slide
    generated_dir = book_dir / "generated"
    output_dir = book_dir / "with_text"
    output_dir.mkdir(exist_ok=True)
    
    slides = book_config.get('slides', [])
    
    for i, slide in enumerate(slides):
        # Get input image path
        slide_type = slide.get('type', f'slide_{i}')
        input_path = generated_dir / f"scene_{i:02d}_{slide_type}.png"
        
        if not input_path.exists():
            print(f"Warning: {input_path} not found, skipping...")
            continue
        
        # Load image
        image = Image.open(input_path)
        
        # Get text content
        text = slide.get('text', '')
        subtitle = slide.get('subtitle', '')
        
        # Apply text (combine with subtitle if present)
        if text or subtitle:
            if text and subtitle:
                combined_text = text + "\n\n" + subtitle
            else:
                combined_text = text or subtitle
            image = overlay.apply_text_overlay(image, combined_text)
        
        # Save output
        output_path = output_dir / f"scene_{i:02d}_{slide_type}_text.png"
        image.save(output_path, 'PNG', quality=95)
        print(f"Saved: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python apply_text_overlays.py <book_path>")
        sys.exit(1)
    
    book_path = sys.argv[1]
    apply_overlays_to_book(book_path)
    print("\nText overlay application complete!")