# Collector Agent Refactor

## Overview
The Collector Agent has been completely rewritten to fetch articles from multiple sources and normalize all results to a consistent structure.

## Key Features

### 1. **YouTube Articles**
- **Primary Method**: YouTube Data API v3
  - Fetches videos with transcripts/descriptions
  - Gets thumbnails, titles, descriptions
  - Filters by date (current month)
- **Fallback**: RSS Feeds
  - Uses official AI YouTube channel RSS feeds
  - No API key required

### 2. **Forbes Articles**
- **Primary Method**: RSS Feeds
  - Forbes real-time feed
  - Forbes innovation feed
  - Forbes AI feed
- **Fallback**: HTML Scraping
  - Scrapes Forbes website directly
  - Extracts article links and titles

### 3. **Web Search Articles**
- **Primary Method**: Bing Search API
  - Uses Microsoft Bing Search API v7
  - Returns relevant AI news articles
- **Fallback 1**: Google Custom Search API
  - Uses Google Custom Search Engine
- **Fallback 2**: RSS Feeds
  - TechCrunch, The Verge, Wired RSS feeds

### 4. **Content Extraction Fallback**
If an article doesn't have sufficient content (< 200 characters):
1. **First**: Tries `ArticleFetcher` service (if available)
   - Fetches full webpage
   - Extracts main content using multiple strategies
   - Gets images and links
2. **Second**: Simple HTML scraping
   - Basic BeautifulSoup parsing
   - Extracts text content
   - Gets thumbnail if available

## Normalized Structure

All articles are normalized to this consistent structure:

```python
{
    "title": string,           # Article title
    "url": string,             # Article URL
    "content": string,         # Full article content
    "published_at": ISO string, # ISO 8601 date format
    "thumbnail": string,        # Thumbnail image URL
    "source": string,          # Source name (youtube, forbes, web_search)
    "description": string,     # Short description (optional, for compatibility)
    "video_url": string,       # Video URL (if applicable)
    "documentation_url": string # Documentation URL (if applicable)
}
```

## API Keys Required

Add these to your `.env` file:

```env
# Required
OPENAI_API_KEY=your_openai_key

# Optional (for enhanced collection)
YOUTUBE_API_KEY=your_youtube_key
BING_SEARCH_API_KEY=your_bing_key
GOOGLE_SEARCH_API_KEY=your_google_key
GOOGLE_SEARCH_ENGINE_ID=your_engine_id
```

## Usage

```python
from collector_agent import CollectorAgent

collector = CollectorAgent()
articles = await collector.collect_articles(
    topic="AI news latest",
    max_articles=20
)

# All articles are normalized with consistent structure
for article in articles:
    print(article["title"])
    print(article["url"])
    print(article["content"])
    print(article["published_at"])
    print(article["thumbnail"])
```

## Benefits

1. **Consistent Structure**: All articles follow the same format
2. **Multiple Fallbacks**: If one method fails, others are tried
3. **Content Extraction**: Automatically fetches full content when needed
4. **Better Coverage**: Fetches from YouTube, Forbes, and web search
5. **Robust**: Handles errors gracefully and continues with other sources

## Changes from Previous Version

- ✅ Normalized all results to consistent structure
- ✅ Added Bing Search API support
- ✅ Enhanced YouTube fetching with better transcript handling
- ✅ Improved Forbes scraping with HTML fallback
- ✅ Added content extraction fallback mechanism
- ✅ Better error handling and logging
- ✅ Preserves compatibility with existing code (source, description fields)

