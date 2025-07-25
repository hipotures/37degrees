"""
Perplexity AI API integration for research
"""

import os
import json
import yaml
import requests
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
from rich.console import Console

from .base import (
    BaseResearchProvider, 
    ResearchQuery, 
    ResearchResponse, 
    ResearchResult,
    ResearchAPIError,
    ResearchLimitError
)
from .citation_db import CitationDatabase

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
        self.model = config.get('model', 'sonar')
        self.max_tokens = config.get('max_tokens', 2000)
        
        # Load prompts from YAML
        self._load_prompts()
    
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
                                "content": self._get_system_prompt(query.language)
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
                
                # Extract citations if available
                citations = data.get('citations', [])
                search_results = data.get('search_results', [])
                
                # Get first citation URL if available
                url = None
                if citations and len(citations) > 0:
                    url = citations[0]
                elif search_results and len(search_results) > 0:
                    url = search_results[0].get('url')
                
                # Parse response into structured result
                result = ResearchResult(
                    title=f"{topic.capitalize()} - {query.book_title}",
                    content=content,
                    source="Perplexity AI",
                    url=url,
                    date=datetime.now(),
                    relevance_score=0.9,
                    metadata={
                        'model': self.model,
                        'topic': topic,
                        'citations': citations,
                        'search_results': search_results
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
    
    def _load_prompts(self):
        """Load prompts from YAML configuration"""
        prompts_file = Path("config/research_prompts.yaml")
        if prompts_file.exists():
            with open(prompts_file, 'r', encoding='utf-8') as f:
                self.prompts_config = yaml.safe_load(f)
        else:
            console.print("[yellow]Warning: research_prompts.yaml not found, using defaults[/yellow]")
            self.prompts_config = {}
    
    def _get_system_prompt(self, language: str) -> str:
        """Get system prompt from config"""
        system_prompt_template = self.prompts_config.get('perplexity', {}).get('system_prompt', '')
        
        if not system_prompt_template:
            # Default system prompt if not in config
            return f"You are a literary research assistant. Provide interesting facts and insights about books in {language}. Focus on fascinating, lesser-known details that would interest young readers (10-20 years old)."
        
        return system_prompt_template.format(language=language)
    
    def _build_prompt(self, query: ResearchQuery, topic: str) -> str:
        """Build research prompt for specific topic"""
        # Get prompts from config
        perplexity_prompts = self.prompts_config.get('perplexity', {}).get('topics', {})
        
        # Normalize topic name (replace spaces with underscores)
        topic_key = topic.replace(' ', '_')
        
        # Get prompt template
        prompt_template = perplexity_prompts.get(topic_key, perplexity_prompts.get('default', ''))
        
        # If no template found, use old default
        if not prompt_template:
            return f"Opowiedz o {topic} w kontekście książki '{query.book_title}' autorstwa {query.author}."
        
        # Format the prompt with book details
        return prompt_template.format(
            book_title=query.book_title,
            author=query.author,
            topic=topic
        )