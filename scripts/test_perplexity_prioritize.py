#!/usr/bin/env python3
"""
Test Perplexity API with prioritize language approach
"""

import os
import requests
import json

# API configuration
api_key = os.getenv('PERPLEXITY_API_KEY')
base_url = "https://api.perplexity.ai"

# Test prompt with prioritize approach
prompt = """Search for film, TV, theater, game and other adaptations of "Alice in Wonderland" by Lewis Carroll.
Prioritize sources from multiple countries: find English-language sources from USA/UK AND Polish-language sources from Poland.
Give equal priority to both international sources and Polish sources.
Look for:
- Film adaptations (dates, directors, actors) 
- TV series
- Theater adaptations
- Video games
- Comics or manga
Write your response in Polish language."""

# Make API call
response = requests.post(
    f"{base_url}/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are a literary research assistant. Search for information in any language from sources worldwide."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.7,
        "stream": False
    },
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    content = data['choices'][0]['message']['content']
    
    print("Response preview:")
    print(content[:500] + "...")
    
    # Check search results if available
    search_results = data.get('search_results', [])
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
    
else:
    print(f"Error: {response.status_code}")
    print(response.text)