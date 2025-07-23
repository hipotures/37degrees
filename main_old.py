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
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()