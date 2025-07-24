"""
Google Custom Search API integration for research
"""

import os
import requests
from typing import Dict, List, Any
from datetime import datetime
from urllib.parse import quote
from rich.console import Console

from .base import (
    BaseResearchProvider, 
    ResearchQuery, 
    ResearchResponse, 
    ResearchResult,
    ResearchAPIError,
    ResearchLimitError
)

console = Console()


class GoogleSearchProvider(BaseResearchProvider):
    """Google Custom Search research provider"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Google Search provider
        
        Args:
            config: Configuration with:
                - api_key: Google API key (or use GOOGLE_API_KEY env)
                - cx: Custom Search Engine ID (or use GOOGLE_CX env)
                - daily_limit: Daily API limit (default: 100)
        """
        super().__init__(config)
        
        # Get credentials from config or environment
        self.api_key = config.get('api_key') or os.getenv('GOOGLE_API_KEY')
        self.cx = config.get('cx') or os.getenv('GOOGLE_CX')
        
        if not self.api_key or self.api_key == 'dummy_key_for_development':
            console.print("[yellow]Warning: Google API key not configured[/yellow]")
        if not self.cx or self.cx == 'dummy_cx_for_development':
            console.print("[yellow]Warning: Google Custom Search Engine ID not configured[/yellow]")
        
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.daily_limit = config.get('daily_limit', 100)
        self.queries_today = 0
    
    def test_connection(self) -> bool:
        """Test if Google Search API is accessible"""
        if not self.api_key or self.api_key == 'dummy_key_for_development':
            console.print("[red]Google API key not configured[/red]")
            return False
        if not self.cx or self.cx == 'dummy_cx_for_development':
            console.print("[red]Google Custom Search Engine ID not configured[/red]")
            return False
        
        try:
            # Test with minimal query
            response = requests.get(
                self.base_url,
                params={
                    'key': self.api_key,
                    'cx': self.cx,
                    'q': 'test',
                    'num': 1
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            console.print(f"[red]Connection test failed: {e}[/red]")
            return False
    
    def search(self, query: ResearchQuery) -> ResearchResponse:
        """Perform research using Google Search
        
        Args:
            query: Research query parameters
            
        Returns:
            ResearchResponse with results
        """
        if not self.api_key or self.api_key == 'dummy_key_for_development':
            raise ResearchAPIError("Google API key not configured")
        if not self.cx or self.cx == 'dummy_cx_for_development':
            raise ResearchAPIError("Google Custom Search Engine ID not configured")
        
        if self.queries_today >= self.daily_limit:
            raise ResearchLimitError(f"Google Search daily limit ({self.daily_limit}) reached")
        
        results = []
        
        # Search for each topic
        for topic in query.topics[:3]:  # Limit topics to conserve API quota
            search_query = self._build_search_query(query, topic)
            
            try:
                response = requests.get(
                    self.base_url,
                    params={
                        'key': self.api_key,
                        'cx': self.cx,
                        'q': search_query,
                        'num': 3,  # Results per query
                        'hl': query.language,  # Interface language
                        'lr': f'lang_{query.language}'  # Result language
                    },
                    timeout=10
                )
                
                self.queries_today += 1
                
                if response.status_code == 429:
                    raise ResearchLimitError("Google Search API rate limit reached")
                elif response.status_code != 200:
                    raise ResearchAPIError(f"Google Search API error: {response.status_code} - {response.text}")
                
                data = response.json()
                
                # Process search results
                for item in data.get('items', []):
                    result = ResearchResult(
                        title=item.get('title', ''),
                        content=item.get('snippet', ''),
                        source="Google Search",
                        url=item.get('link'),
                        date=None,  # Google doesn't provide dates in basic search
                        relevance_score=0.7,
                        metadata={
                            'topic': topic,
                            'display_link': item.get('displayLink', ''),
                            'mime': item.get('mime', 'text/html')
                        }
                    )
                    results.append(result)
                
                console.print(f"[green]✓ Searched {topic} for {query.book_title}[/green]")
                
            except requests.exceptions.Timeout:
                console.print(f"[yellow]Timeout searching {topic}[/yellow]")
            except (ResearchAPIError, ResearchLimitError):
                raise
            except Exception as e:
                console.print(f"[red]Error searching {topic}: {e}[/red]")
        
        return ResearchResponse(
            query=query,
            results=results,
            provider="Google Search",
            timestamp=datetime.now(),
            total_results=len(results),
            metadata={
                'queries_used': self.queries_today,
                'daily_limit': self.daily_limit
            }
        )
    
    def _build_search_query(self, query: ResearchQuery, topic: str) -> str:
        """Build search query for specific topic"""
        
        # Base query with book and author
        base = f'"{query.book_title}" {query.author}'
        
        # Topic-specific additions
        topic_queries = {
            "ciekawostki": f'{base} ciekawostki "mało znane fakty" historia',
            "symbolika": f'{base} symbolika symbole interpretacja znaczenie',
            "kontekst historyczny": f'{base} "kontekst historyczny" epoka tło historia',
            "adaptacje": f'{base} film serial adaptacja teatr ekranizacja',
            "cytaty": f'{base} "najsłynniejsze cytaty" "znane cytaty" aforyzmy',
            "wpływ kulturowy": f'{base} "wpływ na kulturę" znaczenie oddziaływanie popkultura'
        }
        
        # Add language-specific terms if not Polish
        if query.language != 'pl':
            return f'{topic_queries.get(topic, base)} site:.{query.language}'
        
        return topic_queries.get(topic, base)