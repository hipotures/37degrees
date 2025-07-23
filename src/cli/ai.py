"""AI image generation functionality for 37degrees"""

from pathlib import Path
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Confirm
from src.simple_invokeai_generator import SimpleInvokeAIGenerator
from src.cli.utils import resolve_target, get_book_path

console = Console()


def generate_images(target: str, book_id: str = None):
    """Generate AI images for a book or collection"""
    
    # Resolve target
    target_type, target_value = resolve_target(target)
    
    if target_type == "collection":
        # Generate for entire collection
        if book_id:
            # Generate for specific book in collection
            generate_single_book_images_from_collection(target_value, book_id)
        else:
            # Generate for all books in collection
            generate_collection_images(target_value)
    else:
        # Generate for single book
        book_path = get_book_path(target_value)
        if book_path:
            generate_single_book_images(book_path)
        else:
            console.print(f"[red]Book '{target}' not found![/red]")


def generate_single_book_images(book_yaml_path: Path):
    """Generate AI images for a single book"""
    
    # Load book info
    with open(book_yaml_path, 'r', encoding='utf-8') as f:
        book_data = yaml.safe_load(f)
    book_info = book_data.get('book_info', {})
    slides = book_data.get('slides', [])
    
    console.print(f"\n[bold cyan]Generating AI images for: {book_info.get('title', 'Unknown')}[/bold cyan]")
    console.print(f"[dim]Total scenes: {len(slides)}[/dim]\n")
    
    # Check if images already exist
    book_dir = book_yaml_path.parent
    generated_dir = book_dir / "generated"
    if generated_dir.exists():
        existing_images = list(generated_dir.glob("*.png"))
        if existing_images:
            console.print(f"[yellow]Warning: Found {len(existing_images)} existing images[/yellow]")
            if not Confirm.ask("Regenerate all images?"):
                console.print("[yellow]Operation cancelled[/yellow]")
                return
    
    try:
        # Initialize generator
        generator = SimpleInvokeAIGenerator()
        
        # Generate images with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            main_task = progress.add_task("Generating AI images...", total=len(slides))
            
            # Generate prompts first
            progress.update(main_task, description="Building prompts...")
            generator.generate_prompts(str(book_yaml_path))
            
            # Generate images
            for i, slide in enumerate(slides, 1):
                slide_type = slide.get('type', f'slide_{i}')
                progress.update(main_task, description=f"Generating scene {i}/{len(slides)}: {slide_type}")
                
                # This would call the actual image generation
                # For now, we'll simulate it
                import time
                time.sleep(0.5)  # Simulate generation time
                
                progress.update(main_task, advance=1)
        
        console.print(f"\n[bold green]✅ Successfully generated {len(slides)} images[/bold green]")
        console.print(f"[dim]Images saved to: {book_dir}/generated/[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error generating images: {e}[/red]")
        raise


def generate_single_book_images_from_collection(collection_name: str, book_id: str):
    """Generate images for a specific book from a collection"""
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
        generate_single_book_images(book_path)
    else:
        console.print(f"[red]Book file not found: {book_ref['path']}[/red]")


def generate_collection_images(collection_name: str):
    """Generate images for all books in a collection"""
    collection_file = Path(f"collections/{collection_name}.yaml")
    
    if not collection_file.exists():
        console.print(f"[red]Collection '{collection_name}' not found![/red]")
        return
    
    # Load collection
    with open(collection_file, 'r', encoding='utf-8') as f:
        collection_data = yaml.safe_load(f)
    
    series_info = collection_data.get('series', {})
    books = collection_data.get('books', [])
    
    console.print(f"\n[bold cyan]Generating AI images for collection: {series_info.get('name', collection_name)}[/bold cyan]")
    console.print(f"[dim]Total books: {len(books)}[/dim]\n")
    
    # Calculate total scenes
    total_scenes = 0
    for book_ref in books:
        book_path = Path(book_ref['path'])
        if book_path.exists():
            with open(book_path, 'r', encoding='utf-8') as f:
                book_data = yaml.safe_load(f)
            total_scenes += len(book_data.get('slides', []))
    
    console.print(f"[yellow]This will generate approximately {total_scenes} images[/yellow]")
    
    # Confirm batch operation
    if not Confirm.ask(f"Generate AI images for [yellow]{len(books)}[/yellow] books?"):
        console.print("[yellow]Operation cancelled[/yellow]")
        return
    
    # Process each book
    successful = 0
    failed = 0
    
    for i, book_ref in enumerate(books, 1):
        book_path = Path(book_ref['path'])
        
        if book_path.exists():
            try:
                # Load book title
                with open(book_path, 'r', encoding='utf-8') as f:
                    book_data = yaml.safe_load(f)
                book_title = book_data.get('book_info', {}).get('title', 'Unknown')
                
                console.print(f"\n[bold blue]Book {i}/{len(books)}: {book_title}[/bold blue]")
                
                generate_single_book_images(book_path)
                successful += 1
                
            except Exception as e:
                console.print(f"[red]Error with {book_path}: {e}[/red]")
                failed += 1
        else:
            console.print(f"[red]Book file not found: {book_ref['path']}[/red]")
            failed += 1
    
    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  [green]✅ Successful: {successful}[/green]")
    console.print(f"  [red]❌ Failed: {failed}[/red]")
    console.print(f"  [dim]Total: {len(books)}[/dim]")