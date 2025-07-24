"""
Base class for research providers
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json
import hashlib
from rich.console import Console

console = Console()


class ResearchError(Exception):
    """Base exception for research errors"""
    pass


class ResearchAPIError(ResearchError):
    """API-related errors"""
    pass


class ResearchLimitError(ResearchError):
    """Rate limit or quota errors"""
    pass


@dataclass
class ResearchQuery:
    """Research query parameters"""
    book_title: str
    author: str
    language: str = "pl"  # Polish by default
    topics: List[str] = None
    max_results: int = 10
    
    def __post_init__(self):
        if self.topics is None:
            self.topics = [
                "ciekawostki",  # interesting facts
                "symbolika",    # symbolism
                "kontekst historyczny",  # historical context
                "adaptacje",    # adaptations
                "cytaty",       # quotes
                "wpływ kulturowy"  # cultural impact
            ]


@dataclass
class ResearchResult:
    """Single research result"""
    title: str
    content: str
    source: str
    url: Optional[str] = None
    date: Optional[datetime] = None
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ResearchResponse:
    """Complete research response"""
    query: ResearchQuery
    results: List[ResearchResult]
    provider: str
    timestamp: datetime
    total_results: int
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'query': {
                'book_title': self.query.book_title,
                'author': self.query.author,
                'language': self.query.language,
                'topics': self.query.topics,
                'max_results': self.query.max_results
            },
            'results': [
                {
                    'title': r.title,
                    'content': r.content,
                    'source': r.source,
                    'url': r.url,
                    'date': r.date.isoformat() if r.date else None,
                    'relevance_score': r.relevance_score,
                    'metadata': r.metadata
                }
                for r in self.results
            ],
            'provider': self.provider,
            'timestamp': self.timestamp.isoformat(),
            'total_results': self.total_results,
            'metadata': self.metadata
        }


class BaseResearchProvider(ABC):
    """Abstract base class for research providers"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize research provider
        
        Args:
            config: Provider-specific configuration
        """
        self.config = config
        self.name = self.__class__.__name__
        self.cache_enabled = config.get('cache_enabled', True)
        self.cache_ttl = config.get('cache_ttl', 900)  # 15 minutes default
        self.cache_dir = Path(config.get('cache_dir', '.cache/research'))
        
        if self.cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def search(self, query: ResearchQuery) -> ResearchResponse:
        """Perform research based on query
        
        Args:
            query: Research query parameters
            
        Returns:
            ResearchResponse with results
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the provider is accessible
        
        Returns:
            bool: True if connection successful
        """
        pass
    
    def research_book(self, book_title: str, author: str, **kwargs) -> ResearchResponse:
        """Convenience method for researching a book
        
        Args:
            book_title: Title of the book
            author: Author name
            **kwargs: Additional query parameters
            
        Returns:
            ResearchResponse with results
        """
        query = ResearchQuery(
            book_title=book_title,
            author=author,
            **kwargs
        )
        
        # Check cache first
        if self.cache_enabled:
            cached = self._get_cached_response(query)
            if cached:
                console.print(f"[green]Using cached research for {book_title}[/green]")
                return cached
        
        # Perform search
        console.print(f"[yellow]Researching {book_title} by {author}...[/yellow]")
        response = self.search(query)
        
        # Cache response
        if self.cache_enabled:
            self._cache_response(query, response)
        
        return response
    
    def _get_cache_key(self, query: ResearchQuery) -> str:
        """Generate cache key for query"""
        key_data = f"{query.book_title}:{query.author}:{query.language}:{','.join(query.topics)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_response(self, query: ResearchQuery) -> Optional[ResearchResponse]:
        """Get cached response if available and valid"""
        cache_key = self._get_cache_key(query)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            # Check if cache is still valid
            if (datetime.now().timestamp() - cache_file.stat().st_mtime) > self.cache_ttl:
                cache_file.unlink()  # Delete expired cache
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruct response
            response = ResearchResponse(
                query=query,
                results=[
                    ResearchResult(
                        title=r['title'],
                        content=r['content'],
                        source=r['source'],
                        url=r.get('url'),
                        date=datetime.fromisoformat(r['date']) if r.get('date') else None,
                        relevance_score=r.get('relevance_score', 0.0),
                        metadata=r.get('metadata', {})
                    )
                    for r in data['results']
                ],
                provider=data['provider'],
                timestamp=datetime.fromisoformat(data['timestamp']),
                total_results=data['total_results'],
                metadata=data.get('metadata', {})
            )
            
            return response
            
        except Exception as e:
            console.print(f"[red]Error loading cache: {e}[/red]")
            return None
    
    def _cache_response(self, query: ResearchQuery, response: ResearchResponse) -> None:
        """Cache response for future use"""
        cache_key = self._get_cache_key(query)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(response.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            console.print(f"[red]Error caching response: {e}[/red]")
    
    def format_for_review(self, response: ResearchResponse) -> str:
        """Format research results for review.md file
        
        Args:
            response: Research response to format
            
        Returns:
            Formatted markdown string
        """
        sections = {
            "ciekawostki": "## 🎯 Ciekawostki",
            "symbolika": "## 🔮 Symbolika",
            "kontekst historyczny": "## 📜 Kontekst historyczny",
            "adaptacje": "## 🎬 Adaptacje",
            "cytaty": "## 💬 Cytaty",
            "wpływ kulturowy": "## 🌍 Wpływ kulturowy"
        }
        
        # Group results by topic
        grouped = {}
        for result in response.results:
            # Try to match result to a topic based on content
            for topic in response.query.topics:
                if topic.lower() in result.title.lower() or topic.lower() in result.content.lower():
                    if topic not in grouped:
                        grouped[topic] = []
                    grouped[topic].append(result)
                    break
        
        # Build markdown
        lines = [
            f"# {response.query.book_title} - Fascynujące fakty i odkrycia",
            f"*Autor: {response.query.author}*",
            "",
            f"*Wygenerowano: {response.timestamp.strftime('%Y-%m-%d %H:%M')}*",
            "",
        ]
        
        for topic, section_title in sections.items():
            if topic in grouped and grouped[topic]:
                lines.append(section_title)
                lines.append("")
                
                for result in grouped[topic][:3]:  # Limit to 3 per section
                    lines.append(f"### {result.title}")
                    lines.append("")
                    lines.append(result.content)
                    if result.url:
                        lines.append(f"\n*Źródło: [{result.source}]({result.url})*")
                    else:
                        lines.append(f"\n*Źródło: {result.source}*")
                    lines.append("")
        
        # Add metadata
        lines.extend([
            "",
            "---",
            "",
            "## 📊 Informacje o wyszukiwaniu",
            "",
            f"- Provider: {response.provider}",
            f"- Liczba wyników: {response.total_results}",
            f"- Data wyszukiwania: {response.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
        ])
        
        return "\n".join(lines)
    
    def get_info(self) -> Dict[str, Any]:
        """Get provider information"""
        return {
            'name': self.name,
            'class': self.__class__.__name__,
            'config': self.config,
            'cache_enabled': self.cache_enabled,
            'cache_ttl': self.cache_ttl
        }
    
    def __str__(self) -> str:
        return f"{self.name}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} at {hex(id(self))}>"