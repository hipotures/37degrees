#!/usr/bin/env python3
"""
Test Perplexity with prioritize approach
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.research.perplexity_api import PerplexityProvider
from src.research.base import ResearchQuery

# Create provider
provider = PerplexityProvider({
    'api_key': os.getenv('PERPLEXITY_API_KEY'),
    'model': 'sonar',
    'max_tokens': 2000
})

# Override the prompt temporarily
import yaml
from pathlib import Path

prompts_file = Path("config/research_prompts.yaml")
with open(prompts_file, 'r', encoding='utf-8') as f:
    prompts_config = yaml.safe_load(f)

# Test with prioritize approach
prompts_config['perplexity']['topics']['adaptacje'] = """Search for film, TV, theater, game and other adaptations of "{book_title}" by {author}.
Prioritize sources from multiple countries: find English-language sources from USA/UK AND Polish-language sources from Poland.
Give equal priority to both international sources and Polish sources.
Look for:
- Film adaptations (dates, directors, actors) 
- TV series
- Theater adaptations
- Video games
- Comics or manga
Write your response in Polish language."""

provider.prompts_config = prompts_config

# Test query
query = ResearchQuery(
    book_title='Alice in Wonderland',
    author='Lewis Carroll',
    topics=['adaptacje']
)

print("Testing with 'prioritize' approach...")
print("=" * 60)
print("\nEXACT PROMPT BEING SENT:")
print("System prompt:", provider._get_system_prompt('pl'))
print("\nUser prompt:")
print(provider._build_prompt(query, 'adaptacje'))
print("=" * 60)

try:
    response = provider.search(query)
    if response.results:
        result = response.results[0]
        print(f"Content preview: {result.content[:300]}...")
        
        # Save full response to JSON
        import json
        with open('perplexity_response.json', 'w', encoding='utf-8') as f:
            json.dump({
                'content': result.content,
                'metadata': result.metadata,
                'source': result.source,
                'url': result.url
            }, f, ensure_ascii=False, indent=2)
        print("\nFull response saved to: perplexity_response.json")
        
        # Check search results
        search_results = result.metadata.get('search_results', [])
        print(f"\nSearch results: {len(search_results)}")
        
        domains = {}
        for sr in search_results[:10]:
            url = sr.get('url', '')
            if url:
                domain = url.split('/')[2] if len(url.split('/')) > 2 else 'unknown'
                is_polish = domain.endswith('.pl') or 'pl.' in domain
                country = 'PL' if is_polish else 'OTHER'
                domains[country] = domains.get(country, 0) + 1
                print(f"  - {domain} [{country}]")
        
        print(f"\nDomain balance: PL={domains.get('PL', 0)}, OTHER={domains.get('OTHER', 0)}")
        
except Exception as e:
    print(f"Error: {e}")