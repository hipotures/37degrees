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
from .citation_db import CitationDatabase

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
        
        # Initialize citation database
        citation_db = CitationDatabase(book_yaml_path)
        
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
            
            # Create research session
            topics = list(set(result.metadata.get('topic', '') for result in response.results if result.metadata))
            session_id = citation_db.create_research_session(
                provider=self.provider_name,
                book_title=book_title,
                author=author,
                topics=topics,
                metadata={'model': response.metadata.get('model', 'unknown')}
            )
            
            # Process and save citations
            citation_map = self._process_citations(response, citation_db, session_id)
            
            # Format and save review with citation IDs
            review_content = self._format_review_with_citations(response, book_data, citation_map, citation_db)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(review_content)
            
            console.print(f"[green]✓ Review saved to: {output_path}[/green]")
            console.print(f"[dim]Found {len(response.results)} research results[/dim]")
            console.print(f"[dim]Saved {len(citation_map)} unique citations to database[/dim]")
            
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
        
        # Add citations if available
        all_citations = []
        all_search_results = []
        
        for result in response.results:
            if result.metadata:
                citations = result.metadata.get('citations', [])
                search_results = result.metadata.get('search_results', [])
                if citations:
                    all_citations.extend(citations)
                if search_results:
                    all_search_results.extend(search_results)
        
        if all_citations:
            lines.append("\n### 🔗 Źródła cytowane:")
            for i, citation in enumerate(set(all_citations), 1):
                lines.append(f"{i}. {citation}")
        
        if all_search_results:
            lines.append("\n### 🌐 Wyniki wyszukiwania:")
            for result in all_search_results[:5]:  # Show first 5
                lines.append(f"- [{result.get('title', 'Link')}]({result.get('url', '#')})")
        
        if response.metadata:
            lines.append("\n- **Metadane:**")
            for key, value in response.metadata.items():
                if key not in ['citations', 'search_results']:  # Skip these as we show them above
                    lines.append(f"  - {key}: {value}")
        
        lines.extend([
            "",
            "---",
            "",
            "*Ten dokument został wygenerowany automatycznie przez system 37degrees.*"
        ])
        
        return "\n".join(lines)
    
    def _process_citations(self, response: ResearchResponse, citation_db: CitationDatabase, 
                          session_id: int) -> Dict[str, int]:
        """Process all citations from response and save to database
        
        Returns:
            Dictionary mapping URL to citation ID
        """
        citation_map = {}
        citation_count = 0
        
        # Process all results
        for result in response.results:
            if not result.metadata:
                continue
                
            topic = result.metadata.get('topic', 'general')
            
            # Process direct citations
            citations = result.metadata.get('citations', [])
            for url in citations:
                if url not in citation_map:
                    citation_id = citation_db.add_citation(
                        url=url,
                        provider=self.provider_name,
                        topic=topic,
                        relevance_score=0.9
                    )
                    citation_map[url] = citation_id
                    citation_count += 1
            
            # Process search results
            search_results = result.metadata.get('search_results', [])
            for sr in search_results:
                url = sr.get('url')
                if url and url not in citation_map:
                    citation_id = citation_db.add_citation(
                        url=url,
                        title=sr.get('title'),
                        date=sr.get('date'),
                        last_updated=sr.get('last_updated'),
                        provider=self.provider_name,
                        topic=topic,
                        relevance_score=0.8
                    )
                    citation_map[url] = citation_id
                    citation_count += 1
        
        # Update session with total citations
        citation_db.update_session_citations(session_id, citation_count)
        
        return citation_map
    
    def _format_review_with_citations(self, response: ResearchResponse, book_data: Dict[str, Any],
                                     citation_map: Dict[str, int], citation_db: CitationDatabase) -> str:
        """Format review with citation IDs instead of URLs
        
        Args:
            response: Research response
            book_data: Book YAML data
            citation_map: Map of URL to citation ID
            citation_db: Citation database instance
            
        Returns:
            Formatted markdown content with [url=ID] citations
        """
        # First format the regular review
        review_content = self._format_review(response, book_data)
        
        # Replace all URLs with [url=ID] format
        for url, citation_id in citation_map.items():
            # Replace various markdown link formats
            # [text](url) -> text [url=ID]
            review_content = review_content.replace(f"]({url})", f"] [url={citation_id}]")
            # Direct URL mentions
            review_content = review_content.replace(f" {url} ", f" [url={citation_id}] ")
            review_content = review_content.replace(f" {url}.", f" [url={citation_id}].")
            review_content = review_content.replace(f" {url},", f" [url={citation_id}],")
        
        # Remove the old citation sections (we'll add a new one)
        lines = review_content.split('\n')
        new_lines = []
        skip_section = False
        
        for line in lines:
            if line.startswith("### 🔗 Źródła cytowane:") or line.startswith("### 🌐 Wyniki wyszukiwania:"):
                skip_section = True
                continue
            elif skip_section and (line.startswith("###") or line.startswith("##") or line.strip() == "---"):
                skip_section = False
            
            if not skip_section:
                new_lines.append(line)
        
        # Add bibliography section with all citations
        bibliography_lines = [
            "",
            "### 📚 Bibliografia",
            ""
        ]
        
        # Get all citations used
        all_citations = citation_db.get_all_citations()
        for citation in all_citations:
            title = citation['title'] or citation['domain'] or "Link"
            date_str = f" ({citation['date']})" if citation['date'] else ""
            bibliography_lines.append(f"[{citation['id']}] {citation['url']} - \"{title}\"{date_str}")
        
        # Find where to insert bibliography (before the metadata section)
        insert_index = -1
        for i, line in enumerate(new_lines):
            if "## 📊 Informacje o wyszukiwaniu" in line:
                insert_index = i
                break
        
        if insert_index > 0:
            new_lines = new_lines[:insert_index] + bibliography_lines + [""] + new_lines[insert_index:]
        else:
            # If metadata section not found, add at the end
            new_lines.extend(bibliography_lines)
        
        return '\n'.join(new_lines)