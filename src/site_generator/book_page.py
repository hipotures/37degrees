"""
Book page HTML generator
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import json
from datetime import datetime

from .base import BaseHtmlGenerator


class BookPageGenerator(BaseHtmlGenerator):
    """Generate individual book pages from book.yaml files"""
    
    def generate(self, book_yaml_path: Path, output_filename: str = None) -> Path:
        """Generate HTML page for a book
        
        Args:
            book_yaml_path: Path to book.yaml file
            output_filename: Output filename (default: book_id.html)
            
        Returns:
            Path to generated HTML file
        """
        # Load book data
        with open(book_yaml_path, 'r', encoding='utf-8') as f:
            book_data = yaml.safe_load(f)
        
        book_info = book_data.get('book_info', {})
        book_dir = book_yaml_path.parent
        book_id = book_dir.name
        
        # Determine output filename
        if not output_filename:
            output_filename = f"{book_id}.html"
        
        # Load additional data from docs
        review_path = book_dir / 'docs' / 'review.md'
        readme_path = book_dir / 'docs' / 'README.md'
        
        # Prepare template context
        context = self._prepare_context(book_data, review_path, readme_path)
        
        # Load and customize template
        template_content = self._load_template()
        html_content = self._render_book_page(template_content, context)
        
        # Save HTML file
        output_path = self.output_dir / 'books' / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _load_template(self) -> str:
        """Load the book page template"""
        template_path = self.templates_dir / 'book_page_template.html'
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _prepare_context(self, book_data: Dict[str, Any], 
                        review_path: Path, readme_path: Path) -> Dict[str, Any]:
        """Prepare template context from book data
        
        Args:
            book_data: Book YAML data
            review_path: Path to review.md
            readme_path: Path to README.md
            
        Returns:
            Template context dictionary
        """
        book_info = book_data.get('book_info', {})
        
        # Basic book information
        context = {
            'BOOK_TITLE': book_info.get('title', 'Nieznany tytuł'),
            'BOOK_TITLE_GENITIVE': self._get_genitive_form(book_info.get('title', '')),
            'BOOK_EMOJI': book_info.get('emoji', '📚'),
            'AUTHOR_NAME': book_info.get('author', 'Nieznany autor'),
            'AUTHOR_EMOJI': '✍️',
            'HERO_DESCRIPTION': self._get_hero_description(book_info),
            'AUTHOR_DESCRIPTION': self._get_author_description(book_info),
            'SYMBOLS_DESCRIPTION': self._get_symbols_description(book_data)
        }
        
        # Add data from review.md if available
        if review_path.exists():
            review_data = self._parse_review(review_path)
            context.update(review_data)
        
        # Add timeline data
        context['timeline_data'] = json.dumps(self._get_timeline_data(book_info), ensure_ascii=False)
        
        # Add character/symbol data
        context['character_data'] = json.dumps(self._get_character_data(book_data), ensure_ascii=False)
        
        # Add statistics
        context['statistics_data'] = json.dumps(self._get_statistics_data(book_info), ensure_ascii=False)
        
        # Add adaptations
        context['adaptations_data'] = json.dumps(self._get_adaptations_data(review_path), ensure_ascii=False)
        
        return context
    
    def _render_book_page(self, template: str, context: Dict[str, Any]) -> str:
        """Render book page with context
        
        Args:
            template: Template HTML content
            context: Template context
            
        Returns:
            Rendered HTML
        """
        html = template
        
        # Replace placeholders
        for key, value in context.items():
            placeholder = f"[{key}]"
            if placeholder in html:
                html = html.replace(placeholder, str(value))
        
        # Update JavaScript data
        html = html.replace("const timelineData = [", f"const timelineData = {context.get('timeline_data', '[]')}")
        html = html.replace("const characterData = [", f"const characterData = {context.get('character_data', '[]')}")
        
        # Add navigation links
        html = self._add_navigation(html)
        
        return html
    
    def _get_genitive_form(self, title: str) -> str:
        """Get genitive form of book title (Polish grammar)
        
        Args:
            title: Book title
            
        Returns:
            Genitive form
        """
        # Simple heuristic for Polish genitive
        if title.endswith('a'):
            return title[:-1] + 'y'
        elif title.endswith('e'):
            return title[:-1] + 'ego'
        else:
            return title + 'a'
    
    def _get_hero_description(self, book_info: Dict[str, Any]) -> str:
        """Generate hero section description"""
        genre = book_info.get('genre', 'klasyka')
        year = book_info.get('year', 'nieznany')
        
        return (f"Wyrusz w interaktywną podróż, aby odkryć tajemnice i ponadczasową mądrość "
                f"tego klasycznego dzieła {genre} z {year} roku.")
    
    def _get_author_description(self, book_info: Dict[str, Any]) -> str:
        """Generate author description"""
        author = book_info.get('author', 'Nieznany autor')
        return f"{author} - twórca niezapomnianego dzieła, które wciąż inspiruje kolejne pokolenia."
    
    def _get_symbols_description(self, book_data: Dict[str, Any]) -> str:
        """Generate symbols section description"""
        return "Odkryj kluczowe symbole i postacie, które kształtują przesłanie książki."
    
    def _get_timeline_data(self, book_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate timeline data for author"""
        # Basic timeline - can be enhanced with real data
        timeline = []
        
        year = book_info.get('year')
        if year:
            timeline.append({
                'year': str(year),
                'event': f"Publikacja '{book_info.get('title', 'książki')}'"
            })
        
        return timeline
    
    def _get_character_data(self, book_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract character/symbol data from book slides"""
        characters = []
        colors = ['bg-blue-200', 'bg-purple-200', 'bg-green-200', 'bg-yellow-200',
                  'bg-pink-200', 'bg-indigo-200', 'bg-red-200', 'bg-gray-200']
        
        # Extract key themes from slides
        slides = book_data.get('slides', [])
        for i, slide in enumerate(slides[:8]):  # Limit to 8 main themes
            if slide.get('text'):
                characters.append({
                    'id': f'theme_{i+1}',
                    'name': f'Temat {i+1}',
                    'emoji': slide.get('emoji', '📖'),
                    'color': colors[i % len(colors)],
                    'description': slide['text'][:200] + '...' if len(slide['text']) > 200 else slide['text']
                })
        
        return characters
    
    def _get_statistics_data(self, book_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate statistics data"""
        return {
            'translations': 100,  # Placeholder
            'sold_copies_millions': 10,  # Placeholder
            'countries': ['Polska', 'Francja', 'USA', 'Niemcy', 'Włochy']
        }
    
    def _get_adaptations_data(self, review_path: Path) -> List[Dict[str, str]]:
        """Extract adaptations from review.md if available"""
        adaptations = []
        
        if review_path.exists():
            with open(review_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for adaptations section
            if '## 🎬 Adaptacje' in content:
                # Simple extraction - can be enhanced
                adaptations.append({
                    'type': 'Film',
                    'title': 'Ekranizacja',
                    'description': 'Znana adaptacja filmowa tego dzieła.',
                    'image': 'placeholder'
                })
        
        return adaptations
    
    def _parse_review(self, review_path: Path) -> Dict[str, Any]:
        """Parse review.md for additional content"""
        with open(review_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract sections - simple parsing
        review_data = {}
        
        # Extract fascinating facts
        if '## 🎯 Fascynujące ciekawostki' in content:
            section = content.split('## 🎯 Fascynujące ciekawostki')[1]
            section = section.split('##')[0] if '##' in section else section
            # Extract first fact for hero description
            lines = [line.strip() for line in section.split('\n') if line.strip() and line.startswith('💡')]
            if lines:
                review_data['HERO_DESCRIPTION'] = lines[0].replace('💡', '').strip()
        
        return review_data
    
    def _add_navigation(self, html: str) -> str:
        """Add navigation menu items"""
        # Find navigation section and add items
        nav_items = [
            '<a href="#author" class="nav-link text-lg">Autor</a>',
            '<a href="#genesis" class="nav-link text-lg">Geneza</a>',
            '<a href="#symbols" class="nav-link text-lg">Symbole</a>',
            '<a href="#stats" class="nav-link text-lg">Statystyki</a>',
            '<a href="../index.html" class="nav-link text-lg">📚 Wszystkie książki</a>'
        ]
        
        nav_section = '<!-- Dodaj więcej linków według potrzeb -->'
        if nav_section in html:
            html = html.replace(nav_section, '\n'.join(nav_items))
        
        return html