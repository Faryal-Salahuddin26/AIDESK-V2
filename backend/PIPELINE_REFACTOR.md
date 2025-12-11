# Backend Pipeline Refactor - Complete

## Overview

The entire backend pipeline has been refactored to ensure:
- ✅ Consistent JSON structure across all stages
- ✅ Single storage file (`storage/news.json`) with append mode
- ✅ Reverse chronological ordering (newest first)
- ✅ Comprehensive error handling and logging
- ✅ Proper integration with OpenAI Agents SDK 2025

## Pipeline Flow

```
Collector Agent → Raw Article → Summarizer Agent → SEO Agent → Final Article JSON
                                                                      ↓
                                                              save-news (backend)
                                                                      ↓
                                                              storage/news.json
                                                                      ↓
                                                              GET /list-news
                                                                      ↓
                                                              HomePage displays
```

## Article Schema

All articles follow a consistent structure defined in `app/schemas/article_schema.py`:

### Raw Article (from CollectorAgent)
```json
{
  "title": "string",
  "url": "string",
  "source": "string",
  "published_at": "ISO datetime",
  "description": "string",
  "thumbnail": "string",
  "video_url": "string",
  "documentation_url": "string",
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime"
}
```

### With Summaries (from SummaryAgent)
Adds:
- `short_summary`: string (100-150 chars)
- `long_summary`: string (500-1200 words)

### Final Article (with SEO from SEOAgent)
Adds:
- `meta_title`: string (50-60 chars)
- `meta_description`: string (150-160 chars)
- `slug`: string (URL-friendly)
- `tags`: array of strings (5-10 tags)

## Endpoints

### POST `/collect-news`
- Fetches raw articles from multiple sources
- Returns articles with consistent structure
- Uses `ArticleSchema.create_raw_article()` for normalization

### POST `/summaries`
- Generates short and long summaries
- Uses `ArticleSchema.add_summaries()` to add summaries
- Handles errors gracefully, continues with other articles

### POST `/seo`
- Generates all 4 SEO fields: meta_title, meta_description, slug, tags
- Uses `ArticleSchema.add_seo()` to add SEO metadata

### POST `/save-news`
- **Appends** article to `storage/news.json`
- Validates article structure before saving
- Prevents duplicates by URL
- Returns success/failure status

### GET `/list-news`
- Reads from `storage/news.json`
- Returns articles in **reverse chronological order** (newest first)
- Supports pagination (page, limit)
- Returns total count

### POST `/process`
- **Complete pipeline**: Collector → Summarizer → SEO → Save
- Runs all agents in sequence
- Saves all processed articles automatically
- Returns processed articles and save count

### GET `/news/{slug}`
- Gets article by slug from `storage/news.json`
- Optional `fetch_content=true` to fetch full article content

### GET `/stats`
- Returns statistics about stored articles
- Total count, sources breakdown, file size

## Storage Service

New `StorageService` class (`app/services/storage_service.py`):
- Manages single `storage/news.json` file
- Append mode for saving articles
- Automatic deduplication by URL
- Reverse chronological sorting
- Error handling and logging
- File initialization if missing

## Logging

Comprehensive logging throughout:
- ✅ Info logs for each pipeline step
- ✅ Debug logs for individual article processing
- ✅ Error logs with full tracebacks
- ✅ Success confirmations

Log format: `timestamp - logger - level - message`

## Error Handling

- ✅ Try-catch blocks around all operations
- ✅ HTTPException for API errors
- ✅ Graceful degradation (continues processing other articles)
- ✅ Detailed error messages
- ✅ Stack traces in logs

## Testing the Pipeline

### 1. Test Complete Pipeline
```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI news", "max_articles": 5}'
```

### 2. Test Individual Steps
```bash
# Collect
curl -X POST http://localhost:8000/collect-news \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI news", "max_articles": 3}'

# Summarize (use articles from collect)
curl -X POST http://localhost:8000/summaries \
  -H "Content-Type: application/json" \
  -d '{"articles": [...]}'

# SEO (use article with summaries)
curl -X POST http://localhost:8000/seo \
  -H "Content-Type: application/json" \
  -d '{"title": "...", "content": "..."}'

# Save
curl -X POST http://localhost:8000/save-news \
  -H "Content-Type: application/json" \
  -d '{"article": {...}}'
```

### 3. List Articles
```bash
curl http://localhost:8000/list-news?page=1&limit=10
```

### 4. Get Stats
```bash
curl http://localhost:8000/stats
```

## File Structure

```
backend/
├── main.py                          # Main FastAPI app (refactored)
├── collector_agent.py               # CollectorAgent (unchanged)
├── summary_agent.py                 # SummaryAgent (unchanged)
├── seo_agent.py                     # SEOAgent (unchanged)
├── app/
│   ├── schemas/
│   │   └── article_schema.py       # NEW: Consistent article schema
│   ├── services/
│   │   └── storage_service.py      # NEW: Storage service for news.json
│   └── ...
└── storage/
    └── news.json                    # Single file with all articles
```

## Migration Notes

- Old individual JSON files in `storage/news-data/` are still readable
- New articles are saved to `storage/news.json`
- `/list-news` now reads from `storage/news.json` only
- Old endpoint `/save-news-json` is replaced by `/save-news`

## Benefits

1. **Consistency**: All articles follow the same structure
2. **Simplicity**: Single file instead of many individual files
3. **Performance**: Faster reads/writes with single file
4. **Maintainability**: Clear pipeline with logging
5. **Reliability**: Comprehensive error handling
6. **Scalability**: Easy to migrate to database later

