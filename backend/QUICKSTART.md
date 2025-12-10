# AIDesk Backend - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
pip install openai-agents  # or: pip install agents
```

### 2. Create .env File
```bash
echo "OPENAI_API_KEY=your_key_here" > .env
```

### 3. Run Server
```bash
uvicorn main:app --reload --port 8000
```

### 4. Test API
Open browser: http://localhost:8000/docs

## 📡 Quick API Test

### Test Complete Pipeline
```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI news", "max_articles": 3}'
```

### Save an Article
```bash
curl -X POST http://localhost:8000/save-news-json \
  -H "Content-Type: application/json" \
  -d '{
    "article": {
      "title": "Test Article",
      "slug": "test-article",
      "url": "https://example.com",
      "short_summary": "Test summary",
      "long_summary": "Long test summary...",
      "meta_title": "Test Article",
      "meta_description": "Test description",
      "tags": ["AI"],
      "source": "test",
      "published_at": "2025-01-01T12:00:00"
    }
  }'
```

### List All Articles
```bash
curl http://localhost:8000/list-news
```

## 🎯 Endpoint Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/collect-news` | POST | Fetch news from sources |
| `/summaries` | POST | Generate summaries |
| `/seo` | POST | Generate SEO metadata |
| `/process` | POST | Run all agents (recommended) |
| `/save-news-json` | POST | Save article to JSON |
| `/list-news` | GET | List all articles |
| `/news/{slug}` | GET | Get specific article |

## 📝 Complete Workflow Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Step 1: Process news (collect + summarize + SEO)
response = requests.post(
    f"{BASE_URL}/process",
    json={"topic": "AI news", "max_articles": 5}
)

articles = response.json()["articles"]

# Step 2: Save each article
for article in articles:
    save_response = requests.post(
        f"{BASE_URL}/save-news-json",
        json={"article": article}
    )
    print(f"✅ Saved: {save_response.json()['slug']}")

# Step 3: List all saved articles
list_response = requests.get(f"{BASE_URL}/list-news")
print(f"📰 Total articles: {list_response.json()['count']}")
```

## 🔍 Verify Installation

```bash
# Check Python version (need 3.10+)
python --version

# Check if agents package is installed
python -c "from agents import Agent, runner; print('✅ Agents SDK installed')"

# Check if FastAPI is installed
python -c "import fastapi; print('✅ FastAPI installed')"
```

## ⚠️ Common Issues

**Issue**: `ModuleNotFoundError: No module named 'agents'`
**Solution**: `pip install openai-agents` or `pip install agents`

**Issue**: `OPENAI_API_KEY not found`
**Solution**: Create `.env` file with `OPENAI_API_KEY=your_key`

**Issue**: Port 8000 already in use
**Solution**: Use different port: `uvicorn main:app --port 8001`

