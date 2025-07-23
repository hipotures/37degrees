#!/usr/bin/env python3
"""
37 Degrees TikTok Video Generator
Main entry point for generating book review TikTok videos
"""

import argparse
import sys
import yaml
from pathlib import Path
from src.video_generator import VideoGenerator
from src.utils import validate_yaml_structure, format_duration

# Simple console replacement
class Console:
    def print(self, *args, **kwargs):
        print(*args)

console = Console()


def display_banner():
    """Display application banner"""
    banner = """
    ╔═══════════════════════════════════════╗
    ║      37 DEGREES - TikTok Generator    ║
    ║         Book Video Generator          ║
    ╚═══════════════════════════════════════╝
    """
    print(banner)


def list_series_books(series_file: str = "content/classics.yaml"):
    """List all books in a series"""
    if not Path(series_file).exists():
        console.print(f"[red]Series file not found: {series_file}[/red]")
        return
    
    # Load series configuration
    with open(series_file, 'r', encoding='utf-8') as f:
        series_config = yaml.safe_load(f)
    
    series_info = series_config['series']
    books = series_config['books']
    
    # Display series info
    console.print(f"\n[bold cyan]{series_info['name']}[/bold cyan]")
    console.print(f"[dim]{series_info['description']}[/dim]\n")
    
    # Simple table display
    print("\nBooks in Series")
    print("-" * 80)
    print(f"{'No.':<5} {'Title':<30} {'Author':<25} {'Tags'}")
    print("-" * 80)
    
    for i, book_ref in enumerate(books):
        try:
            # Load book info
            with open(book_ref['path'], 'r', encoding='utf-8') as f:
                book_data = yaml.safe_load(f)
                book_info = book_data['book_info']
                
            tags = ', '.join(book_ref.get('tags', [])[:3])  # Show first 3 tags
            print(f"{book_ref['order']:<5} {book_info['title'][:29]:<30} {book_info['author'][:24]:<25} {tags}")
        except Exception as e:
            print(f"{i + 1:<5} Error: {book_ref['path']}")
    console.print(f"\n[dim]Total books: {len(books)}[/dim]")


def list_all_books(books_dir: str = "books"):
    """List all books in the books directory"""
    book_files = sorted(Path(books_dir).glob("*/book.yaml"))
    
    if not book_files:
        console.print("[red]No book files found in books directory![/red]")
        return
    
    # Simple table display
    print("\nAll Available Books")
    print("-" * 100)
    print(f"{'Path':<35} {'Title':<30} {'Author':<25} {'Genre'}")
    print("-" * 100)
    
    for book_file in book_files:
        try:
            with open(book_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                book_info = data.get('book_info', {})
                
            relative_path = str(book_file.relative_to(Path.cwd()))
            title = book_info.get('title', 'Unknown')[:29]
            author = book_info.get('author', 'Unknown')[:24]
            genre = book_info.get('genre', '-')
            print(f"{relative_path:<35} {title:<30} {author:<25} {genre}")
        except Exception as e:
            print(f"{str(book_file):<35} Error reading file")
    console.print(f"\n[dim]Total books: {len(book_files)}[/dim]")


def generate_single_video(book_ref: str, template: str = "templates/classics_template.yaml", 
                         series_file: str = None):
    """Generate video for a single book
    
    book_ref can be:
    - Direct path to book YAML file
    - Index number if series_file is provided
    """
    try:
        # Determine book path
        if series_file and book_ref.isdigit():
            # Generate from series by index
            book_index = int(book_ref) - 1  # Convert to 0-based index
            
            with open(series_file, 'r', encoding='utf-8') as f:
                series_config = yaml.safe_load(f)
            
            books = series_config['books']
            if book_index < 0 or book_index >= len(books):
                console.print(f"[red]Invalid book index: {book_ref} (valid range: 1-{len(books)})[/red]")
                return
            
            book_path = books[book_index]['path']
            console.print(f"[blue]Generating video for book #{book_ref} from series[/blue]")
        else:
            # Direct path provided
            book_path = book_ref
        
        # Validate inputs
        if not Path(book_path).exists():
            console.print(f"[red]Book YAML file not found: {book_path}[/red]")
            return
        
        if not Path(template).exists():
            console.print(f"[red]Template file not found: {template}[/red]")
            return
        
        # Initialize generator
        generator = VideoGenerator(template)
        
        # Generate video
        output_path = generator.generate_video(book_path)
        
        console.print(f"\n[bold green]✅ Success! Video saved to: {output_path}[/bold green]")
        
    except Exception as e:
        import traceback
        console.print(f"[red]Error generating video: {e}[/red]")
        traceback.print_exc()
        raise


def generate_batch_videos(series_file: str = "content/classics.yaml", 
                         template: str = "templates/classics_template.yaml"):
    """Generate videos for all books in a series"""
    try:
        # Validate inputs
        if not Path(series_file).exists():
            console.print(f"[red]Series file not found: {series_file}[/red]")
            return
        
        if not Path(template).exists():
            console.print(f"[red]Template file not found: {template}[/red]")
            return
        
        # Initialize generator
        generator = VideoGenerator(template)
        
        # Generate all videos
        generated_videos = generator.batch_generate(series_file)
        
        # Summary
        console.print("\n[bold green]Batch generation complete![/bold green]")
        console.print(f"Generated {len(generated_videos)} videos")
        
    except Exception as e:
        console.print(f"[red]Error in batch generation: {e}[/red]")
        raise


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="37 Degrees TikTok Video Generator - Create engaging book review videos",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'command',
        choices=['generate', 'batch', 'list', 'list-all'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '-b', '--book',
        type=str,
        help='Book reference: path to YAML file or index number (when used with -s)'
    )
    
    parser.add_argument(
        '-s', '--series',
        type=str,
        default='content/classics.yaml',
        help='Path to series YAML file'
    )
    
    parser.add_argument(
        '-t', '--template',
        type=str,
        default='shared_assets/templates/classics_template.yaml',
        help='Path to template YAML file'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output video path (optional)'
    )
    
    args = parser.parse_args()
    
    # Display banner
    display_banner()
    
    # Execute command
    if args.command == 'list':
        list_series_books(args.series)
    
    elif args.command == 'list-all':
        list_all_books()
    
    elif args.command == 'generate':
        if not args.book:
            console.print("[red]Please specify a book with -b/--book[/red]")
            console.print("[dim]Examples:[/dim]")
            console.print("  python main.py generate -b books/l/i/little_prince.yaml")
            console.print("  python main.py generate -b 1 -s content/classics.yaml")
            sys.exit(1)
        generate_single_video(args.book, args.template, args.series)
    
    elif args.command == 'batch':
        console.print(f"[yellow]Starting batch generation for series: {args.series}[/yellow]")
        generate_batch_videos(args.series, args.template)
    
    console.print("\n[dim]Thank you for using 37 Degrees TikTok Generator![/dim]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]")
        sys.exit(1)