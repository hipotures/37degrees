"""Utility functions for CLI modules"""

from pathlib import Path
import yaml
from typing import Tuple, Optional

def resolve_target(target: str) -> Tuple[str, str]:
    """
    Resolve target to determine if it's a book ID, book name, or collection
    Returns: (target_type, target_value)
    """
    # Check if it's a collection
    collection_file = Path(f"collections/{target}.yaml")
    if collection_file.exists():
        return ("collection", target)
    
    # Check if it's a book ID (numeric)
    if target.isdigit():
        return ("book_id", target)
    
    # Otherwise assume it's a book name
    return ("book_name", target)


def get_book_path(identifier: str) -> Optional[Path]:
    """
    Get book path from ID or name
    """
    books_dir = Path("books")
    
    # If it's a number, look for book by ID
    if identifier.isdigit():
        target_id = identifier.zfill(4)  # Pad with zeros
        for book_dir in books_dir.iterdir():
            if book_dir.is_dir() and book_dir.name.startswith(f"{target_id}_"):
                book_yaml = book_dir / "book.yaml"
                if book_yaml.exists():
                    return book_yaml
    
    # Try to find by name (partial match)
    identifier_lower = identifier.lower().replace('_', '').replace('-', '')
    for book_dir in books_dir.iterdir():
        if book_dir.is_dir():
            # Remove ID prefix and compare
            dir_name = book_dir.name
            if '_' in dir_name:
                book_name = dir_name.split('_', 1)[1]
            else:
                book_name = dir_name
            
            book_name_clean = book_name.lower().replace('_', '').replace('-', '')
            
            if identifier_lower in book_name_clean:
                book_yaml = book_dir / "book.yaml"
                if book_yaml.exists():
                    return book_yaml
    
    return None


def get_all_collections() -> list:
    """Get list of all collection names"""
    collections_dir = Path("collections")
    if not collections_dir.exists():
        return []
    
    return [f.stem for f in collections_dir.glob("*.yaml")]