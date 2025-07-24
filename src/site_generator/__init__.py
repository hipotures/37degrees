"""
Static HTML site generator for 37degrees book reviews
"""

from .book_page import BookPageGenerator
from .index_page import IndexPageGenerator
from .collection_page import CollectionPageGenerator
from .site_builder import SiteBuilder

__all__ = [
    'BookPageGenerator',
    'IndexPageGenerator', 
    'CollectionPageGenerator',
    'SiteBuilder'
]