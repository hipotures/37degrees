"""Research command for generating book review content"""

from pathlib import Path
import yaml
from rich.console import Console
from rich.prompt import Confirm

from src.research import registry
from src.research.perplexity_api import PerplexityProvider
from src.research.google_search import GoogleSearchProvider
from src.research.mock import MockResearchProvider
from src.research.review_generator import ReviewGenerator
from src.cli.utils import resolve_target, get_book_path

console = Console()

# Register available providers
registry.register('perplexity', PerplexityProvider)
registry.register('google', GoogleSearchProvider)
registry.register('mock', MockResearchProvider)


def research_book(target: str, book_id: str = None, provider: str = None):
    """Generate research content for a book or collection
    
    Args:
        target: Book ID, book name, or collection name
        book_id: Specific book ID when target is a collection
        provider: Research provider to use (perplexity, google, mock)
    """
    
    # Resolve target
    target_type, target_value = resolve_target(target)
    
    if target_type == "collection":
        # Research for entire collection
        if book_id:
            # Research specific book in collection
            research_single_book_from_collection(target_value, book_id, provider)
        else:
            # Research all books in collection
            research_collection(target_value, provider)
    else:
        # Research single book
        book_path = get_book_path(target_value)
        if book_path:
            research_single_book(book_path, provider)
        else:
            console.print(f"[red]Book '{target}' not found![/red]")


def research_single_book(book_yaml_path: Path, provider: str = None):
    """Generate research for a single book"""
    
    # Load book info
    with open(book_yaml_path, 'r', encoding='utf-8') as f:
        book_data = yaml.safe_load(f)
    book_info = book_data.get('book_info', {})
    
    console.print(f"\n[bold cyan]Researching: {book_info.get('title', 'Unknown')}[/bold cyan]")
    console.print(f"[dim]Author: {book_info.get('author', 'Unknown')}[/dim]\n")
    
    # Check if review already exists
    book_dir = book_yaml_path.parent
    review_path = book_dir / 'docs' / 'review.md'
    
    if review_path.exists():
        console.print(f"[yellow]Review already exists at: {review_path}[/yellow]")
        if not Confirm.ask("Regenerate review?"):
            console.print("[yellow]Operation cancelled[/yellow]")
            return
    
    # Initialize generator
    generator = ReviewGenerator(provider)
    
    # Generate review
    if generator.generate_review(book_yaml_path):
        console.print("\n[bold green]✅ Review generated successfully![/bold green]")
        
        # Show sample
        if review_path.exists():
            with open(review_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]
            console.print("\n[dim]Preview:[/dim]")
            for line in lines:
                console.print(f"[dim]{line.rstrip()}[/dim]")
            console.print("[dim]...[/dim]")
    else:
        console.print("\n[bold red]❌ Failed to generate review[/bold red]")


def research_single_book_from_collection(collection_name: str, book_id: str, provider: str = None):
    """Research a specific book from a collection"""
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
        research_single_book(book_path, provider)
    else:
        console.print(f"[red]Book file not found: {book_ref['path']}[/red]")


def research_collection(collection_name: str, provider: str = None):
    """Research all books in a collection"""
    collection_file = Path(f"collections/{collection_name}.yaml")
    
    if not collection_file.exists():
        console.print(f"[red]Collection '{collection_name}' not found![/red]")
        return
    
    # Load collection
    with open(collection_file, 'r', encoding='utf-8') as f:
        collection_data = yaml.safe_load(f)
    
    series_info = collection_data.get('series', {})
    books = collection_data.get('books', [])
    
    console.print(f"\n[bold cyan]Researching collection: {series_info.get('name', collection_name)}[/bold cyan]")
    console.print(f"[dim]Total books: {len(books)}[/dim]\n")
    
    # Count existing reviews
    existing_reviews = 0
    for book_ref in books:
        book_path = Path(book_ref['path'])
        if book_path.exists():
            review_path = book_path.parent / 'docs' / 'review.md'
            if review_path.exists():
                existing_reviews += 1
    
    console.print(f"[yellow]Found {existing_reviews} existing reviews[/yellow]")
    
    # Confirm batch operation
    if not Confirm.ask(f"Generate reviews for [yellow]{len(books)}[/yellow] books?"):
        console.print("[yellow]Operation cancelled[/yellow]")
        return
    
    # Initialize generator
    generator = ReviewGenerator(provider)
    
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
                
                if generator.generate_review(book_path):
                    successful += 1
                else:
                    failed += 1
                    
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