"""Video generation functionality for 37degrees"""

from pathlib import Path
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.prompt import Confirm
from src.video_generator import VideoGenerator
from src.cli.utils import resolve_target, get_book_path

console = Console()


def generate_video(target: str, book_id: str = None, only_render: bool = False, template: str = None):
    """Generate video for a book or collection"""
    
    # Resolve target
    target_type, target_value = resolve_target(target)
    
    if target_type == "collection":
        # Generate for entire collection
        if book_id:
            # Generate for specific book in collection
            generate_single_video_from_collection(target_value, book_id, only_render, template)
        else:
            # Generate for all books in collection
            generate_collection_videos(target_value, only_render, template)
    else:
        # Generate for single book
        book_path = get_book_path(target_value)
        if book_path:
            generate_single_video(book_path, only_render, template)
        else:
            console.print(f"[red]Book '{target}' not found![/red]")


def generate_single_video(book_yaml_path: Path, only_render: bool = False, template_name: str = None):
    """Generate video for a single book"""
    
    # Default template
    template_path = "shared_assets/templates/classics_template.yaml"
    if template_name:
        # Check if it's a path or just a name
        if Path(template_name).exists():
            template_path = template_name
        else:
            # Try to find template in templates directory
            template_file = Path(f"shared_assets/templates/{template_name}_template.yaml")
            if template_file.exists():
                template_path = str(template_file)
            else:
                console.print(f"[yellow]Template '{template_name}' not found, using default[/yellow]")
    
    # Load book info
    with open(book_yaml_path, 'r', encoding='utf-8') as f:
        book_data = yaml.safe_load(f)
    book_info = book_data.get('book_info', {})
    
    console.print(f"\n[bold cyan]Generating video for: {book_info.get('title', 'Unknown')}[/bold cyan]")
    
    if only_render:
        console.print("[yellow]Mode: Only rendering (using existing images)[/yellow]")
    
    try:
        # Initialize generator
        generator = VideoGenerator(template_path)
        
        # Generate video (MoviePy will handle progress display)
        output_path = generator.generate_video(str(book_yaml_path))
        
        console.print(f"\n[bold green]✅ Video saved to: {output_path}[/bold green]")
        
    except Exception as e:
        console.print(f"[red]Error generating video: {e}[/red]")
        raise


def generate_single_video_from_collection(collection_name: str, book_id: str, only_render: bool = False, template: str = None):
    """Generate video for a specific book from a collection"""
    collection_file = Path(f"collections/{collection_name}.yaml")
    
    if not collection_file.exists():
        console.print(f"[red]Collection '{collection_name}' not found![/red]")
        return
    
    # Load collection
    with open(collection_file, 'r', encoding='utf-8') as f:
        collection_data = yaml.safe_load(f)
    
    books = collection_data.get('books', [])
    
    # Find book by order number
    book_ref = None
    for book in books:
        if str(book.get('order', '')) == book_id:
            book_ref = book
            break
    
    if not book_ref:
        console.print(f"[red]Book #{book_id} not found in collection '{collection_name}'[/red]")
        return
    
    book_path = Path(book_ref['path'])
    if book_path.exists():
        generate_single_video(book_path, only_render, template)
    else:
        console.print(f"[red]Book file not found: {book_ref['path']}[/red]")


def generate_collection_videos(collection_name: str, only_render: bool = False, template: str = None):
    """Generate videos for all books in a collection"""
    collection_file = Path(f"collections/{collection_name}.yaml")
    
    if not collection_file.exists():
        console.print(f"[red]Collection '{collection_name}' not found![/red]")
        return
    
    # Load collection
    with open(collection_file, 'r', encoding='utf-8') as f:
        collection_data = yaml.safe_load(f)
    
    series_info = collection_data.get('series', {})
    books = collection_data.get('books', [])
    
    console.print(f"\n[bold cyan]Generating videos for collection: {series_info.get('name', collection_name)}[/bold cyan]")
    console.print(f"[dim]Total books: {len(books)}[/dim]\n")
    
    # Confirm batch operation
    if not Confirm.ask(f"Generate videos for [yellow]{len(books)}[/yellow] books?"):
        console.print("[yellow]Operation cancelled[/yellow]")
        return
    
    # Process each book
    successful = 0
    failed = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        
        main_task = progress.add_task("Processing collection...", total=len(books))
        
        for i, book_ref in enumerate(books, 1):
            book_path = Path(book_ref['path'])
            
            if book_path.exists():
                try:
                    # Load book title
                    with open(book_path, 'r', encoding='utf-8') as f:
                        book_data = yaml.safe_load(f)
                    book_title = book_data.get('book_info', {}).get('title', 'Unknown')
                    
                    progress.update(main_task, description=f"[{i}/{len(books)}] {book_title[:30]}...")
                    
                    generate_single_video(book_path, only_render, template)
                    successful += 1
                    
                except Exception as e:
                    console.print(f"[red]Error with {book_path}: {e}[/red]")
                    failed += 1
            else:
                console.print(f"[red]Book file not found: {book_ref['path']}[/red]")
                failed += 1
            
            progress.update(main_task, advance=1)
    
    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  [green]✅ Successful: {successful}[/green]")
    console.print(f"  [red]❌ Failed: {failed}[/red]")
    console.print(f"  [dim]Total: {len(books)}[/dim]")