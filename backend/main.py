"""
AIDesk Backend - Main FastAPI Application
Refactored pipeline: Collector → Summarizer → SEO → Storage → List
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from pathlib import Path
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

# Import agents
from collector_agent import CollectorAgent
from summary_agent import SummaryAgent
from seo_agent import SEOAgent
from app.services.article_fetcher import ArticleFetcher
from app.auth import router as auth_router

# Import new services and schemas
from app.services.storage_service import StorageService
from app.schemas.article_schema import ArticleSchema

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AIDesk API",
    description="AI-powered news collection and processing platform",
    version="1.0.0"
)

# CORS settings - Allow localhost:3000 and Vercel domains
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Add Vercel preview and production domains (if configured)
vercel_url = os.getenv("NEXT_PUBLIC_SITE_URL")
if vercel_url:
    allowed_origins.append(vercel_url)

# Add CORS origins from environment variable (comma-separated)
cors_env = os.getenv("CORS_ORIGINS", "")
if cors_env:
    allowed_origins.extend([origin.strip() for origin in cors_env.split(",") if origin.strip()])

# In development, allow all origins for easier testing
# In production, use specific origins only
is_production = os.getenv("ENVIRONMENT", "development") == "production"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if is_production else ["*"],  # Allow all in dev, specific in prod
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include auth router
app.include_router(auth_router)

# Initialize storage service
storage_service = StorageService()

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
    total: int


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
            "run_full_pipeline": "/run-full-pipeline",
            "save_news": "/save-news",
            "list_news": "/list-news"
        },
        "pipeline": "Collector → Summarizer → SEO → Storage → List"
    }


@app.post("/collect-news")
async def collect_news(request: CollectNewsRequest):
    """
    Step 1: Run CollectorAgent to fetch raw news articles.
    
    Returns raw articles with consistent structure:
    - title, url, source, published_at, description, thumbnail, video_url, documentation_url
    """
    try:
        logger.info(f"Collecting news: topic='{request.topic}', max_articles={request.max_articles}")
        
        collector = CollectorAgent()
        raw_articles = await collector.collect_articles(
            topic=request.topic,
            max_articles=request.max_articles or 10
        )
        
        # Ensure consistent structure using ArticleSchema
        normalized_articles = []
        for article in raw_articles:
            normalized = ArticleSchema.create_raw_article(
                title=article.get("title", ""),
                url=article.get("url", ""),
                source=article.get("source", "unknown"),
                published_at=article.get("published_at"),
                description=article.get("description"),
                thumbnail=article.get("thumbnail"),
                video_url=article.get("video_url"),
                documentation_url=article.get("documentation_url")
            )
            normalized_articles.append(normalized)
        
        logger.info(f"✅ Collected {len(normalized_articles)} raw articles")
        
        return {
            "status": "success",
            "count": len(normalized_articles),
            "articles": normalized_articles
        }
    except Exception as e:
        logger.error(f"❌ Error collecting news: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error collecting news: {str(e)}"
        )


@app.post("/summaries")
async def generate_summaries(request: SummariesRequest):
    """
    Step 2: Run SummaryAgent to generate short and long summaries.
    
    Input: List of raw articles (from CollectorAgent)
    Output: Articles with short_summary (100-150 chars) and long_summary (500-1200 words)
    """
    try:
        logger.info(f"Generating summaries for {len(request.articles)} articles")
        
        summary_agent = SummaryAgent()
        summarized_articles = []
        
        for idx, article in enumerate(request.articles, 1):
            try:
                logger.debug(f"Summarizing article {idx}/{len(request.articles)}: {article.get('title', 'Unknown')[:50]}")
                
                summaries = await summary_agent.summarize_article(article)
                
                # Add summaries using ArticleSchema
                article_with_summaries = ArticleSchema.add_summaries(
                    article=article,
                    short_summary=summaries.get("short_summary", ""),
                    long_summary=summaries.get("long_summary", "")
                )
                
                summarized_articles.append(article_with_summaries)
                logger.debug(f"✅ Summarized: {article.get('title', 'Unknown')[:50]}")
                
            except Exception as e:
                logger.error(f"❌ Error summarizing article {article.get('title', 'unknown')}: {e}")
                continue
        
        logger.info(f"✅ Generated summaries for {len(summarized_articles)}/{len(request.articles)} articles")
        
        return {
            "status": "success",
            "count": len(summarized_articles),
            "articles": summarized_articles
        }
    except Exception as e:
        logger.error(f"❌ Error generating summaries: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summaries: {str(e)}"
        )


@app.post("/seo")
async def generate_seo(request: SEORequest):
    """
    Step 3: Run SEOAgent to generate SEO metadata.
    
    Input: title and content (long_summary)
    Output: meta_title, meta_description, slug, tags
    """
    try:
        logger.info(f"Generating SEO metadata for: {request.title[:50]}...")
        
        seo_agent = SEOAgent()
        seo_data = await seo_agent.generate_seo(
            title=request.title,
            content=request.content
        )
        
        logger.info(f"✅ Generated SEO metadata: slug={seo_data.get('slug', 'N/A')}")
        
        return {
            "status": "success",
            "seo": seo_data
        }
    except Exception as e:
        logger.error(f"❌ Error generating SEO metadata: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating SEO metadata: {str(e)}"
        )


@app.post("/save-news")
async def save_news(request: SaveNewsRequest):
    """
    Step 4: Save a processed article to storage/news.json (append mode).
    
    The article must have all required fields:
    - Raw: title, url, source, published_at
    - Summaries: short_summary, long_summary
    - SEO: meta_title, meta_description, slug, tags
    """
    try:
        article = request.article
        
        # Validate article structure
        is_valid, error_msg = ArticleSchema.validate_article(article)
        if not is_valid:
            logger.error(f"❌ Invalid article structure: {error_msg}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid article structure: {error_msg}"
            )
        
        logger.info(f"Saving article: {article.get('title', 'Unknown')[:50]}... (slug: {article.get('slug', 'N/A')})")
        
        # Save using storage service (appends to news.json)
        success = storage_service.save_article(article)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Article already exists or failed to save"
            )
        
        logger.info(f"✅ Saved article: {article.get('slug', 'N/A')}")
        
        return {
            "status": "success",
            "message": "Article saved successfully",
            "slug": article.get("slug"),
            "file_path": str(storage_service.news_file)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error saving article: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error saving article: {str(e)}"
        )


@app.get("/list-news", response_model=NewsListResponse)
async def list_news(page: int = 1, limit: int = 50):
    """
    Step 5: List all articles from storage/news.json.
    
    Returns articles in reverse chronological order (newest first).
    Supports pagination.
    """
    try:
        logger.info(f"Listing news: page={page}, limit={limit}")
        
        # Get articles from storage service (already sorted newest first)
        articles, total_count = storage_service.get_articles(
            page=page,
            limit=limit,
            reverse=True  # Newest first
        )
        
        logger.info(f"✅ Returning {len(articles)} articles (page {page}, total {total_count})")
        
        return {
            "articles": articles,
            "count": len(articles),
            "total": total_count
        }
    except Exception as e:
        logger.error(f"❌ Error listing news: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error listing news: {str(e)}"
        )


async def process_all_news(topic: Optional[str] = None, max_articles: int = 20):
    """
    Master pipeline function that processes all news articles sequentially.
    
    Flow:
    1. Collect raw articles
    2. For each article:
       - Generate summaries
       - Generate SEO metadata
       - Merge all data into schema
       - Save article
    
    Args:
        topic: Search topic (default: "AI news latest")
        max_articles: Maximum number of articles to process
    
    Returns:
        Dict with status, count, saved count, and errors
    """
    try:
        logger.info(f"🚀 Starting master pipeline: topic='{topic}', max_articles={max_articles}")
        
        # Step 1: Collect raw articles
        logger.info("Step 1: Collecting raw articles...")
        collector = CollectorAgent()
        raw_articles = await collector.collect_articles(
            topic=topic or "AI news latest",
            max_articles=max_articles
        )
        
        if not raw_articles:
            logger.warning("No articles collected")
            return {
                "status": "success",
                "count": 0,
                "saved": 0,
                "errors": []
            }
        
        logger.info(f"✅ Collected {len(raw_articles)} raw articles")
        
        # Initialize agents
        summary_agent = SummaryAgent()
        seo_agent = SEOAgent()
        
        # Process each article sequentially
        saved_count = 0
        errors = []
        
        for idx, article in enumerate(raw_articles, 1):
            try:
                logger.info(f"Processing article {idx}/{len(raw_articles)}: {article.get('title', 'Unknown')[:50]}...")
                
                # Normalize raw article
                normalized = ArticleSchema.create_raw_article(
                    title=article.get("title", ""),
                    url=article.get("url", ""),
                    source=article.get("source", "unknown"),
                    published_at=article.get("published_at"),
                    description=article.get("description") or article.get("content", ""),
                    thumbnail=article.get("thumbnail"),
                    video_url=article.get("video_url"),
                    documentation_url=article.get("documentation_url")
                )
                
                # Step 2: Generate summaries
                logger.debug(f"  → Generating summaries...")
                summaries = await summary_agent.summarize_article(normalized)
                article_with_summaries = ArticleSchema.add_summaries(
                    article=normalized,
                    short_summary=summaries.get("short_summary", ""),
                    long_summary=summaries.get("long_summary", "")
                )
                
                # Step 3: Generate SEO metadata
                logger.debug(f"  → Generating SEO metadata...")
                seo_data = await seo_agent.generate_seo(
                    title=article_with_summaries.get("title", ""),
                    content=article_with_summaries.get("long_summary", "") or article_with_summaries.get("description", "")
                )
                
                # Step 4: Merge all data into final schema
                logger.debug(f"  → Merging data...")
                final_article = ArticleSchema.add_seo(
                    article=article_with_summaries,
                    meta_title=seo_data.get("meta_title", ""),
                    meta_description=seo_data.get("meta_description", ""),
                    slug=seo_data.get("slug", ""),
                    tags=seo_data.get("tags", [])
                )
                
                # Step 5: Save article
                logger.debug(f"  → Saving article...")
                try:
                    success = storage_service.save_article(final_article)
                    if success:
                        saved_count += 1
                        logger.info(f"  ✅ Saved: {final_article.get('slug', 'N/A')}")
                    else:
                        logger.warning(f"  ⚠️ Article already exists or failed to save: {final_article.get('slug', 'N/A')}")
                except Exception as save_error:
                    logger.error(f"  ❌ Error saving article: {save_error}")
                    errors.append({
                        "article": article.get("title", "Unknown"),
                        "step": "save",
                        "error": str(save_error)
                    })
                
            except Exception as e:
                logger.error(f"❌ Error processing article {article.get('title', 'unknown')}: {e}", exc_info=True)
                errors.append({
                    "article": article.get("title", "Unknown"),
                    "step": "process",
                    "error": str(e)
                })
                continue
        
        logger.info(f"🎉 Master pipeline complete! Processed {len(raw_articles)} articles, saved {saved_count}, errors: {len(errors)}")
        
        return {
            "status": "success",
            "count": len(raw_articles),
            "saved": saved_count,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"❌ Error in master pipeline: {e}", exc_info=True)
        return {
            "status": "error",
            "count": 0,
            "saved": 0,
            "errors": [{"step": "pipeline", "error": str(e)}]
        }


@app.post("/run-full-pipeline")
async def run_full_pipeline(request: ProcessRequest):
    """
    Endpoint to manually trigger the master pipeline.
    
    This runs the complete pipeline:
    - Collect news
    - Generate summaries for each article
    - Generate SEO metadata for each article
    - Save each article
    
    Returns:
        Dict with status, count, saved count, and any errors
    """
    try:
        logger.info(f"📞 Manual pipeline trigger: topic='{request.topic}', max_articles={request.max_articles}")
        
        result = await process_all_news(
            topic=request.topic,
            max_articles=request.max_articles or 20
        )
        
        return {
            "status": result["status"],
            "message": f"Pipeline completed. Processed {result['count']} articles, saved {result['saved']}.",
            "count": result["count"],
            "saved": result["saved"],
            "errors": result["errors"],
            "error_count": len(result["errors"])
        }
    except Exception as e:
        logger.error(f"❌ Error in manual pipeline trigger: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error running pipeline: {str(e)}"
        )


@app.post("/process")
async def process_news(request: ProcessRequest):
    """
    Complete pipeline: Collector → Summarizer → SEO → Save
    
    Runs all agents in sequence and saves articles to storage/news.json.
    Returns fully processed articles.
    """
    try:
        logger.info(f"🚀 Starting complete pipeline: topic='{request.topic}', max_articles={request.max_articles}")
        
        # Step 1: Collect raw articles
        logger.info("Step 1/4: Collecting raw articles...")
        collector = CollectorAgent()
        raw_articles = await collector.collect_articles(
            topic=request.topic,
            max_articles=request.max_articles or 10
        )
        
        if not raw_articles:
            logger.warning("No articles collected")
            return {
                "status": "success",
                "count": 0,
                "articles": [],
                "saved": 0
            }
        
        # Normalize raw articles
        normalized_articles = []
        for article in raw_articles:
            normalized = ArticleSchema.create_raw_article(
                title=article.get("title", ""),
                url=article.get("url", ""),
                source=article.get("source", "unknown"),
                published_at=article.get("published_at"),
                description=article.get("description"),
                thumbnail=article.get("thumbnail"),
                video_url=article.get("video_url"),
                documentation_url=article.get("documentation_url")
            )
            normalized_articles.append(normalized)
        
        logger.info(f"✅ Collected {len(normalized_articles)} raw articles")
        
        # Step 2: Generate summaries
        logger.info("Step 2/4: Generating summaries...")
        summary_agent = SummaryAgent()
        summarized_articles = []
        
        for idx, article in enumerate(normalized_articles, 1):
            try:
                logger.debug(f"Summarizing {idx}/{len(normalized_articles)}: {article.get('title', 'Unknown')[:50]}")
                summaries = await summary_agent.summarize_article(article)
                
                article_with_summaries = ArticleSchema.add_summaries(
                    article=article,
                    short_summary=summaries.get("short_summary", ""),
                    long_summary=summaries.get("long_summary", "")
                )
                summarized_articles.append(article_with_summaries)
            except Exception as e:
                logger.error(f"❌ Error summarizing article {article.get('title', 'unknown')}: {e}")
                continue
        
        logger.info(f"✅ Generated summaries for {len(summarized_articles)} articles")
        
        # Step 3: Generate SEO metadata
        logger.info("Step 3/4: Generating SEO metadata...")
        seo_agent = SEOAgent()
        final_articles = []
        
        for idx, article in enumerate(summarized_articles, 1):
            try:
                logger.debug(f"Generating SEO {idx}/{len(summarized_articles)}: {article.get('title', 'Unknown')[:50]}")
                seo_data = await seo_agent.generate_seo(
                    title=article.get("title", ""),
                    content=article.get("long_summary", "")
                )
                
                final_article = ArticleSchema.add_seo(
                    article=article,
                    meta_title=seo_data.get("meta_title", ""),
                    meta_description=seo_data.get("meta_description", ""),
                    slug=seo_data.get("slug", ""),
                    tags=seo_data.get("tags", [])
                )
                
                final_articles.append(final_article)
            except Exception as e:
                logger.error(f"❌ Error generating SEO for article {article.get('title', 'unknown')}: {e}")
                continue
        
        logger.info(f"✅ Generated SEO metadata for {len(final_articles)} articles")
        
        # Step 4: Save articles
        logger.info("Step 4/4: Saving articles to storage/news.json...")
        saved_count = storage_service.save_articles(final_articles)
        
        logger.info(f"🎉 Pipeline complete! Processed {len(final_articles)} articles, saved {saved_count}")
        
        return {
            "status": "success",
            "count": len(final_articles),
            "articles": final_articles,
            "saved": saved_count
        }
    except Exception as e:
        logger.error(f"❌ Error in pipeline: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing news: {str(e)}"
        )


@app.get("/news/{slug}")
async def get_news_by_slug(slug: str, fetch_content: bool = False):
    """
    Get a specific article by slug from storage/news.json.
    If fetch_content=True, fetches and includes full article content from URL.
    """
    try:
        logger.info(f"Getting article by slug: {slug}, fetch_content={fetch_content}")
        
        article = storage_service.get_article_by_slug(slug)
        
        if not article:
            raise HTTPException(
                status_code=404,
                detail=f"Article with slug '{slug}' not found"
            )
        
        # Fetch full article content if requested
        if fetch_content and article.get("url"):
            try:
                logger.info(f"Fetching full content for: {article.get('url')}")
                fetcher = ArticleFetcher()
                fetched_content = fetcher.fetch_article_content(
                    url=article.get("url"),
                    title=article.get("title", ""),
                    description=article.get("description", "") or article.get("short_summary", "")
                )
                
                # Add fetched content
                article["full_content"] = fetched_content.get("content", "")
                article["html_content"] = fetched_content.get("html_content")
                article["is_video"] = fetched_content.get("is_video", False)
                article["images"] = fetched_content.get("images", [])
                article["links"] = fetched_content.get("links", [])
                article["source_url"] = fetched_content.get("source_url", article.get("url", ""))
                article["content_length"] = fetched_content.get("content_length", len(fetched_content.get("content", "")))
                article["content_fetched"] = True
                
                logger.info(f"✅ Fetched content: {article['content_length']} chars, {len(article.get('images', []))} images")
            except Exception as e:
                logger.error(f"❌ Error fetching article content: {e}")
                article["content_fetched"] = False
                article["fetch_error"] = str(e)
        
        return article
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting article: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error reading article: {str(e)}"
        )


@app.get("/stats")
async def get_stats():
    """Get statistics about stored articles."""
    try:
        stats = storage_service.get_stats()
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error getting stats: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
