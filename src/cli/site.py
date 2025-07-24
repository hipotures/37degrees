"""Site generation command"""

from pathlib import Path
from rich.console import Console

from src.site_generator import SiteBuilder
from src.cli.utils import resolve_target, get_book_path

console = Console()


def generate_site(target: str = None, book_id: str = None):
    """Generate static HTML site
    
    Args:
        target: Optional - specific book ID, book name, or collection name
        book_id: Optional - specific book ID when target is a collection
    """
    
    builder = SiteBuilder()
    
    if not target:
        # Generate entire site
        console.print("[bold cyan]Generating complete site...[/bold cyan]")
        builder.build_site()
    else:
        # Resolve target
        target_type, target_value = resolve_target(target)
        
        if target_type == "collection":
            if book_id:
                # Generate specific book from collection
                console.print(f"[bold cyan]Generating book #{book_id} from {target_value} collection[/bold cyan]")
                book_ids = [f"{book_id:04d}"]  # Assuming 4-digit format
                builder.build_site(book_ids=book_ids)
            else:
                # Generate all books in collection
                console.print(f"[bold cyan]Generating all books in {target_value} collection[/bold cyan]")
                builder.build_site(collections=[target_value])
        else:
            # Generate single book
            book_path = get_book_path(target_value)
            if book_path:
                book_id = book_path.parent.name
                console.print(f"[bold cyan]Generating page for book: {book_id}[/bold cyan]")
                builder.build_site(book_ids=[book_id])
            else:
                console.print(f"[red]Book '{target}' not found![/red]")