# AIDesk Backend - FastAPI with OpenAI Agents SDK 2025

AI-powered news collection and processing backend using FastAPI and OpenAI Agents SDK 2025.

## 🎯 Overview

AIDesk automatically fetches news from multiple sources (YouTube, Forbes, web search), uses AI agents to filter and summarize content, and generates SEO-friendly articles stored as JSON files.

## 🚀 Features

- **Multi-Source News Collection**: YouTube, Forbes, web search, official websites
- **AI-Powered Processing**: Three specialized agents for collection, summarization, and SEO
- **No Database**: All data stored as JSON files
- **RESTful API**: Clean FastAPI endpoints
- **CORS Enabled**: Ready for frontend integration

## 📋 Requirements

- Python 3.10+
- OpenAI API Key
- OpenAI Agents SDK 2025

## 🛠️ Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install OpenAI Agents SDK 2025

```bash
# Option 1: If package is named 'openai-agents'
pip install openai-agents

# Option 2: If package is named 'agents'
pip install agents
```

**Important**: The package must support:
- `from agents import Agent, runner`
- `from agents import functional_tool`
- `@functional_tool` decorator

### 3. Set Environment Variables

Create a `.env` file in the `backend/` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Run the Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### Root
- **GET** `/` - API information and available endpoints

### News Collection
- **POST** `/collect-news` - Run CollectorAgent to fetch news from multiple sources
- **POST** `/summaries` - Run SummaryAgent to generate article summaries
- **POST** `/seo` - Run SEOAgent to generate SEO metadata
- **POST** `/process` - Run all agents in pipeline (collect → summarize → SEO)

### Data Management
- **POST** `/save-news-json` - Save a processed article to JSON file
- **GET** `/list-news` - List all saved articles from JSON files
- **GET** `/news/{slug}` - Get a specific article by slug

## 📖 API Documentation

### Interactive Docs
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔧 Endpoint Details

### POST /collect-news

Collect news from multiple sources using CollectorAgent.

**Request Body:**
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
      "title": "Article Title",
      "url": "https://example.com/article",
      "source": "youtube",
      "published_at": "2025-01-01T12:00:00"
    }
  ]
}
```

### POST /summaries

Generate summaries for articles using SummaryAgent.

**Request Body:**
```json
{
  "articles": [
    {
      "title": "Article Title",
      "url": "https://example.com/article",
      "source": "youtube",
      "published_at": "2025-01-01T12:00:00"
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
      "title": "Article Title",
      "url": "https://example.com/article",
      "source": "youtube",
      "published_at": "2025-01-01T12:00:00",
      "short_summary": "Brief summary (100-150 chars)...",
      "long_summary": "Detailed summary (500-1200 words)..."
    }
  ]
}
```

### POST /seo

Generate SEO metadata using SEOAgent.

**Request Body:**
```json
{
  "title": "Article Title",
  "content": "Article content or long summary..."
}
```

**Response:**
```json
{
  "status": "success",
  "seo": {
    "meta_title": "SEO Optimized Title (50-60 chars)",
    "meta_description": "SEO description (150-160 chars)...",
    "slug": "article-title",
    "tags": ["AI", "machine learning", "technology"]
  }
}
```

### POST /process

Run the complete pipeline: collect → summarize → SEO.

**Request Body:**
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
      "title": "Article Title",
      "url": "https://example.com/article",
      "source": "youtube",
      "published_at": "2025-01-01T12:00:00",
      "short_summary": "Brief summary...",
      "long_summary": "Detailed summary...",
      "meta_title": "SEO Title",
      "meta_description": "SEO description...",
      "slug": "article-title",
      "tags": ["AI", "technology"]
    }
  ]
}
```

### POST /save-news-json

Save a processed article to JSON file.

**Request Body:**
```json
{
  "article": {
    "title": "Article Title",
    "slug": "article-title",
    "url": "https://example.com/article",
    "short_summary": "...",
    "long_summary": "...",
    "meta_title": "...",
    "meta_description": "...",
    "tags": ["AI"],
    "source": "youtube",
    "published_at": "2025-01-01T12:00:00"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Article saved successfully",
  "slug": "article-title",
  "file_path": "/path/to/article-title.json"
}
```

### GET /list-news

List all saved articles.

