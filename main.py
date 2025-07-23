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

# Import CLI modules
from src.cli import collections, list_books, video, ai

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
"""
    )
    
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
    
    # Generate command (AI + Video)
    generate_parser = subparsers.add_parser('generate', help='Generate AI images and video')
    generate_parser.add_argument('target', help='Book ID, name, or collection')
    generate_parser.add_argument('book_id', nargs='?', help='Book ID when target is collection')
    generate_parser.add_argument('--template', help='Template name or path')
    
    # Prompts command
    prompts_parser = subparsers.add_parser('prompts', help='Generate prompts from book.yaml')
    prompts_parser.add_argument('target', help='Book ID, name, or collection')
    prompts_parser.add_argument('book_id', nargs='?', help='Book ID when target is collection')
    
    args = parser.parse_args()
    
    # Display banner
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
            ai.generate_images(args.target, args.book_id)
            
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
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()