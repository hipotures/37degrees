# Research API Integration Guide

## Overview

The 37degrees project now includes AI-powered research capabilities for generating book reviews and fascinating facts. This system uses various search APIs to gather information about books and formats it into engaging content for young readers.

## Architecture

### Components

1. **Base Classes** (`src/research/base.py`)
   - `BaseResearchProvider`: Abstract base for all research providers
   - `ResearchQuery`: Query parameters dataclass
   - `ResearchResult`: Individual result dataclass
   - `ResearchResponse`: Complete response dataclass

2. **Providers**
   - `PerplexityProvider`: Uses Perplexity AI for comprehensive research
   - `GoogleSearchProvider`: Uses Google Custom Search API
   - `MockResearchProvider`: For testing without API calls

3. **Registry** (`src/research/registry.py`)
   - Dynamic provider loading and management
   - Configuration handling

4. **Review Generator** (`src/research/review_generator.py`)
   - Converts research results to formatted review.md files
   - Handles caching and formatting

## Configuration

Add to your `.env` file:

```bash
# Perplexity API (recommended)
PERPLEXITY_API_KEY=your_api_key_here
PERPLEXITY_MODEL=sonar-medium-online

# Google Search API (optional)
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CX=your_custom_search_engine_id
```

Configure in `config/settings.yaml`:

```yaml
services:
  research:
    default: perplexity  # or google, mock
    cache_enabled: true
    cache_ttl: 900  # 15 minutes
    providers:
      perplexity:
        api_key: ${PERPLEXITY_API_KEY}
        model: ${PERPLEXITY_MODEL:-sonar-medium-online}
        max_tokens: 2000
      google:
        api_key: ${GOOGLE_API_KEY}
        cx: ${GOOGLE_CX}
        daily_limit: 100
```

## Usage

### Command Line

```bash
# Research single book
python main.py research 17
python main.py research little_prince

# Research with specific provider
python main.py research 17 --provider perplexity
python main.py research 17 --provider google
python main.py research 17 --provider mock  # For testing

# Research entire collection
python main.py research classics
python main.py research classics --provider mock
```

### Generated Content

Research generates a `review.md` file in each book's `docs/` directory with:

- 🎯 **Ciekawostki** - Fascinating facts about the book
- 🔮 **Symbolika** - Symbolism and hidden meanings
- 📜 **Kontekst historyczny** - Historical context
- 🎬 **Adaptacje** - Film, theater, and other adaptations
- 💬 **Cytaty** - Famous quotes
- 🌍 **Wpływ kulturowy** - Cultural impact

## Provider Details

### Perplexity AI

**Pros:**
- Real-time web search
- High-quality, contextual responses
- Good for comprehensive research

**Setup:**
1. Get API key from https://www.perplexity.ai/settings/api
2. Add to `.env` file
3. Use `--provider perplexity`

### Google Search

**Pros:**
- Free tier (100 queries/day)
- Direct web results
- Good for specific facts

**Setup:**
1. Create project at https://console.cloud.google.com
2. Enable Custom Search API
3. Create Custom Search Engine at https://cse.google.com
4. Add credentials to `.env`
5. Use `--provider google`

### Mock Provider

**Pros:**
- No API needed
- Instant results
- Perfect for testing

**Usage:**
```bash
python main.py research 17 --provider mock
```

## Caching

Research results are cached to minimize API calls:

- Cache location: `.cache/research/`
- Default TTL: 15 minutes
- Cache key based on: book title + author + language + topics

Clear cache:
```bash
rm -rf .cache/research/
```

## Creating Custom Providers

To add a new research provider:

```python
# src/research/my_provider.py
from src.research.base import BaseResearchProvider, ResearchQuery, ResearchResponse

class MyProvider(BaseResearchProvider):
    def test_connection(self) -> bool:
        # Test API availability
        return True
    
    def search(self, query: ResearchQuery) -> ResearchResponse:
        # Perform research
        results = []
        # ... your implementation
        return ResearchResponse(
            query=query,
            results=results,
            provider="My Provider",
            timestamp=datetime.now(),
            total_results=len(results)
        )
```

Register in `src/cli/research.py`:
```python
registry.register('myprovider', MyProvider)
```

## Best Practices

1. **Use Mock for Development**
   ```bash
   python main.py research 17 --provider mock
   ```

2. **Cache Results**
   - Results are automatically cached
   - Reuse cache during development

3. **Rate Limits**
   - Perplexity: Check your plan limits
   - Google: 100 free queries/day
   - Implement delays between requests

4. **Content Quality**
   - Review generated content
   - Customize prompts for your audience
   - Combine multiple providers for best results

## Troubleshooting

### "API key not configured"
- Check `.env` file has correct keys
- Ensure no spaces around `=` in `.env`
- Restart after changing `.env`

### "Rate limit reached"
- Wait for limit reset
- Use different provider
- Check cache is working

### "No results found"
- Try different search terms
- Check internet connection
- Use mock provider to test

## Future Enhancements

- OpenAI/Claude integration
- Wikipedia API
- GoodReads API
- Automatic translation
- Sentiment analysis
- Fact verification