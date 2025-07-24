"""
Index page HTML generator with collection organization
"""

from pathlib import Path
from typing import Dict, Any, List
import yaml

from .base import BaseHtmlGenerator


class IndexPageGenerator(BaseHtmlGenerator):
    """Generate main index.html page with all books organized by collections"""
    
    def generate(self) -> Path:
        """Generate index.html with all books
        
        Returns:
            Path to generated index.html
        """
        # Load all collections
        collections = self._load_collections()
        
        # Generate HTML
        html_content = self._generate_index_html(collections)
        
        # Save to output
        output_path = self.output_dir / 'index.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Copy assets
        self.copy_assets()
        
        return output_path
    
    def _load_collections(self) -> List[Dict[str, Any]]:
        """Load all collections and their books"""
        collections_dir = Path('collections')
        collections = []
        
        if collections_dir.exists():
            for collection_file in collections_dir.glob('*.yaml'):
                with open(collection_file, 'r', encoding='utf-8') as f:
                    collection_data = yaml.safe_load(f)
                
                # Load book details
                books = []
                for book_ref in collection_data.get('books', []):
                    book_path = Path(book_ref['path'])
                    if book_path.exists():
                        with open(book_path, 'r', encoding='utf-8') as f:
                            book_data = yaml.safe_load(f)
                        
                        book_info = book_data.get('book_info', {})
                        book_id = book_path.parent.name
                        
                        books.append({
                            'id': book_id,
                            'order': book_ref.get('order', 0),
                            'title': book_info.get('title', 'Nieznany tytuł'),
                            'author': book_info.get('author', 'Nieznany autor'),
                            'year': book_info.get('year', ''),
                            'genre': book_info.get('genre', 'klasyka'),
                            'emoji': book_info.get('emoji', '📚'),
                            'page_url': f'books/{book_id}.html'
                        })
                
                # Sort books by order
                books.sort(key=lambda x: x['order'])
                
                collections.append({
                    'id': collection_file.stem,
                    'name': collection_data.get('series', {}).get('name', collection_file.stem),
                    'description': collection_data.get('series', {}).get('description', ''),
                    'books': books
                })
        
        return collections
    
    def _generate_index_html(self, collections: List[Dict[str, Any]]) -> str:
        """Generate the index HTML page"""
        html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>37 Stopni - Interaktywna Biblioteka Klasyki</title>
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
        .book-card {{
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
        }}
        .book-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            background: rgba(255, 255, 255, 0.9);
        }}
        .collection-header {{
            background: linear-gradient(90deg, #268BD2 0%, #2AA198 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .hero-pattern {{
            background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23268BD2' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        }}
    </style>
</head>
<body class="antialiased">
    <!-- HEADER -->
    <header class="bg-white/80 backdrop-blur-md sticky top-0 z-50 shadow-lg">
        <nav class="container mx-auto px-6 py-4">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <span class="text-3xl">🌡️</span>
                    <div>
                        <h1 class="text-2xl font-bold text-[#073642]">37 Stopni</h1>
                        <p class="text-sm text-gray-600">Gorączka czytania</p>
                    </div>
                </div>
                <div class="flex items-center space-x-6">
                    <a href="#about" class="text-gray-700 hover:text-[#268BD2] transition-colors">O projekcie</a>
                    <a href="#collections" class="text-gray-700 hover:text-[#268BD2] transition-colors">Kolekcje</a>
                    <a href="#contact" class="text-gray-700 hover:text-[#268BD2] transition-colors">Kontakt</a>
                </div>
            </div>
        </nav>
    </header>

    <!-- HERO SECTION -->
    <section class="hero-pattern py-20">
        <div class="container mx-auto px-6 text-center">
            <h2 class="text-5xl md:text-6xl font-bold mb-6 collection-header">
                Interaktywna Biblioteka Klasyki
            </h2>
            <p class="text-xl text-gray-700 max-w-3xl mx-auto mb-8">
                Odkryj klasyczne dzieła literatury światowej w nowoczesnej, interaktywnej formie.
                Każda książka to osobna podróż pełna fascynujących odkryć i niespodzianek.
            </p>
            <div class="flex justify-center space-x-4">
                <span class="bg-white/80 px-4 py-2 rounded-full text-sm font-semibold">
                    📚 {sum(len(col['books']) for col in collections)} książek
                </span>
                <span class="bg-white/80 px-4 py-2 rounded-full text-sm font-semibold">
                    🎬 {len(collections)} kolekcji
                </span>
                <span class="bg-white/80 px-4 py-2 rounded-full text-sm font-semibold">
                    🌍 Literatura światowa
                </span>
            </div>
        </div>
    </section>

    <!-- COLLECTIONS -->
    <main id="collections" class="container mx-auto px-6 py-12">
"""
        
        # Add each collection
        for collection in collections:
            html += f"""
        <section class="mb-16">
            <h3 class="text-3xl font-bold mb-2 text-[#268BD2]">{collection['name']}</h3>
            <p class="text-gray-600 mb-8">{collection['description']}</p>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
"""
            
            # Add books in collection
            for book in collection['books']:
                html += f"""
                <a href="{book['page_url']}" class="book-card rounded-xl p-6 block hover:no-underline">
                    <div class="text-center mb-4">
                        <span class="text-6xl block mb-3">{book['emoji']}</span>
                        <span class="inline-block bg-[#268BD2]/10 text-[#268BD2] text-xs px-2 py-1 rounded-full">
                            #{book['order']:02d}
                        </span>
                    </div>
                    <h4 class="font-bold text-lg mb-1 text-[#073642]">{book['title']}</h4>
                    <p class="text-sm text-gray-600 mb-2">{book['author']}</p>
                    <div class="flex justify-between text-xs text-gray-500">
                        <span>{book['genre']}</span>
                        <span>{book['year']}</span>
                    </div>
                </a>
"""
            
            html += """
            </div>
        </section>
"""
        
        # Footer
        html += """
    </main>

    <!-- ABOUT SECTION -->
    <section id="about" class="bg-white/80 py-16">
        <div class="container mx-auto px-6">
            <h3 class="text-3xl font-bold mb-8 text-center text-[#268BD2]">O projekcie</h3>
            <div class="max-w-4xl mx-auto text-lg text-gray-700 space-y-4">
                <p>
                    <strong>37 Stopni</strong> to innowacyjny projekt edukacyjny, który łączy klasyczną literaturę
                    z nowoczesnymi technologiami. Każda książka została przeprojektowana jako interaktywne doświadczenie,
                    które angażuje młodych czytelników i pomaga im odkryć bogactwo literatury światowej.
                </p>
                <p>
                    Nazwa projektu nawiązuje do "gorączki czytania" - pasji, która rozpala umysły i serca
                    kolejnych pokoleń czytelników. Poprzez krótkie, dynamiczne materiały wideo na TikToku
                    zachęcamy młodzież do sięgnięcia po klasyczne dzieła.
                </p>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                    <div class="text-center">
                        <span class="text-4xl mb-2 block">🎯</span>
                        <h4 class="font-bold mb-1">Cel</h4>
                        <p class="text-sm">Przybliżenie klasyki młodemu pokoleniu</p>
                    </div>
                    <div class="text-center">
                        <span class="text-4xl mb-2 block">🎨</span>
                        <h4 class="font-bold mb-1">Forma</h4>
                        <p class="text-sm">Interaktywne strony i krótkie filmy</p>
                    </div>
                    <div class="text-center">
                        <span class="text-4xl mb-2 block">👥</span>
                        <h4 class="font-bold mb-1">Odbiorcy</h4>
                        <p class="text-sm">Młodzież w wieku 10-20 lat</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- FOOTER -->
    <footer id="contact" class="bg-[#073642] text-white py-12">
        <div class="container mx-auto px-6">
            <div class="text-center">
                <h3 class="text-2xl font-bold mb-4">Kontakt</h3>
                <p class="mb-6">Śledź nas na TikToku: <strong>@37stopni</strong></p>
                <div class="flex justify-center space-x-6 text-3xl">
                    <a href="#" class="hover:text-[#268BD2] transition-colors">📱</a>
                    <a href="#" class="hover:text-[#268BD2] transition-colors">📧</a>
                    <a href="#" class="hover:text-[#268BD2] transition-colors">🎬</a>
                </div>
                <p class="mt-8 text-sm text-gray-400">
                    © 2025 37 Stopni. Wszystkie prawa zastrzeżone.
                </p>
            </div>
        </div>
    </footer>

    <script>
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                }}
            }});
        }});

        // Add animation on scroll
        const observerOptions = {{
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        }};

        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }}
            }});
        }}, observerOptions);

        // Observe all book cards
        document.querySelectorAll('.book-card').forEach(card => {{
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'all 0.6s ease';
            observer.observe(card);
        }});
    </script>
</body>
</html>
"""
        
        return html