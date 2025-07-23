"""Collections management for 37degrees"""

from pathlib import Path
import yaml
from rich.console import Console
from rich.table import Table

console = Console()


def list_collections():
    """List all available collections"""
    collections_dir = Path("collections")
    
    if not collections_dir.exists():
        console.print("[red]No collections directory found![/red]")
        return
    
    # Find all YAML files in collections directory
    collection_files = list(collections_dir.glob("*.yaml"))
    
    if not collection_files:
        console.print("[yellow]No collections found in collections directory[/yellow]")
        return
    
    # Create rich table
    table = Table(title="Available Collections")
    table.add_column("Collection", style="cyan", no_wrap=True)
    table.add_column("Description", style="green")
    table.add_column("Books", justify="right", style="yellow")
    
    for collection_file in sorted(collection_files):
        try:
            with open(collection_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Extract collection name from filename
            collection_name = collection_file.stem
            
            # Get series info if available
            series_info = data.get('series', {})
            description = series_info.get('description', 'No description')
            
            # Count books
            books = data.get('books', [])
            book_count = len(books)
            
            table.add_row(
                collection_name,
                description[:50] + "..." if len(description) > 50 else description,
                str(book_count)
            )
            
        except Exception as e:
            console.print(f"[red]Error reading {collection_file}: {e}[/red]")
    
    console.print(table)