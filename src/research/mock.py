"""
Mock research provider for testing
"""

import random
from typing import Dict, Any
from datetime import datetime, timedelta
from rich.console import Console

from .base import (
    BaseResearchProvider, 
    ResearchQuery, 
    ResearchResponse, 
    ResearchResult
)

console = Console()


class MockResearchProvider(BaseResearchProvider):
    """Mock research provider for testing without API calls"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize mock provider
        
        Args:
            config: Configuration (mostly ignored for mock)
        """
        super().__init__(config)
        self.delay = config.get('delay', 0.5)
        
    def test_connection(self) -> bool:
        """Always returns True for mock"""
        console.print("[green]Mock research provider connection test successful[/green]")
        return True
    
    def search(self, query: ResearchQuery) -> ResearchResponse:
        """Generate mock research results
        
        Args:
            query: Research query parameters
            
        Returns:
            ResearchResponse with mock results
        """
        results = []
        
        # Generate mock results for each topic
        for topic in query.topics:
            # Simulate some delay
            import time
            time.sleep(self.delay)
            
            mock_content = self._generate_mock_content(query, topic)
            
            result = ResearchResult(
                title=f"{topic.capitalize()} - {query.book_title} (Mock)",
                content=mock_content,
                source="Mock Research Provider",
                url=f"https://example.com/{query.book_title.lower().replace(' ', '-')}/{topic}",
                date=datetime.now() - timedelta(days=random.randint(1, 365)),
                relevance_score=random.uniform(0.7, 1.0),
                metadata={
                    'mock': True,
                    'topic': topic
                }
            )
            results.append(result)
            
            console.print(f"[green]✓ Mock researched {topic} for {query.book_title}[/green]")
        
        return ResearchResponse(
            query=query,
            results=results,
            provider="Mock",
            timestamp=datetime.now(),
            total_results=len(results),
            metadata={
                'mock': True,
                'test_mode': True
            }
        )
    
    def _generate_mock_content(self, query: ResearchQuery, topic: str) -> str:
        """Generate mock content for specific topic"""
        
        mock_data = {
            "ciekawostki": [
                f"Książka '{query.book_title}' została napisana w zaledwie 3 miesiące podczas podróży autora po Europie.",
                f"{query.author} napisał pierwszą wersję '{query.book_title}' na serwetce w kawiarni.",
                f"Pierwsze wydanie '{query.book_title}' zawierało błąd drukarski, który zmienił sens całego rozdziału.",
                f"'{query.book_title}' było początkowo odrzucone przez 12 wydawnictw.",
                f"Rękopis '{query.book_title}' został odnaleziony dopiero 10 lat po śmierci autora."
            ],
            
            "symbolika": [
                f"Główny bohater '{query.book_title}' symbolizuje walkę człowieka z własnymi ograniczeniami.",
                f"Powtarzający się motyw wody w '{query.book_title}' reprezentuje przemijanie i odnowę.",
                f"Kolory użyte w opisach w '{query.book_title}' mają głębokie znaczenie symboliczne.",
                f"Liczba 7 pojawia się w '{query.book_title}' dokładnie 77 razy, co nie jest przypadkiem.",
                f"Imiona bohaterów '{query.book_title}' tworzą anagram hasła przewodniego książki."
            ],
            
            "kontekst historyczny": [
                f"'{query.book_title}' powstało w czasie wielkiego kryzysu gospodarczego lat 30.",
                f"Wydarzenia w '{query.book_title}' są alegorią II wojny światowej.",
                f"{query.author} pisał '{query.book_title}' będąc na emigracji politycznej.",
                f"Publikacja '{query.book_title}' zbiegła się z ważnymi wydarzeniami historycznymi.",
                f"'{query.book_title}' było zakazane w 5 krajach ze względów politycznych."
            ],
            
            "adaptacje": [
                f"Istnieją 3 adaptacje filmowe '{query.book_title}' - z 1962, 1987 i 2019 roku.",
                f"Musical oparty na '{query.book_title}' był wystawiany na Broadwayu przez 5 lat.",
                f"Manga inspirowana '{query.book_title}' sprzedała się w nakładzie 2 milionów egzemplarzy.",
                f"Gra komputerowa na podstawie '{query.book_title}' zdobyła nagrodę za fabułę.",
                f"Opera na podstawie '{query.book_title}' miała premierę w La Scali."
            ],
            
            "cytaty": [
                f"'Najważniejsze jest niewidoczne dla oczu' - najsłynniejszy cytat z '{query.book_title}'.",
                f"'Każdy człowiek jest swoim własnym wrogiem' - cytat który zmienił życie wielu czytelników.",
                f"'Czas jest jedynym prawdziwym bogactwem' - motto przewodnie '{query.book_title}'.",
                f"'Miłość to nie patrzenie na siebie, ale patrzenie razem w tym samym kierunku'.",
                f"'Prawdziwe piękno kryje się w prostocie' - cytat często używany w motivatorach."
            ],
            
            "wpływ kulturowy": [
                f"'{query.book_title}' zainspirowało powstanie 50 innych powieści.",
                f"Fraza z '{query.book_title}' stała się popularnym memem internetowym.",
                f"Uniwersytet w Oxfordzie prowadzi specjalny kurs poświęcony '{query.book_title}'.",
                f"'{query.book_title}' jest cytowane w ponad 1000 prac naukowych.",
                f"Fankluby '{query.book_title}' istnieją w 40 krajach świata."
            ]
        }
        
        # Get random content for topic
        content_list = mock_data.get(topic, [f"Mock content for {topic} in '{query.book_title}'."])
        selected = random.sample(content_list, min(3, len(content_list)))
        
        return "\n\n".join(selected)