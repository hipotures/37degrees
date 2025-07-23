#!/usr/bin/env python3
"""Create docs directories for all books and move existing documents"""

from pathlib import Path
import shutil
from rich.console import Console
from rich.progress import track

console = Console()


def create_docs_structure():
    """Create docs directories for all books"""
    books_dir = Path('books')
    
    # Get all book directories
    book_dirs = sorted([d for d in books_dir.iterdir() if d.is_dir() and (d / "book.yaml").exists()])
    
    console.print(f"[bold cyan]Creating docs structure for {len(book_dirs)} books[/bold cyan]")
    
    created_count = 0
    moved_files = 0
    
    for book_dir in track(book_dirs, description="Processing books..."):
        # Create docs directory
        docs_dir = book_dir / "docs"
        if not docs_dir.exists():
            docs_dir.mkdir(exist_ok=True)
            created_count += 1
            
            # Add README.md template if it doesn't exist
            readme_path = docs_dir / "README.md"
            if not readme_path.exists():
                template_path = Path("shared_assets/templates/docs_readme_template.md")
                if template_path.exists():
                    shutil.copy(str(template_path), str(readme_path))
        
        # Check for existing documents to move
        # Look for markdown files that are not book.yaml
        md_files = [f for f in book_dir.glob("*.md") if f.name != "README.md"]
        
        for md_file in md_files:
            # Move to docs directory
            target_path = docs_dir / md_file.name
            console.print(f"[yellow]Moving {md_file.name} to docs/[/yellow]")
            shutil.move(str(md_file), str(target_path))
            moved_files += 1
        
        # Special case for review.md in little_prince
        if book_dir.name == "0017_little_prince":
            review_file = book_dir / "review.md"
            if review_file.exists() and not (docs_dir / "review.md").exists():
                console.print(f"[yellow]Moving review.md to docs/ for {book_dir.name}[/yellow]")
                shutil.move(str(review_file), str(docs_dir / "review.md"))
                moved_files += 1
    
    console.print(f"\n[green]✓ Created {created_count} docs directories[/green]")
    console.print(f"[green]✓ Moved {moved_files} documents[/green]")
    
    # Show summary of what's in docs directories
    console.print("\n[bold]Books with documents:[/bold]")
    for book_dir in book_dirs:
        docs_dir = book_dir / "docs"
        if docs_dir.exists():
            doc_files = list(docs_dir.glob("*"))
            if doc_files:
                console.print(f"  {book_dir.name}:")
                for doc in doc_files:
                    console.print(f"    - {doc.name}")


if __name__ == "__main__":
    create_docs_structure()