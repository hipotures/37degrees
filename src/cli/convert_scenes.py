#!/usr/bin/env python3
"""
CLI tool for converting scene files between JSON and YAML formats.
"""

import click
from pathlib import Path
from typing import Optional
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scene_file_handler import SceneFileHandlerFactory


def convert_file(input_path: Path, output_path: Optional[Path], from_format: str, to_format: str) -> None:
    """
    Convert a single scene file between formats.
    
    Args:
        input_path: Path to input file
        output_path: Path to output file (optional, auto-generated if not provided)
        from_format: Source format ('json' or 'yaml')
        to_format: Target format ('json' or 'yaml')
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Auto-generate output path if not provided
    if output_path is None:
        if to_format == 'json':
            output_path = input_path.with_suffix('.json')
        else:
            output_path = input_path.with_suffix('.yaml')
    
    # Load data from source format
    handler = SceneFileHandlerFactory.get_handler(format_type=from_format)
    data = handler.load(input_path)
    
    # Save data in target format
    handler = SceneFileHandlerFactory.get_handler(format_type=to_format)
    handler.save(data, output_path)
    
    click.echo(f"✓ Converted: {input_path} → {output_path}")


def convert_directory(dir_path: Path, from_format: str, to_format: str, recursive: bool = True) -> None:
    """
    Convert all scene files in a directory between formats.
    
    Args:
        dir_path: Directory path
        from_format: Source format ('json' or 'yaml')
        to_format: Target format ('json' or 'yaml')
        recursive: Whether to process subdirectories
    """
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")
    
    if not dir_path.is_dir():
        raise ValueError(f"Path is not a directory: {dir_path}")
    
    # Determine source file pattern
    if from_format == 'json':
        pattern = '**/*.json' if recursive else '*.json'
    else:
        pattern = '**/*.yaml' if recursive else '*.yaml'
        pattern_yml = '**/*.yml' if recursive else '*.yml'
    
    converted_count = 0
    
    # Find and convert files
    for file_path in dir_path.glob(pattern):
        if 'scene_' in file_path.name or file_path.name == 'scene-description-template.json':
            try:
                convert_file(file_path, None, from_format, to_format)
                converted_count += 1
            except Exception as e:
                click.echo(f"✗ Error converting {file_path}: {e}", err=True)
    
    # Also check .yml files if converting from yaml
    if from_format in ('yaml', 'yml'):
        for file_path in dir_path.glob(pattern_yml):
            if 'scene_' in file_path.name:
                try:
                    convert_file(file_path, None, from_format, to_format)
                    converted_count += 1
                except Exception as e:
                    click.echo(f"✗ Error converting {file_path}: {e}", err=True)
    
    click.echo(f"\nTotal files converted: {converted_count}")


@click.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--from', 'from_format', required=True, 
              type=click.Choice(['json', 'yaml', 'yml'], case_sensitive=False),
              help='Source format')
@click.option('--to', 'to_format', required=True,
              type=click.Choice(['json', 'yaml', 'yml'], case_sensitive=False),
              help='Target format')
@click.option('--output', '-o', type=click.Path(),
              help='Output path (for single file conversion)')
@click.option('--recursive/--no-recursive', '-r/-R', default=True,
              help='Process subdirectories (default: recursive)')
def convert_scenes(path: str, from_format: str, to_format: str, output: Optional[str], recursive: bool) -> None:
    """
    Convert scene files between JSON and YAML formats.
    
    Examples:
        python main.py convert-scenes scene.json --from json --to yaml
        python main.py convert-scenes books/0031_solaris/prompts --from json --to yaml
        python main.py convert-scenes . --from json --to yaml --recursive
    """
    path_obj = Path(path)
    
    # Normalize format names
    if from_format == 'yml':
        from_format = 'yaml'
    if to_format == 'yml':
        to_format = 'yaml'
    
    try:
        if path_obj.is_file():
            # Single file conversion
            output_path = Path(output) if output else None
            convert_file(path_obj, output_path, from_format, to_format)
        else:
            # Directory conversion
            if output:
                click.echo("Warning: --output option is ignored for directory conversion", err=True)
            convert_directory(path_obj, from_format, to_format, recursive)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    convert_scenes()