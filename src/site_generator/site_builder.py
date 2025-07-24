"""
Site builder orchestrator
"""

from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from .book_page import BookPageGenerator
from .index_page import IndexPageGenerator
from .collection_page import CollectionPageGenerator

console = Console()


class SiteBuilder:
    """Orchestrate the generation of the entire static site"""
    
    def __init__(self, output_dir: Path = None):
        """Initialize site builder
        
        Args:
            output_dir: Output directory for generated site
        """
        from src.config import get_config
        config = get_config()
        
        self.output_dir = output_dir or Path(config.get('paths.site_output', 'site'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize generators
        self.book_generator = BookPageGenerator(self.output_dir)
        self.index_generator = IndexPageGenerator(self.output_dir)
        self.collection_generator = CollectionPageGenerator(self.output_dir)
    
    def build_site(self, book_ids: Optional[List[str]] = None, 
                   collections: Optional[List[str]] = None):
        """Build the entire site or specific parts
        
        Args:
            book_ids: Specific book IDs to generate (None = all)
            collections: Specific collections to generate (None = all)
        """
        console.print("[bold cyan]🚀 Starting site generation...[/bold cyan]")
        
        # Get all books and collections
        all_books = self._get_all_books(book_ids)
        all_collections = self._get_all_collections(collections)
        
        total_tasks = len(all_books) + len(all_collections) + 1  # +1 for index
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            task = progress.add_task("Building site...", total=total_tasks)
            
            # Generate book pages
            console.print("\n[yellow]📚 Generating book pages...[/yellow]")
            successful_books = 0
            failed_books = 0
            
            for book_path in all_books:
                try:
                    book_id = book_path.parent.name
                    book_title = self._get_book_title(book_path)
                    
                    progress.update(task, description=f"Generating: {book_title}")
                    
                    output_path = self.book_generator.generate(book_path)
                    successful_books += 1
                    console.print(f"  ✅ {book_title} → {output_path.relative_to(self.output_dir)}")
                    
                except Exception as e:
                    failed_books += 1
                    console.print(f"  ❌ Failed to generate {book_path}: {e}")
                
                progress.advance(task)
            
            # Generate collection pages
            console.print("\n[yellow]📁 Generating collection pages...[/yellow]")
            successful_collections = 0
            failed_collections = 0
            
            for collection_path in all_collections:
                try:
                    collection_name = collection_path.stem
                    progress.update(task, description=f"Generating: {collection_name}")
                    
                    output_path = self.collection_generator.generate(collection_path)
                    successful_collections += 1
                    console.print(f"  ✅ {collection_name} → {output_path.relative_to(self.output_dir)}")
                    
                except Exception as e:
                    failed_collections += 1
                    console.print(f"  ❌ Failed to generate {collection_path}: {e}")
                
                progress.advance(task)
            
            # Generate index page
            console.print("\n[yellow]🏠 Generating index page...[/yellow]")
            progress.update(task, description="Generating index.html")
            
            try:
                index_path = self.index_generator.generate()
                console.print(f"  ✅ index.html → {index_path.relative_to(self.output_dir)}")
            except Exception as e:
                console.print(f"  ❌ Failed to generate index: {e}")
            
            progress.advance(task)
        
        # Summary
        console.print("\n[bold green]✨ Site generation complete![/bold green]")
        console.print(f"\n📊 Summary:")
        console.print(f"  Books: {successful_books} ✅ / {failed_books} ❌")
        console.print(f"  Collections: {successful_collections} ✅ / {failed_collections} ❌")
        console.print(f"  Output: {self.output_dir.absolute()}")
        
        # Create simple HTTP server command
        console.print(f"\n💡 To preview the site, run:")
        console.print(f"  [bold]cd {self.output_dir} && python -m http.server 8000[/bold]")
        console.print(f"  Then open: [link]http://localhost:8000[/link]")
    
    def _get_all_books(self, book_ids: Optional[List[str]] = None) -> List[Path]:
        """Get all book YAML files to process"""
        books_dir = Path('books')
        all_books = []
        
        if books_dir.exists():
            if book_ids:
                # Specific books
                for book_id in book_ids:
                    # Try exact match first
                    book_path = books_dir / book_id / 'book.yaml'
                    if book_path.exists():
                        all_books.append(book_path)
                    else:
                        # Try pattern match
                        for book_dir in books_dir.iterdir():
                            if book_id in book_dir.name:
                                yaml_path = book_dir / 'book.yaml'
                                if yaml_path.exists():
                                    all_books.append(yaml_path)
            else:
                # All books
                for book_dir in sorted(books_dir.iterdir()):
                    if book_dir.is_dir():
                        yaml_path = book_dir / 'book.yaml'
                        if yaml_path.exists():
                            all_books.append(yaml_path)
        
        return all_books
    
    def _get_all_collections(self, collection_names: Optional[List[str]] = None) -> List[Path]:
        """Get all collection YAML files to process"""
        collections_dir = Path('collections')
        all_collections = []
        
        if collections_dir.exists():
            if collection_names:
                # Specific collections
                for name in collection_names:
                    collection_path = collections_dir / f'{name}.yaml'
                    if collection_path.exists():
                        all_collections.append(collection_path)
            else:
                # All collections
                all_collections = list(collections_dir.glob('*.yaml'))
        
        return all_collections
    
    def _get_book_title(self, book_yaml_path: Path) -> str:
        """Get book title from YAML file"""
        try:
            import yaml
            with open(book_yaml_path, 'r', encoding='utf-8') as f:
                book_data = yaml.safe_load(f)
            return book_data.get('book_info', {}).get('title', book_yaml_path.parent.name)
        except:
            return book_yaml_path.parent.name