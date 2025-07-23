#!/usr/bin/env python3
"""
Migration script to reorganize book structure
From: books/[a-z]/[a-z]/book_name.yaml
To: books/book_name/book.yaml
"""

import os
import shutil
import yaml
from pathlib import Path
import sys

class Console:
    def print(self, *args, **kwargs):
        # Extract text from rich markup
        text = ' '.join(str(arg) for arg in args)
        text = text.replace('[bold cyan]', '').replace('[/bold cyan]', '')
        text = text.replace('[yellow]', '').replace('[/yellow]', '')
        text = text.replace('[green]', '').replace('[/green]', '')
        text = text.replace('[red]', '').replace('[/red]', '')
        text = text.replace('[bold green]', '').replace('[/bold green]', '')
        text = text.replace('[cyan]', '').replace('[/cyan]', '')
        text = text.replace('[dim]', '').replace('[/dim]', '')
        text = text.replace('[bold]', '').replace('[/bold]', '')
        print(text)
    
    def input(self, prompt):
        return input(prompt)

console = Console()

def track(iterable, description=None):
    if description:
        print(f"\n{description}...")
    return iterable


def migrate_books():
    """Migrate all books to new structure"""
    console.print("[bold cyan]Starting book structure migration...[/bold cyan]")
    
    # Find all existing book YAML files
    old_book_files = list(Path("books").glob("*/*/*.yaml"))
    console.print(f"Found {len(old_book_files)} books to migrate")
    
    # Create backup
    backup_dir = Path("books_backup")
    if not backup_dir.exists():
        console.print("[yellow]Creating backup of current structure...[/yellow]")
        shutil.copytree("books", backup_dir)
    
    # Migrate each book
    migrated = 0
    errors = []
    
    for old_path in track(old_book_files, description="Migrating books"):
        try:
            # Get book name from filename
            book_name = old_path.stem
            
            # Create new directory structure
            new_book_dir = Path("books") / book_name
            new_book_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy YAML file as book.yaml
            new_yaml_path = new_book_dir / "book.yaml"
            shutil.copy2(old_path, new_yaml_path)
            
            # Create placeholder directories for assets
            (new_book_dir / "assets").mkdir(exist_ok=True)
            (new_book_dir / "audio").mkdir(exist_ok=True)
            
            # Check if cover exists in old structure
            old_cover = Path("assets/covers") / f"{book_name}.jpg"
            if not old_cover.exists():
                old_cover = Path("assets/covers") / f"{book_name}.png"
            
            if old_cover.exists():
                shutil.copy2(old_cover, new_book_dir / f"cover{old_cover.suffix}")
                console.print(f"[green]Copied cover for {book_name}[/green]")
            
            migrated += 1
            
        except Exception as e:
            errors.append((old_path, str(e)))
            console.print(f"[red]Error migrating {old_path}: {e}[/red]")
    
    # Clean up old structure
    console.print("\n[yellow]Cleaning up old directory structure...[/yellow]")
    for letter_dir in Path("books").iterdir():
        if letter_dir.is_dir() and len(letter_dir.name) == 1:
            shutil.rmtree(letter_dir)
    
    # Report results
    console.print(f"\n[bold green]Migration complete![/bold green]")
    console.print(f"✅ Successfully migrated: {migrated} books")
    if errors:
        console.print(f"❌ Errors: {len(errors)}")
        for path, error in errors:
            console.print(f"  - {path}: {error}")
    
    console.print(f"\n[dim]Backup saved in: {backup_dir}[/dim]")


def create_shared_assets():
    """Create shared assets directory structure"""
    console.print("\n[cyan]Creating shared assets structure...[/cyan]")
    
    shared_dirs = [
        "shared_assets/fonts",
        "shared_assets/music",
        "shared_assets/templates",
        "shared_assets/backgrounds"
    ]
    
    for dir_path in shared_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Move existing shared assets
    if Path("assets/fonts").exists():
        for font in Path("assets/fonts").iterdir():
            shutil.copy2(font, Path("shared_assets/fonts") / font.name)
    
    # Move templates
    if Path("templates").exists():
        for template in Path("templates").iterdir():
            shutil.copy2(template, Path("shared_assets/templates") / template.name)
    
    console.print("[green]Shared assets structure created[/green]")


def update_series_files():
    """Update series YAML files with new paths"""
    console.print("\n[cyan]Updating series files...[/cyan]")
    
    series_files = list(Path("content").glob("*.yaml"))
    
    for series_file in series_files:
        try:
            with open(series_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Update book paths
            if 'books' in data:
                for book in data['books']:
                    old_path = book['path']
                    # Extract book name from old path
                    book_name = Path(old_path).stem
                    book['path'] = f"books/{book_name}/book.yaml"
            
            # Save updated file
            with open(series_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            
            console.print(f"[green]Updated {series_file.name}[/green]")
            
        except Exception as e:
            console.print(f"[red]Error updating {series_file}: {e}[/red]")


def main():
    """Run the migration"""
    console.print("[bold]Book Structure Migration Tool[/bold]\n")
    
    # Confirm with user
    console.print("This will reorganize the book structure from:")
    console.print("  [dim]books/[a-z]/[a-z]/book_name.yaml[/dim]")
    console.print("To:")
    console.print("  [green]books/book_name/book.yaml[/green]")
    console.print("\nA backup will be created before migration.")
    
    response = console.input("\nProceed with migration? [y/N]: ")
    if response.lower() != 'y':
        console.print("[yellow]Migration cancelled[/yellow]")
        return
    
    # Run migration steps
    migrate_books()
    create_shared_assets()
    update_series_files()
    
    console.print("\n[bold green]✨ Migration completed successfully![/bold green]")
    console.print("\nNext steps:")
    console.print("1. Test the new structure with: python main.py list")
    console.print("2. Update code to use new paths")
    console.print("3. Remove backup when everything works: rm -rf books_backup")


if __name__ == "__main__":
    main()