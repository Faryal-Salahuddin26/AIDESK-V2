from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from pathlib import Path
from dotenv import load_dotenv
import os
from agents.agent import Agent
from agents.run import AgentRunner
from agents.tool import function_tool

from collector_agent import CollectorAgent
from summary_agent import SummaryAgent
from seo_agent import SEOAgent
from app.services.article_fetcher import ArticleFetcher

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="AIDesk API",
    description="AI-powered news collection and processing platform",
    version="1.0.0"
)

# CORS settings - Allow all origins for development
# In production, specify exact origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# News data directory - use the correct storage path
# Try backend/storage/news-data first, then fallback to old path
NEWS_DATA_DIR = Path(__file__).parent / "storage" / "news-data"
if not NEWS_DATA_DIR.exists():
    # Fallback to old path for compatibility
    NEWS_DATA_DIR = Path(__file__).parent.parent / "aidesk" / "public" / "news-data"
NEWS_DATA_DIR.mkdir(parents=True, exist_ok=True)


# Request/Response Models
class CollectNewsRequest(BaseModel):
    topic: Optional[str] = None
    max_articles: Optional[int] = 10


class SummariesRequest(BaseModel):
    articles: List[Dict[str, Any]]


class SEORequest(BaseModel):
    title: str
    content: str


class ProcessRequest(BaseModel):
    topic: Optional[str] = None
    max_articles: Optional[int] = 10


class SaveNewsRequest(BaseModel):
    article: Dict[str, Any]


class NewsListResponse(BaseModel):
    articles: List[Dict[str, Any]]
    count: int


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "AIDesk API",
        "version": "1.0.0",
        "endpoints": {
            "collect_news": "/collect-news",
            "summaries": "/summaries",
            "seo": "/seo",
            "process": "/process",
            "save_news_json": "/save-news-json",
            "list_news": "/list-news"
        }
    }


@app.post("/collect-news")
async def collect_news(request: CollectNewsRequest):
    """
    Run CollectorAgent to fetch news from multiple sources:
    - YouTube news
    - Forbes articles
    - Web search
    - Official websites
    
    Returns raw articles with: title, url, source, published_at
    """
    try:
        collector = CollectorAgent()
        articles = await collector.collect_articles(
            topic=request.topic,
            max_articles=request.max_articles or 10
        )
        
        return {
            "status": "success",
            "count": len(articles),
            "articles": articles
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error collecting news: {str(e)}"
        )


@app.post("/summaries")
async def generate_summaries(request: SummariesRequest):
    """
    Run SummaryAgent to generate short and long summaries for articles.
    
    Input: List of raw articles (from CollectorAgent)
    Output: Articles with short_summary (100-150 chars) and long_summary (500-1200 words)
    """
    try:
        summary_agent = SummaryAgent()
        summarized_articles = []
        
        for article in request.articles:
            try:
                summaries = await summary_agent.summarize_article(article)
                article_with_summaries = {
                    **article,
                    "short_summary": summaries.get("short_summary", ""),
                    "long_summary": summaries.get("long_summary", "")
                }
                summarized_articles.append(article_with_summaries)
            except Exception as e:
                print(f"Error summarizing article {article.get('title', 'unknown')}: {str(e)}")
                continue
        
        return {
            "status": "success",
            "count": len(summarized_articles),
            "articles": summarized_articles
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summaries: {str(e)}"
        )


@app.post("/seo")
async def generate_seo(request: SEORequest):
    """
    Run SEOAgent to generate SEO metadata for an article.
    
    Input: title and content
    Output: meta_title, meta_description, slug, tags
    """
    try:
        seo_agent = SEOAgent()
        seo_data = await seo_agent.generate_seo(
            title=request.title,
            content=request.content
        )
        
        return {
            "status": "success",
            "seo": seo_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating SEO metadata: {str(e)}"
        )


@app.post("/process")
async def process_news(request: ProcessRequest):
    """
    Run all agents in pipeline:
    1. CollectorAgent - Fetch news
    2. SummaryAgent - Generate summaries
    3. SEOAgent - Generate SEO metadata
    
    Returns fully processed articles ready to save.
    """
    try:
        # Step 1: Collect news
        collector = CollectorAgent()
        raw_articles = await collector.collect_articles(
            topic=request.topic,
            max_articles=request.max_articles or 10
        )
        
        if not raw_articles:
            return {
                "status": "success",
                "count": 0,
                "articles": []
            }
        
        # Step 2: Generate summaries
        summary_agent = SummaryAgent()
        summarized_articles = []
        
        for article in raw_articles:
            try:
                summaries = await summary_agent.summarize_article(article)
                article_with_summaries = {
                    **article,
                    "short_summary": summaries.get("short_summary", ""),
                    "long_summary": summaries.get("long_summary", "")
                }
                summarized_articles.append(article_with_summaries)
            except Exception as e:
                print(f"Error summarizing article {article.get('title', 'unknown')}: {str(e)}")
                continue
        
        # Step 3: Generate SEO metadata
        seo_agent = SEOAgent()
        final_articles = []
        
        for article in summarized_articles:
            try:
                seo_data = await seo_agent.generate_seo(
                    title=article.get("title", ""),
                    content=article.get("long_summary", "")
                )
                
                final_article = {
                    **article,
                    "meta_title": seo_data.get("meta_title", ""),
                    "meta_description": seo_data.get("meta_description", ""),
                    "slug": seo_data.get("slug", ""),
                    "tags": seo_data.get("tags", [])
                }
                
                final_articles.append(final_article)
            except Exception as e:
                print(f"Error generating SEO for article {article.get('title', 'unknown')}: {str(e)}")
                continue
        
        return {
            "status": "success",
            "count": len(final_articles),
            "articles": final_articles
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing news: {str(e)}"
        )


