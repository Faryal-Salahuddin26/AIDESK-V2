# AIDesk Backend - API Endpoints Reference

## 📡 All Endpoints

### Root
```
GET /
```
Returns API information and available endpoints.

---

### Collect News
```
POST /collect-news
```
Runs CollectorAgent to fetch news from multiple sources.

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

---

### Generate Summaries
```
POST /summaries
```
Runs SummaryAgent to generate short and long summaries.

**Request:**
```json
{
  "articles": [
    {
      "title": "...",
      "url": "...",
      "source": "...",
      "published_at": "..."
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

---

### Generate SEO Metadata
```
POST /seo
```
Runs SEOAgent to generate SEO metadata.

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

---

### Process Pipeline
```
POST /process
```
Runs all agents in sequence: Collector → Summary → SEO.

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
  "articles": [
    {
      "title": "...",
      "url": "...",
      "source": "...",
      "published_at": "...",
      "short_summary": "...",
      "long_summary": "...",
      "meta_title": "...",
      "meta_description": "...",
      "slug": "...",
      "tags": [...]
    }
  ]
}
```

---

### Save Article
```
POST /save-news-json
```
Saves a processed article to JSON file.

**Request:**
```json
{
  "article": {
    "title": "...",
    "slug": "...",
    "url": "...",
    "short_summary": "...",
    "long_summary": "...",
    "meta_title": "...",
    "meta_description": "...",
    "tags": [...],
    "source": "...",
    "published_at": "..."
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Article saved successfully",
  "slug": "article-slug",
  "file_path": "/path/to/article-slug.json"
}
```

---

### List All Articles
```
GET /list-news
```
Lists all saved articles from JSON files.

**Response:**
```json
{
  "articles": [...],
  "count": 10
}
```

---

### Get Article by Slug
```
GET /news/{slug}
```
Gets a specific article by slug.

**Response:**
```json
{
  "title": "...",
  "slug": "...",
  ...
}
```

---

## 🔄 Typical Workflow

1. **Process News** → `POST /process`
2. **Save Articles** → `POST /save-news-json` (for each article)
3. **List Articles** → `GET /list-news`
4. **View Article** → `GET /news/{slug}`

## 📝 Example: Complete Workflow

```bash
# 1. Process news
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI news", "max_articles": 5}'

# 2. Save articles (use response from step 1)
# For each article in the response:
curl -X POST http://localhost:8000/save-news-json \
  -H "Content-Type: application/json" \
  -d '{"article": {...}}'

# 3. List all saved articles
curl http://localhost:8000/list-news

# 4. Get specific article
curl http://localhost:8000/news/article-slug
```

