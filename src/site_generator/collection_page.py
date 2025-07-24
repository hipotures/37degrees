"""
Collection page HTML generator
"""

from pathlib import Path
from typing import Dict, Any, List
import yaml

from .base import BaseHtmlGenerator


class CollectionPageGenerator(BaseHtmlGenerator):
    """Generate individual collection pages"""
    
    def generate(self, collection_file: Path) -> Path:
        """Generate HTML page for a collection
        
        Args:
            collection_file: Path to collection YAML file
            
        Returns:
            Path to generated HTML file
        """
        # Load collection data
        with open(collection_file, 'r', encoding='utf-8') as f:
            collection_data = yaml.safe_load(f)
        
        collection_id = collection_file.stem
        series_info = collection_data.get('series', {})
        
        # Load books in collection
        books = self._load_collection_books(collection_data)
        
        # Generate HTML
        html_content = self._generate_collection_html(collection_id, series_info, books)
        
        # Save to output
        output_path = self.output_dir / 'collections' / f'{collection_id}.html'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _load_collection_books(self, collection_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Load all books in a collection"""
        books = []
        
        for book_ref in collection_data.get('books', []):
            book_path = Path(book_ref['path'])
            if book_path.exists():
                with open(book_path, 'r', encoding='utf-8') as f:
                    book_data = yaml.safe_load(f)
                
                book_info = book_data.get('book_info', {})
                book_id = book_path.parent.name
                
                # Check if book page exists
                book_page = self.output_dir / 'books' / f'{book_id}.html'
                
                books.append({
                    'id': book_id,
                    'order': book_ref.get('order', 0),
                    'title': book_info.get('title', 'Nieznany tytuł'),
                    'author': book_info.get('author', 'Nieznany autor'),
                    'year': book_info.get('year', ''),
                    'genre': book_info.get('genre', 'klasyka'),
                    'emoji': book_info.get('emoji', '📚'),
                    'description': book_data.get('description', ''),
                    'page_exists': book_page.exists(),
                    'page_url': f'../books/{book_id}.html'
                })
        
        # Sort by order
        books.sort(key=lambda x: x['order'])
        
        return books
    
    def _generate_collection_html(self, collection_id: str, 
                                 series_info: Dict[str, Any], 
                                 books: List[Dict[str, Any]]) -> str:
        """Generate collection HTML page"""
        
        collection_name = series_info.get('name', collection_id.replace('_', ' ').title())
        description = series_info.get('description', '')
        
        html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{collection_name} - 37 Stopni</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Lora:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {{
            background: linear-gradient(135deg, #FDF6E3 0%, #FAF0D7 100%);
            color: #073642;
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
        }}
        h1, h2, h3 {{
            font-family: 'Lora', serif;
        }}
        .book-item {{
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
        }}
        .book-item:hover {{
            transform: translateX(10px);
            background: rgba(255, 255, 255, 0.9);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        .progress-bar {{
            background: linear-gradient(90deg, #268BD2 0%, #2AA198 100%);
        }}
    </style>
</head>
<body class="antialiased">
    <!-- HEADER -->
    <header class="bg-white/80 backdrop-blur-md sticky top-0 z-50 shadow-lg">
        <nav class="container mx-auto px-6 py-4">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <a href="../index.html" class="text-2xl hover:text-[#268BD2] transition-colors">
                        ← Powrót
                    </a>
                </div>
                <h1 class="text-xl font-bold text-[#073642]">{collection_name}</h1>
                <div class="text-sm text-gray-600">
                    {len(books)} książek
                </div>
            </div>
        </nav>
    </header>

    <!-- HERO SECTION -->
    <section class="py-16 px-6">
        <div class="container mx-auto text-center">
            <h1 class="text-5xl md:text-6xl font-bold mb-6 text-[#268BD2]">
                {collection_name}
            </h1>
            <p class="text-xl text-gray-700 max-w-3xl mx-auto mb-8">
                {description}
            </p>
            
            <!-- Progress stats -->
            <div class="max-w-2xl mx-auto bg-white/80 rounded-xl p-6 shadow-lg">
                <div class="grid grid-cols-3 gap-4 text-center">
                    <div>
                        <span class="text-3xl font-bold text-[#268BD2]">{len(books)}</span>
                        <p class="text-sm text-gray-600">Książek w kolekcji</p>
                    </div>
                    <div>
                        <span class="text-3xl font-bold text-[#2AA198]">{len([b for b in books if b['page_exists']])}</span>
                        <p class="text-sm text-gray-600">Dostępnych stron</p>
                    </div>
                    <div>
                        <span class="text-3xl font-bold text-[#CB4B16]">{len(set(b['author'] for b in books))}</span>
                        <p class="text-sm text-gray-600">Autorów</p>
                    </div>
                </div>
                
                <!-- Progress bar -->
                <div class="mt-6">
                    <div class="flex justify-between text-sm text-gray-600 mb-2">
                        <span>Postęp digitalizacji</span>
                        <span>{int(len([b for b in books if b['page_exists']]) / len(books) * 100)}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-3">
                        <div class="progress-bar h-3 rounded-full" 
                             style="width: {int(len([b for b in books if b['page_exists']]) / len(books) * 100)}%">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- BOOKS LIST -->
    <main class="container mx-auto px-6 py-12">
        <div class="max-w-4xl mx-auto">
            <h2 class="text-3xl font-bold mb-8 text-[#073642]">Książki w kolekcji</h2>
            
            <div class="space-y-4">
"""
        
        # Add each book
        for book in books:
            availability = "Dostępna" if book['page_exists'] else "Wkrótce"
            availability_color = "text-green-600" if book['page_exists'] else "text-gray-400"
            
            if book['page_exists']:
                html += f"""
                <a href="{book['page_url']}" class="book-item block rounded-xl p-6 hover:no-underline">
"""
            else:
                html += f"""
                <div class="book-item rounded-xl p-6 opacity-75">
"""
            
            html += f"""
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-4">
                            <span class="text-4xl">{book['emoji']}</span>
                            <div>
                                <h3 class="font-bold text-lg text-[#073642]">
                                    #{book['order']:02d} - {book['title']}
                                </h3>
                                <p class="text-sm text-gray-600">
                                    {book['author']} • {book['year']} • {book['genre']}
                                </p>
                            </div>
                        </div>
                        <div class="text-right">
                            <span class="{availability_color} text-sm font-semibold">
                                {availability}
                            </span>
                        </div>
                    </div>
"""
            
            if book['page_exists']:
                html += """
                </a>
"""
            else:
                html += """
                </div>
"""
        
        html += """
            </div>
        </div>
    </main>

    <!-- FOOTER -->
    <footer class="bg-[#073642] text-white py-8 mt-16">
        <div class="container mx-auto px-6 text-center">
            <p>© 2025 37 Stopni. Wszystkie prawa zastrzeżone.</p>
        </div>
    </footer>

    <script>
        // Animation on load
        document.addEventListener('DOMContentLoaded', () => {
            const books = document.querySelectorAll('.book-item');
            books.forEach((book, index) => {
                book.style.opacity = '0';
                book.style.transform = 'translateX(-20px)';
                setTimeout(() => {
                    book.style.transition = 'all 0.5s ease';
                    book.style.opacity = '1';
                    book.style.transform = 'translateX(0)';
                }, index * 50);
            });
        });
    </script>
</body>
</html>
"""
        
        return html