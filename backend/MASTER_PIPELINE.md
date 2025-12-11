# Master Pipeline Implementation

## Overview
The master pipeline function `process_all_news()` processes articles sequentially through the complete pipeline: Collect → Summarize → SEO → Save.

## Function: `process_all_news()`

```python
async def process_all_news(topic: Optional[str] = None, max_articles: int = 20)
```

### Flow:
1. **Collect raw articles** from all sources (YouTube, Forbes, Web Search)
2. **For each article sequentially**:
   - Generate summaries (short + long)
   - Generate SEO metadata (meta_title, meta_description, slug, tags)
   - Merge all data into final schema
   - Save article to storage

### Returns:
```python
{
    "status": "success" | "error",
    "count": int,  # Total articles processed
    "saved": int,  # Articles successfully saved
    "errors": [     # List of errors encountered
        {
            "article": str,
            "step": str,  # "process" | "save"
            "error": str
        }
    ]
}
```

## Endpoint: `/run-full-pipeline`

**Method**: `POST`

**Request Body**:
```json
{
    "topic": "AI news latest",  // Optional
    "max_articles": 20          // Optional, default: 20
}
```

**Response**:
```json
{
    "status": "success",
    "message": "Pipeline completed. Processed 20 articles, saved 18.",
    "count": 20,
    "saved": 18,
    "errors": [],
    "error_count": 0
}
```

### Usage:
```bash
# Trigger pipeline manually
curl -X POST http://localhost:8000/run-full-pipeline \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI news latest", "max_articles": 20}'
```

## Scheduler Integration

The scheduler automatically runs `process_all_news()` every **10 minutes** (600 seconds).

### Configuration:
- **Interval**: 10 minutes (600 seconds)
- **Config File**: `backend/app/config.py`
- **Setting**: `SCHEDULER_INTERVAL = 600`

### Scheduler Behavior:
1. Starts automatically when FastAPI app starts
2. Runs `process_all_news()` every 10 minutes
3. Also runs immediately on startup (doesn't wait for first interval)
4. Logs all progress and errors

### Disable Scheduler:
Set in `.env`:
```env
SCHEDULER_ENABLED=false
```

## Pipeline Steps (Per Article)

### 1. Collect Raw Article
- Fetches from YouTube, Forbes, or Web Search
- Normalizes to consistent structure
- Includes: title, url, content, published_at, thumbnail, source

### 2. Generate Summaries
- **Short Summary**: 100-150 characters
- **Long Summary**: 500-1200 words
- Uses SummaryAgent with OpenAI

### 3. Generate SEO Metadata
- **Meta Title**: 50-60 characters
- **Meta Description**: 150-160 characters
- **Slug**: URL-friendly slug
- **Tags**: 5-10 relevant tags
- Uses SEOAgent with OpenAI

### 4. Merge Data
- Combines raw article + summaries + SEO into final schema
- Validates all required fields are present

### 5. Save Article
- Appends to `storage/news.json`
- Checks for duplicates by URL
- Returns success/failure status

## Error Handling

- Errors are caught per article and logged
- Failed articles are skipped, pipeline continues
- Error details are returned in response
- No single article failure stops the entire pipeline

## Logging

All steps are logged with:
- ✅ Success indicators
- ❌ Error indicators
- 📊 Progress counters
- 🔍 Debug information

## Example Output

```
🚀 Starting master pipeline: topic='AI news latest', max_articles=20
Step 1: Collecting raw articles...
✅ Collected 20 raw articles
Processing article 1/20: OpenAI Releases GPT-5...
  → Generating summaries...
  → Generating SEO metadata...
  → Merging data...
  → Saving article...
  ✅ Saved: openai-releases-gpt-5
...
🎉 Master pipeline complete! Processed 20 articles, saved 18, errors: 2
```

