# AIDesk API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Endpoints

### POST /collect-news
Collect news from multiple sources.

**Request:**
```json
{
  "topic": "AI news latest",
  "max_articles": 10
}
```

**Response:**
```json
{
  "status": "success",
  "count": 10,
  "articles": [...]
}
```

### POST /summaries
Generate summaries for articles.

**Request:**
```json
{
  "articles": [
    {
      "title": "...",
      "url": "...",
      "source": "..."
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "count": 1,
  "articles": [
    {
      ...,
      "short_summary": "...",
      "long_summary": "..."
    }
  ]
}
```

### POST /generate-seo
Generate SEO metadata.

**Request:**
```json
{
  "title": "Article Title",
  "content": "Article content..."
}
```

**Response:**
```json
{
  "status": "success",
  "seo": {
    "meta_title": "...",
    "meta_description": "...",
    "slug": "...",
    "tags": [...]
  }
}
```

### POST /save-news
Save a processed article.

**Request:**
```json
{
  "title": "...",
  "slug": "...",
  "url": "...",
  "short_summary": "...",
  "long_summary": "...",
  "meta_title": "...",
  "meta_description": "...",
  "tags": [...],
  "source": "..."
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Article saved successfully",
  "article": {...}
}
```

### GET /list-news
List all articles with pagination.

**Query Parameters:**
- `page` (int, default: 1)
- `limit` (int, default: 20)

**Response:**
```json
{
  "articles": [...],
  "count": 20,
  "page": 1,
  "total_pages": 5
}
```

### GET /news/{slug}
Get a specific article by slug.

**Response:**
```json
{
  "title": "...",
  "slug": "...",
  ...
}
```