@app.post("/save-news-json")
async def save_news_json(request: SaveNewsRequest):
    """
    Save a processed article to JSON file.
    
    The article must have a 'slug' field which will be used as the filename.
    """
    try:
        article = request.article
        
        if "slug" not in article or not article["slug"]:
            raise HTTPException(
                status_code=400,
                detail="Article must have a 'slug' field"
            )
        
        slug = article["slug"]
        file_path = NEWS_DATA_DIR / f"{slug}.json"
        
        # Save article to JSON file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(article, f, indent=2, ensure_ascii=False)
        
        return {
            "status": "success",
            "message": f"Article saved successfully",
            "slug": slug,
            "file_path": str(file_path)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving article: {str(e)}"
        )


@app.get("/list-news", response_model=NewsListResponse)
async def list_news(page: int = 1, limit: int = 50):
    """
    List all JSON files in the news-data folder.
    
    Returns all saved articles with metadata.
    Supports pagination with page and limit parameters.
    """
    try:
        articles = []
        
        if not NEWS_DATA_DIR.exists():
            print(f"Warning: News data directory does not exist: {NEWS_DATA_DIR}")
            return {
                "articles": [],
                "count": 0
            }
        
        # Read all JSON files
        json_files = list(NEWS_DATA_DIR.glob("*.json"))
        print(f"Found {len(json_files)} JSON files in {NEWS_DATA_DIR}")
        
        for file_path in json_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    article = json.load(f)
                    articles.append(article)
            except Exception as e:
                print(f"Error reading {file_path}: {str(e)}")
                continue
        
        # Remove duplicates based on URL and title
        seen_urls = set()
        seen_titles_normalized = set()
        unique_articles = []
        
        for article in articles:
            url = article.get("url", "").strip()
            title = article.get("title", "").strip()
            
            # Skip if URL already seen
            if url and url in seen_urls:
                continue
            
            # Normalize title for comparison
            import re
            title_normalized = re.sub(r'[^\w\s]', '', title.lower().strip())
            
            # Skip if very similar title exists
            is_duplicate = False
            for seen_title in seen_titles_normalized:
                if title_normalized == seen_title:
                    is_duplicate = True
                    break
                # Check word overlap
                title_words = set(title_normalized.split())
                seen_words = set(seen_title.split())
                if len(title_words) > 0 and len(seen_words) > 0:
                    similarity = len(title_words & seen_words) / len(title_words | seen_words)
                    if similarity > 0.85:  # 85% similarity threshold
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                if url:
                    seen_urls.add(url)
                seen_titles_normalized.add(title_normalized)
                unique_articles.append(article)
        
        print(f"Deduplication: {len(articles)} articles -> {len(unique_articles)} unique articles")
        
        # Sort by published_at (newest first)
        unique_articles.sort(
            key=lambda x: x.get("published_at", "") or x.get("created_at", ""),
            reverse=True
        )
        
        # Apply pagination
        start = (page - 1) * limit
        end = start + limit
        paginated_articles = unique_articles[start:end]
        
        print(f"Returning {len(paginated_articles)} articles (page {page}, limit {limit}, total {len(unique_articles)})")
        
        return {
            "articles": paginated_articles,
            "count": len(paginated_articles)
        }
    except Exception as e:
        print(f"Error in list_news: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error listing news: {str(e)}"
        )


@app.get("/news/{slug}")
async def get_news_by_slug(slug: str, fetch_content: bool = False):
    """
    Get a specific article by slug.
    If fetch_content=True, fetches and includes full article content from URL.
    """
    file_path = NEWS_DATA_DIR / f"{slug}.json"
    
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Article with slug '{slug}' not found"
        )
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            article = json.load(f)
        
        # Fetch full article content if requested
        if fetch_content and article.get("url"):
            try:
                fetcher = ArticleFetcher()
                fetched_content = fetcher.fetch_article_content(
                    url=article.get("url"),
                    title=article.get("title", ""),
                    description=article.get("description", "") or article.get("short_summary", "")
                )
                
                # Add fetched content to article - ALL original content
                article["full_content"] = fetched_content.get("content", "")
                article["html_content"] = fetched_content.get("html_content")
                article["is_video"] = fetched_content.get("is_video", False)
                article["images"] = fetched_content.get("images", [])
                article["links"] = fetched_content.get("links", [])
                article["source_url"] = fetched_content.get("source_url", article.get("url", ""))
                article["content_length"] = fetched_content.get("content_length", len(fetched_content.get("content", "")))
                article["content_fetched"] = True
                
                print(f"✅ Fetched complete content: {article['content_length']} characters, {len(article.get('images', []))} images, {len(article.get('links', []))} links")
                
                if fetched_content.get("error"):
                    print(f"Warning fetching article content: {fetched_content.get('error')}")
            except Exception as e:
                print(f"Error fetching article content: {e}")
                import traceback
                traceback.print_exc()
                article["content_fetched"] = False
                article["fetch_error"] = str(e)
        
        return article
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading article: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
