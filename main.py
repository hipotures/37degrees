#!/usr/bin/env python3
"""
37 Degrees TikTok Video Generator
Main entry point with intuitive CLI interface
"""

import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from src.config import get_config, set_override

# Import CLI modules
from src.cli import collections, list_books, video, ai, research, site, convert_scenes

console = Console()


def display_banner():
    """Display application banner using rich"""
    console.print("""
[bold cyan]╔═══════════════════════════════════════╗
║      37 DEGREES - TikTok Generator    ║
║         Book Video Generator          ║
╚═══════════════════════════════════════╝[/bold cyan]
""")


def main():
    """Main function with subcommands"""
    parser = argparse.ArgumentParser(
        description="37 Degrees - Create engaging TikTok book review videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py collections              # List all collections
  python main.py list classics            # List books in classics collection
  python main.py list                     # List all books
  
  python main.py video 17                 # Generate video for book #17
  python main.py video little_prince      # Generate video by name
  python main.py video classics           # Generate videos for entire collection
  
  python main.py ai 17                    # Generate AI images for book #17
  python main.py ai classics              # Generate AI images for collection
  
  python main.py generate 17              # Generate AI images + video for book #17
  python main.py generate classics        # Generate AI images + videos for collection
  
  python main.py prompts 17               # Generate prompts for book #17
  python main.py prompts little_prince    # Generate prompts by name
  
  python main.py research 17              # Generate review.md for book #17
  python main.py research classics        # Generate reviews for collection
  
  python main.py site                     # Generate complete static site
  python main.py site 17                  # Generate page for book #17
  python main.py site classics            # Generate pages for collection
"""
    )
    
    # Global arguments
    parser.add_argument('--config', help='Path to config file (default: config/settings.yaml)')
    parser.add_argument('--set', action='append', help='Set config value (e.g., --set video.fps=60)')
    parser.add_argument('--no-banner', action='store_true', help='Skip banner display')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Collections command
    collections_parser = subparsers.add_parser('collections', help='List all collections')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List books')
    list_parser.add_argument('target', nargs='?', help='Collection name (optional)')
    
    # Video command
    video_parser = subparsers.add_parser('video', help='Generate video')
    video_parser.add_argument('target', help='Book ID, name, or collection')
    video_parser.add_argument('book_id', nargs='?', help='Book ID when target is collection')
    video_parser.add_argument('--only-render', action='store_true', help='Only render video from existing images')
    video_parser.add_argument('--template', help='Template name or path')
    
    # AI command
    ai_parser = subparsers.add_parser('ai', help='Generate AI images')
    ai_parser.add_argument('target', help='Book ID, name, or collection')
    ai_parser.add_argument('book_id', nargs='?', help='Book ID when target is collection')
    ai_parser.add_argument('--generator', help='Generator to use (invokeai, comfyui, mock)')
    
    # Generate command (AI + Video)
    generate_parser = subparsers.add_parser('generate', help='Generate AI images and video')
    generate_parser.add_argument('target', help='Book ID, name, or collection')
    generate_parser.add_argument('book_id', nargs='?', help='Book ID when target is collection')
    generate_parser.add_argument('--template', help='Template name or path')
    
    # Prompts command
    prompts_parser = subparsers.add_parser('prompts', help='Generate prompts from book.yaml')
    prompts_parser.add_argument('target', help='Book ID, name, or collection')
    prompts_parser.add_argument('book_id', nargs='?', help='Book ID when target is collection')
    
    # Research command
    research_parser = subparsers.add_parser('research', help='Generate review.md with AI research')
    research_parser.add_argument('target', help='Book ID, name, or collection')
    research_parser.add_argument('book_id', nargs='?', help='Book ID when target is collection')
    research_parser.add_argument('--provider', help='Research provider (perplexity, google, mock)')
    
    # Site command
    site_parser = subparsers.add_parser('site', help='Generate static HTML site')
    site_parser.add_argument('target', nargs='?', help='Book ID, name, or collection (optional)')
    site_parser.add_argument('book_id', nargs='?', help='Book ID when target is collection')
    
    # Convert scenes command
    convert_parser = subparsers.add_parser('convert-scenes', help='Convert scene files between JSON and YAML formats')
    convert_parser.add_argument('path', help='File or directory path')
    convert_parser.add_argument('--from', dest='from_format', required=True, 
                               choices=['json', 'yaml', 'yml'],
                               help='Source format')
    convert_parser.add_argument('--to', dest='to_format', required=True,
                               choices=['json', 'yaml', 'yml'],
                               help='Target format')
    convert_parser.add_argument('--output', '-o', help='Output path (for single file conversion)')
    convert_parser.add_argument('--recursive', '-r', action='store_true', default=True,
                               help='Process subdirectories (default: recursive)')
    convert_parser.add_argument('--no-recursive', '-R', action='store_false', dest='recursive',
                               help='Do not process subdirectories')
    
    args = parser.parse_args()
    
    # Load config with custom path if provided
    if args.config:
        from pathlib import Path
        from src.config import Config
        import src.config
        src.config._config = Config(Path(args.config))
    
    # Apply config overrides from CLI
    if args.set:
        for override in args.set:
            if '=' in override:
                key, value = override.split('=', 1)
                # Try to parse value as number or boolean
                try:
                    if value.lower() in ['true', 'false']:
                        value = value.lower() == 'true'
                    elif '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    pass  # Keep as string
                set_override(key, value)
                console.print(f"[green]Config override: {key} = {value}[/green]")
    
    # Display banner unless disabled
    if not hasattr(args, 'no_banner') or not args.no_banner:
        display_banner()
    
    # Handle commands
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'collections':
            collections.list_collections()
            
        elif args.command == 'list':
            if args.target:
                list_books.list_collection_books(args.target)
            else:
                list_books.list_all_books()
                
        elif args.command == 'video':
            video.generate_video(args.target, args.book_id, args.only_render, args.template)
            
        elif args.command == 'ai':
            ai.generate_images(args.target, args.book_id, args.generator)
            
        elif args.command == 'generate':
            # Generate prompts, AI images, then video
            from src.cli.utils import get_book_path
            from pathlib import Path
            import subprocess
            
            # Get book path
            if args.book_id:
                # Collection with book ID
                from src.cli.utils import resolve_target
                _, collection_name = resolve_target(args.target)
                collection_file = Path(f"collections/{collection_name}.yaml")
                if collection_file.exists():
                    import yaml
                    with open(collection_file, 'r', encoding='utf-8') as f:
                        collection_data = yaml.safe_load(f)
                    for book in collection_data.get('books', []):
                        if str(book.get('order', '')) == args.book_id:
                            book_path = Path(book['path'])
                            break
                    else:
                        book_path = None
                else:
                    book_path = None
            else:
                book_path = get_book_path(args.target)
            
            if book_path:
                # Step 1: Generate prompts
                console.print("[yellow]Step 1: Generating prompts...[/yellow]")
                result = subprocess.run([
                    sys.executable, "src/prompt_builder.py", str(book_path)
                ], capture_output=True, text=True)
                if result.returncode != 0:
                    console.print(f"[red]Prompt generation failed: {result.stderr}[/red]")
                else:
                    console.print("[green]✓ Prompts generated[/green]")
                
                # Step 2: Generate AI images
                console.print("[yellow]Step 2: Generating AI images...[/yellow]")
                ai.generate_images(args.target, args.book_id)
                
                # Step 3: Generate video
                console.print("[yellow]Step 3: Generating video...[/yellow]")
                video.generate_video(args.target, args.book_id, False, args.template)
            else:
                console.print(f"[red]Book '{args.target}' not found![/red]")
                
        elif args.command == 'prompts':
            # Generate prompts only
            from src.cli.utils import get_book_path
            from pathlib import Path
            import subprocess
            
            # Get book path (same logic as generate)
            if args.book_id:
                from src.cli.utils import resolve_target
                _, collection_name = resolve_target(args.target)
                collection_file = Path(f"collections/{collection_name}.yaml")
                if collection_file.exists():
                    import yaml
                    with open(collection_file, 'r', encoding='utf-8') as f:
                        collection_data = yaml.safe_load(f)
                    for book in collection_data.get('books', []):
                        if str(book.get('order', '')) == args.book_id:
                            book_path = Path(book['path'])
                            break
                    else:
                        book_path = None
                else:
                    book_path = None
            else:
                book_path = get_book_path(args.target)
            
            if book_path:
                console.print(f"[yellow]Generating prompts for: {book_path}[/yellow]")
                result = subprocess.run([
                    sys.executable, "src/prompt_builder.py", str(book_path)
                ])
                if result.returncode == 0:
                    console.print("[green]✓ Prompts generated successfully[/green]")
                else:
                    console.print("[red]✗ Prompt generation failed[/red]")
            else:
                console.print(f"[red]Book '{args.target}' not found![/red]")
                
        elif args.command == 'research':
            research.research_book(args.target, args.book_id, args.provider)
            
        elif args.command == 'site':
            site.generate_site(args.target, args.book_id)
            
        elif args.command == 'convert-scenes':
            # Call convert_scenes with proper arguments
            from pathlib import Path
            path_obj = Path(args.path)
            
            # Normalize format names
            from_format = 'yaml' if args.from_format == 'yml' else args.from_format
            to_format = 'yaml' if args.to_format == 'yml' else args.to_format
            
            if path_obj.is_file():
                # Single file conversion
                output_path = Path(args.output) if args.output else None
                convert_scenes.convert_file(path_obj, output_path, from_format, to_format)
            else:
                # Directory conversion
                if args.output:
                    console.print("[yellow]Warning: --output option is ignored for directory conversion[/yellow]")
                convert_scenes.convert_directory(path_obj, from_format, to_format, args.recursive)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()