**Response:**
```json
{
  "articles": [
    {
      "title": "Article Title",
      "slug": "article-title",
      ...
    }
  ],
  "count": 10
}
```

### GET /news/{slug}

Get a specific article by slug.

**Response:**
```json
{
  "title": "Article Title",
  "slug": "article-title",
  ...
}
```

## 🤖 AI Agents

### CollectorAgent
- Fetches news from YouTube (RSS/API)
- Fetches Forbes articles
- Performs web search
- Cleans article titles
- Removes duplicates

**Tools:**
- `fetch_youtube_news(query, max_results)`
- `fetch_forbes_articles(query, max_results)`
- `web_search_articles(query, max_results)`
- `clean_title(title)`
- `remove_duplicates(articles)`

### SummaryAgent
- Generates short summary (100-150 characters)
- Generates long summary (500-1200 words)

**Tools:**
- `generate_short_summary(title, content)`
- `generate_long_summary(title, content)`

### SEOAgent
- Generates SEO-optimized meta title (50-60 chars)
- Generates meta description (150-160 chars)
- Creates URL-friendly slug
- Extracts relevant tags (5-10 tags)

**Tools:**
- `generate_slug(title)`
- `extract_tags(title, content)`

## 📁 Project Structure

```
backend/
├── main.py              # FastAPI application and endpoints
├── collector_agent.py   # CollectorAgent implementation
├── summary_agent.py     # SummaryAgent implementation
├── seo_agent.py        # SEOAgent implementation
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── .env                # Environment variables (create this)
```

## 🔒 CORS Configuration

CORS is configured to allow all origins in development. For production, update `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📝 Usage Examples

### Complete Pipeline

```bash
# 1. Collect news
curl -X POST http://localhost:8000/collect-news \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI news", "max_articles": 5}'

# 2. Process complete pipeline (recommended)
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI news", "max_articles": 5}'

# 3. Save articles
# Use the response from /process and save each article
curl -X POST http://localhost:8000/save-news-json \
  -H "Content-Type: application/json" \
  -d '{"article": {...}}'

# 4. List all saved articles
curl http://localhost:8000/list-news
```

### Python Example

```python
import requests

# Process news
response = requests.post(
    "http://localhost:8000/process",
    json={"topic": "AI news", "max_articles": 5}
)

articles = response.json()["articles"]

# Save each article
for article in articles:
    save_response = requests.post(
        "http://localhost:8000/save-news-json",
        json={"article": article}
    )
    print(f"Saved: {save_response.json()['slug']}")
```

## 🚨 Important Notes

### OpenAI Agents SDK 2025 Requirements

**✅ MUST USE:**
- `from agents import Agent, runner`
- `from agents import functional_tool`
- `@functional_tool` decorator
- `Agent()` class
- `runner.run()` method

**❌ MUST NOT USE:**
- ChatCompletion API
- Swarm
- Deprecated assistant API
- `.agents` folder structure

### Storage

- All articles are saved as JSON files in `../aidesk/public/news-data/`
- Each article is saved as `{slug}.json`
- No database required - pure file-based storage

## 🐛 Troubleshooting

### Import Error: No module named 'agents'

```bash
# Try installing the OpenAI Agents SDK
pip install openai-agents
# OR
pip install agents
```

### OpenAI API Key Error

- Ensure `.env` file exists in `backend/` directory
- Verify `OPENAI_API_KEY` is set correctly
- Check API key has sufficient credits

### Path Errors

- Ensure the directory structure is correct
- The backend saves to `../aidesk/public/news-data/`
- Create the directory if it doesn't exist

## 🚀 Deployment

### Render

1. Connect GitHub repository
2. Set environment variable: `OPENAI_API_KEY`
3. Use `render.yaml` configuration
4. Deploy

### Fly.io

1. Install Fly CLI
2. Run: `fly launch` (uses `fly.toml`)
3. Set secrets: `fly secrets set OPENAI_API_KEY=your_key`
4. Deploy: `fly deploy`

### Vercel

1. Connect repository
2. Set environment variables
3. Use `vercel.json` configuration
4. Deploy

## 📄 License

MIT License

## 🙏 Acknowledgments

- Built with FastAPI
- Powered by OpenAI Agents SDK 2025
- Inspired by CoinDesk
