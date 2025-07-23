"""Book listing functionality for 37degrees"""

from pathlib import Path
import yaml
from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()


def get_book_info(book_path: Path) -> dict:
    """Get book information from YAML file"""
    try:
        with open(book_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data.get('book_info', {})
    except:
        return {}


def list_all_books():
    """List all books in the books directory"""
    books_dir = Path("books")
    book_dirs = sorted([d for d in books_dir.iterdir() if d.is_dir() and (d / "book.yaml").exists()])
    
    if not book_dirs:
        console.print("[red]No books found![/red]")
        return
    
    # Create rich table
    table = Table(title="All Books", show_lines=True)
    table.add_column("ID", style="cyan", no_wrap=True, width=6)
    table.add_column("Title", style="green", width=30)
    table.add_column("Author", style="yellow", width=25)
    table.add_column("Genre", style="magenta", width=20)
    table.add_column("Folder", style="dim", width=25)
    
    for book_dir in book_dirs:
        book_yaml = book_dir / "book.yaml"
        book_info = get_book_info(book_yaml)
        
        # Extract ID from folder name
        folder_name = book_dir.name
        book_id = folder_name.split('_')[0] if '_' in folder_name else "?"
        
        table.add_row(
            book_id,
            book_info.get('title', 'Unknown')[:30],
            book_info.get('author', 'Unknown')[:25],
            book_info.get('genre', '-')[:20],
            folder_name[:25]
        )
    
    console.print(table)
    console.print(f"\n[dim]Total books: {len(book_dirs)}[/dim]")


def list_collection_books(collection_name: str):
    """List books in a specific collection"""
    collection_file = Path(f"collections/{collection_name}.yaml")
    
    if not collection_file.exists():
        console.print(f"[red]Collection '{collection_name}' not found![/red]")
        console.print("[dim]Available collections:[/dim]")
        for f in Path("collections").glob("*.yaml"):
            console.print(f"  - {f.stem}")
        return
    
    # Load collection
    with open(collection_file, 'r', encoding='utf-8') as f:
        collection_data = yaml.safe_load(f)
    
    series_info = collection_data.get('series', {})
    books = collection_data.get('books', [])
    
    # Display collection info
    console.print(f"\n[bold cyan]{series_info.get('name', collection_name)}[/bold cyan]")
    console.print(f"[dim]{series_info.get('description', 'No description')}[/dim]\n")
    
    # Create rich table
    table = Table(show_lines=True)
    table.add_column("No.", style="cyan", no_wrap=True, width=6)
    table.add_column("Title", style="green", width=30)
    table.add_column("Author", style="yellow", width=25)
    table.add_column("Tags", style="magenta")
    table.add_column("Status", style="blue", width=12)
    
    for book_ref in books:
        book_path = Path(book_ref['path'])
        
        if book_path.exists():
            book_info = get_book_info(book_path)
            
            # Check if images exist
            book_dir = book_path.parent
            has_images = (book_dir / "generated").exists() and list((book_dir / "generated").glob("*.png"))
            status = "[green]✓ Ready[/green]" if has_images else "[yellow]⚠ No images[/yellow]"
            
            tags = ', '.join(book_ref.get('tags', [])[:3])
            
            table.add_row(
                str(book_ref.get('order', '?')),
                book_info.get('title', 'Unknown')[:30],
                book_info.get('author', 'Unknown')[:25],
                tags,
                status
            )
        else:
            table.add_row(
                str(book_ref.get('order', '?')),
                "[red]Missing book file[/red]",
                "-",
                "-",
                "[red]✗ Error[/red]"
            )
    
    console.print(table)
    console.print(f"\n[dim]Total books in collection: {len(books)}[/dim]")