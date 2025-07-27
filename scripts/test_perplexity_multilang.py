#!/usr/bin/env python3
"""
Test Perplexity API for multi-language search results
"""

import os
from src.research.perplexity_api import PerplexityProvider
from src.research.base import ResearchQuery
from src.config import get_config

# Load config
config = get_config()

# Get perplexity config directly
perplexity_config = {
    'api_key': os.getenv('PERPLEXITY_API_KEY'),
    'model': os.getenv('PERPLEXITY_MODEL', 'sonar'),
    'max_tokens': 2000
}

# Create provider
provider = PerplexityProvider(perplexity_config)

# Test with adaptations topic only
print("Testing Perplexity API for multi-language results...")
print("=" * 60)

# Test 1: Original prompt (should return mostly Polish results)
print("\nTest 1: Original prompt")
print("-" * 40)

# Print the actual prompt that will be sent
print("\nActual prompt being sent:")
print("System prompt:", provider._get_system_prompt('pl'))
print("\nUser prompt for 'adaptacje':")
print(provider._build_prompt(ResearchQuery(
    book_title='Alicja w Krainie Czarów',
    author='Lewis Carroll',
    topics=['adaptacje']
), 'adaptacje'))
print("-" * 40)

query1 = ResearchQuery(
    book_title='Alicja w Krainie Czarów',
    author='Lewis Carroll',
    topics=['adaptacje']
)

try:
    response1 = provider.search(query1)
    result1 = response1.results[0] if response1.results else None
    
    if result1:
        print(f"Content preview: {result1.content[:200]}...")
        
        # Check search results
        search_results = result1.metadata.get('search_results', [])
        print(f"\nSearch results count: {len(search_results)}")
        
        # Analyze domains
        domains = {}
        for sr in search_results:
            url = sr.get('url', '')
            if url:
                # Extract domain
                domain = url.split('/')[2] if len(url.split('/')) > 2 else 'unknown'
                # Check if Polish domain
                is_polish = domain.endswith('.pl') or 'pl.' in domain
                country = 'PL' if is_polish else 'OTHER'
                domains[country] = domains.get(country, 0) + 1
                print(f"  - {domain} [{country}]")
        
        print(f"\nDomain analysis: PL={domains.get('PL', 0)}, OTHER={domains.get('OTHER', 0)}")
        
except Exception as e:
    print(f"Error: {e}")

# Test 2: Modified prompt with explicit language requirement
print("\n\nTest 2: Modified prompt with explicit language requirement")
print("-" * 40)

# Temporarily modify the prompt to include explicit language requirement
import yaml
from pathlib import Path

prompts_file = Path("config/research_prompts.yaml")
with open(prompts_file, 'r', encoding='utf-8') as f:
    prompts_config = yaml.safe_load(f)

# Save original prompt
original_prompt = prompts_config['perplexity']['topics']['adaptacje']

# Create modified prompt
modified_prompt = """List and describe adaptations of the book "{book_title}" by {author}.
CRITICAL: You MUST search for sources in BOTH Polish language (from domains like .pl, filmweb, culture.pl) AND English language (from domains like .com, .org, imdb.com, variety.com).
I need a balanced mix - at least 40% Polish sources and 40% English/international sources.
Search query should include both "Alicja w Krainie Czarów" AND "Alice in Wonderland" to get diverse results.
Look for:
- Film adaptations (dates, directors, actors)
- TV series
- Theater adaptations
- Video games
- Comics or manga
Include specific titles, dates, and creators. Present findings in Polish."""

# Update prompt temporarily
prompts_config['perplexity']['topics']['adaptacje'] = modified_prompt
provider.prompts_config = prompts_config

query2 = ResearchQuery(
    book_title='Alicja w Krainie Czarów',
    author='Lewis Carroll',
    topics=['adaptacje']
)

try:
    response2 = provider.search(query2)
    result2 = response2.results[0] if response2.results else None
    
    if result2:
        print(f"Content preview: {result2.content[:200]}...")
        
        # Check search results
        search_results = result2.metadata.get('search_results', [])
        print(f"\nSearch results count: {len(search_results)}")
        
        # Analyze domains
        domains = {}
        for sr in search_results:
            url = sr.get('url', '')
            if url:
                # Extract domain
                domain = url.split('/')[2] if len(url.split('/')) > 2 else 'unknown'
                # Check if Polish domain
                is_polish = domain.endswith('.pl') or 'pl.' in domain
                country = 'PL' if is_polish else 'OTHER'
                domains[country] = domains.get(country, 0) + 1
                print(f"  - {domain} [{country}]")
        
        print(f"\nDomain analysis: PL={domains.get('PL', 0)}, OTHER={domains.get('OTHER', 0)}")
        
except Exception as e:
    print(f"Error: {e}")

# Test 3: English title
print("\n\nTest 3: Using English book title")
print("-" * 40)

query3 = ResearchQuery(
    book_title="Alice's Adventures in Wonderland",
    author='Lewis Carroll',
    topics=['adaptacje']
)

try:
    response3 = provider.search(query3)
    result3 = response3.results[0] if response3.results else None
    
    if result3:
        print(f"Content preview: {result3.content[:200]}...")
        
        # Check search results
        search_results = result3.metadata.get('search_results', [])
        print(f"\nSearch results count: {len(search_results)}")
        
        # Analyze domains
        domains = {}
        for sr in search_results:
            url = sr.get('url', '')
            if url:
                # Extract domain
                domain = url.split('/')[2] if len(url.split('/')) > 2 else 'unknown'
                # Check if Polish domain
                is_polish = domain.endswith('.pl') or 'pl.' in domain
                country = 'PL' if is_polish else 'OTHER'
                domains[country] = domains.get(country, 0) + 1
                print(f"  - {domain} [{country}]")
        
        print(f"\nDomain analysis: PL={domains.get('PL', 0)}, OTHER={domains.get('OTHER', 0)}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("Test completed")