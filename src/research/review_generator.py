"""
Review.md file generator using research providers
"""

from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .base import ResearchQuery, ResearchResponse
from .registry import registry

console = Console()


class ReviewGenerator:
    """Generate review.md files for books using research APIs"""
    
    def __init__(self, provider_name: str = None):
        """Initialize review generator
        
        Args:
            provider_name: Name of research provider to use (default from config)
        """
        from src.config import get_config
        config = get_config()
        
        # Load research config
        research_config = config.get_section('services').get('research', {})
        self.provider_name = provider_name or research_config.get('default', 'mock')
        
        # Initialize provider from config
        provider_configs = research_config.get('providers', {})
        registry.load_config(provider_configs)
        
        try:
            self.provider = registry.get_provider(self.provider_name)
        except Exception as e:
            console.print(f"[red]Failed to initialize provider '{self.provider_name}': {e}[/red]")
            console.print("[yellow]Falling back to mock provider[/yellow]")
            self.provider = registry.get_provider('mock')
    
    def generate_review(self, book_yaml_path: Path, output_path: Optional[Path] = None) -> bool:
        """Generate review.md for a book
        
        Args:
            book_yaml_path: Path to book.yaml file
            output_path: Optional output path (default: book_dir/docs/review.md)
            
        Returns:
            bool: True if successful
        """
        import yaml
        
        # Load book data
        try:
            with open(book_yaml_path, 'r', encoding='utf-8') as f:
                book_data = yaml.safe_load(f)
        except Exception as e:
            console.print(f"[red]Failed to load book data: {e}[/red]")
            return False
        
        book_info = book_data.get('book_info', {})
        book_title = book_info.get('title', 'Unknown')
        author = book_info.get('author', 'Unknown')
        
        # Determine output path
        if not output_path:
            book_dir = book_yaml_path.parent
            docs_dir = book_dir / 'docs'
            docs_dir.mkdir(exist_ok=True)
            output_path = docs_dir / 'review.md'
        
        console.print(f"\n[bold cyan]Generating review for: {book_title}[/bold cyan]")
        console.print(f"Author: {author}")
        console.print(f"Provider: {self.provider_name}")
        
        # Check if provider is available
        if not self.provider.test_connection():
            console.print(f"[red]Provider '{self.provider_name}' is not available[/red]")
            return False
        
        # Perform research
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Researching book...", total=None)
                
                response = self.provider.research_book(
                    book_title=book_title,
                    author=author,
                    language='pl'
                )
                
                progress.update(task, completed=True)
            
            # Format and save review
            review_content = self._format_review(response, book_data)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(review_content)
            
            console.print(f"[green]✓ Review saved to: {output_path}[/green]")
            console.print(f"[dim]Found {len(response.results)} research results[/dim]")
            
            return True
            
        except Exception as e:
            console.print(f"[red]Failed to generate review: {e}[/red]")
            return False
    
    def _format_review(self, response: ResearchResponse, book_data: Dict[str, Any]) -> str:
        """Format research response into review.md content
        
        Args:
            response: Research response
            book_data: Book YAML data
            
        Returns:
            Formatted markdown content
        """
        book_info = book_data.get('book_info', {})
        
        # Start with header
        lines = [
            f"# {book_info.get('title', 'Unknown')} - Fascynujące fakty i odkrycia",
            "",
            f"**Autor:** {book_info.get('author', 'Unknown')}  ",
            f"**Rok wydania:** {book_info.get('year', 'Nieznany')}  ",
            f"**Gatunek:** {book_info.get('genre', 'Klasyka')}  ",
            "",
            f"*Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M')} przez {response.provider}*",
            "",
            "---",
            ""
        ]
        
        # Add emoji if available
        if 'emoji' in book_info:
            lines.insert(1, f"{book_info['emoji']}")
            lines.insert(2, "")
        
        # Group results by topic
        sections = {
            "ciekawostki": {
                "title": "## 🎯 Fascynujące ciekawostki",
                "icon": "💡",
                "results": []
            },
            "symbolika": {
                "title": "## 🔮 Symbolika i znaczenia",
                "icon": "🎭",
                "results": []
            },
            "kontekst historyczny": {
                "title": "## 📜 Kontekst historyczny",
                "icon": "🏛️",
                "results": []
            },
            "adaptacje": {
                "title": "## 🎬 Adaptacje i inspiracje",
                "icon": "🎥",
                "results": []
            },
            "cytaty": {
                "title": "## 💬 Najsłynniejsze cytaty",
                "icon": "📝",
                "results": []
            },
            "wpływ kulturowy": {
                "title": "## 🌍 Wpływ na kulturę",
                "icon": "🌟",
                "results": []
            }
        }
        
        # Categorize results
        for result in response.results:
            topic = result.metadata.get('topic', '')
            if topic in sections:
                sections[topic]['results'].append(result)
        
        # Format each section
        for topic, section in sections.items():
            if section['results']:
                lines.append(section['title'])
                lines.append("")
                
                for i, result in enumerate(section['results'][:3], 1):
                    # Format content
                    content = result.content.strip()
                    
                    # Split into paragraphs if long
                    paragraphs = content.split('\n\n')
                    for para in paragraphs:
                        if para.strip():
                            lines.append(f"{section['icon']} {para.strip()}")
                            lines.append("")
                    
                    # Add source if URL available
                    if result.url:
                        lines.append(f"*[Źródło]({result.url})*")
                        lines.append("")
                
                lines.append("---")
                lines.append("")
        
        # Add metadata section
        lines.extend([
            "## 📊 Informacje o wyszukiwaniu",
            "",
            f"- **Dostawca:** {response.provider}",
            f"- **Liczba wyników:** {response.total_results}",
            f"- **Data wyszukiwania:** {response.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
        ])
        
        if response.metadata:
            lines.append("- **Metadane:**")
            for key, value in response.metadata.items():
                lines.append(f"  - {key}: {value}")
        
        lines.extend([
            "",
            "---",
            "",
            "*Ten dokument został wygenerowany automatycznie przez system 37degrees.*"
        ])
        
        return "\n".join(lines)