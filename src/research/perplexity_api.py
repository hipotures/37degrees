"""
Perplexity AI API integration for research
"""

import os
import json
import requests
from typing import Dict, List, Any
from datetime import datetime
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


class PerplexityProvider(BaseResearchProvider):
    """Perplexity AI research provider"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Perplexity provider
        
        Args:
            config: Configuration with:
                - api_key: Perplexity API key (or use PERPLEXITY_API_KEY env)
                - model: Model to use (default: sonar-medium-online)
                - max_tokens: Maximum tokens in response (default: 2000)
        """
        super().__init__(config)
        
        # Get API key from config or environment
        self.api_key = config.get('api_key') or os.getenv('PERPLEXITY_API_KEY')
        if not self.api_key or self.api_key == 'dummy_key_for_development':
            console.print("[yellow]Warning: Perplexity API key not configured[/yellow]")
        
        self.base_url = "https://api.perplexity.ai"
        self.model = config.get('model', 'sonar-medium-online')
        self.max_tokens = config.get('max_tokens', 2000)
    
    def test_connection(self) -> bool:
        """Test if Perplexity API is accessible"""
        if not self.api_key or self.api_key == 'dummy_key_for_development':
            console.print("[red]Perplexity API key not configured[/red]")
            return False
        
        try:
            # Simple test query
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "Test"}],
                    "max_tokens": 10
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            console.print(f"[red]Connection test failed: {e}[/red]")
            return False
    
    def search(self, query: ResearchQuery) -> ResearchResponse:
        """Perform research using Perplexity AI
        
        Args:
            query: Research query parameters
            
        Returns:
            ResearchResponse with results
        """
        if not self.api_key or self.api_key == 'dummy_key_for_development':
            raise ResearchAPIError("Perplexity API key not configured")
        
        results = []
        
        # Research each topic
        for topic in query.topics:
            prompt = self._build_prompt(query, topic)
            
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": f"You are a literary research assistant. Provide interesting facts and insights about books in {query.language}. Focus on fascinating, lesser-known details that would interest young readers (10-20 years old)."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": self.max_tokens,
                        "temperature": 0.7,
                        "stream": False
                    },
                    timeout=30
                )
                
                if response.status_code == 429:
                    raise ResearchLimitError("Perplexity API rate limit reached")
                elif response.status_code != 200:
                    raise ResearchAPIError(f"Perplexity API error: {response.status_code} - {response.text}")
                
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Parse response into structured result
                result = ResearchResult(
                    title=f"{topic.capitalize()} - {query.book_title}",
                    content=content,
                    source="Perplexity AI",
                    url=None,
                    date=datetime.now(),
                    relevance_score=0.9,
                    metadata={
                        'model': self.model,
                        'topic': topic
                    }
                )
                results.append(result)
                
                console.print(f"[green]✓ Researched {topic} for {query.book_title}[/green]")
                
            except requests.exceptions.Timeout:
                console.print(f"[yellow]Timeout researching {topic}[/yellow]")
            except (ResearchAPIError, ResearchLimitError):
                raise
            except Exception as e:
                console.print(f"[red]Error researching {topic}: {e}[/red]")
        
        return ResearchResponse(
            query=query,
            results=results,
            provider="Perplexity",
            timestamp=datetime.now(),
            total_results=len(results),
            metadata={
                'model': self.model,
                'api_version': 'v1'
            }
        )
    
    def _build_prompt(self, query: ResearchQuery, topic: str) -> str:
        """Build research prompt for specific topic"""
        prompts = {
            "ciekawostki": f"""
Znajdź 3-5 fascynujących ciekawostek o książce "{query.book_title}" autorstwa {query.author}.
Szukaj informacji o:
- Nietypowych okolicznościach powstania książki
- Zaskakujących faktach z życia autora związanych z książką
- Rekordach lub wyjątkowych osiągnięciach książki
- Ciekawych historiach związanych z publikacją lub recepcją
Podaj konkretne fakty z datami i liczbami gdzie to możliwe.
""",
            
            "symbolika": f"""
Wyjaśnij główne symbole i metafory w książce "{query.book_title}" autorstwa {query.author}.
Opisz:
- Najważniejsze symbole i ich znaczenie
- Ukryte znaczenia i alegorie
- Jak symbole łączą się z przesłaniem książki
- Przykłady konkretnych scen gdzie symbole są kluczowe
Wyjaśnij w sposób zrozumiały dla młodych czytelników.
""",
            
            "kontekst historyczny": f"""
Opisz kontekst historyczny książki "{query.book_title}" autorstwa {query.author}.
Uwzględnij:
- W jakich czasach powstała książka i dlaczego to ważne
- Jakie wydarzenia historyczne wpłynęły na treść
- Jak książka odzwierciedla swoją epokę
- Czy książka wpłynęła na historię lub społeczeństwo
Podaj konkretne daty i wydarzenia.
""",
            
            "adaptacje": f"""
Wymień i opisz adaptacje książki "{query.book_title}" autorstwa {query.author}.
Szukaj informacji o:
- Adaptacjach filmowych (daty, reżyserzy, aktorzy)
- Serialach telewizyjnych
- Adaptacjach teatralnych
- Grach komputerowych
- Komiksach lub mangach
- Innych formach adaptacji
Podaj konkretne tytuły, daty i twórców.
""",
            
            "cytaty": f"""
Znajdź 3-5 najsłynniejszych cytatów z książki "{query.book_title}" autorstwa {query.author}.
Dla każdego cytatu:
- Podaj dokładny cytat w języku polskim
- Wyjaśnij kontekst i znaczenie
- Opisz dlaczego cytat stał się słynny
- Jak jest używany współcześnie
Wybierz cytaty, które najbardziej przemawiają do młodych ludzi.
""",
            
            "wpływ kulturowy": f"""
Opisz wpływ kulturowy książki "{query.book_title}" autorstwa {query.author}.
Uwzględnij:
- Jak książka zmieniła literaturę lub kulturę
- Wpływ na inne dzieła i twórców
- Obecność w popkulturze
- Memy, odniesienia w internecie
- Współczesne nawiązania
Podaj konkretne przykłady.
"""
        }
        
        return prompts.get(topic, f"Opowiedz o {topic} w kontekście książki '{query.book_title}' autorstwa {query.author}.")