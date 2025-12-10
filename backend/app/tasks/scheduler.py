"""Scheduled tasks for news collection."""
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.services.news_service import NewsService
from app.services.storage_service import StorageService
from app.config import settings
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def collect_and_save_news():
    """Task to collect and save news articles automatically."""
    try:
        logger.info("🤖 Starting automatic news collection...")
        
        news_service = NewsService()
        storage_service = StorageService()
        
        # Step 1: Collect news from real sources
        raw_articles = await news_service.collect_news(
            topic="AI news latest",
            max_articles=15  # Collect more to have variety
        )
        
        if not raw_articles:
            logger.warning("No articles collected from sources.")
            return
        
        logger.info(f"📰 Collected {len(raw_articles)} articles from sources")
        
        # Step 2: Generate summaries for each article
        summarized_articles = await news_service.generate_summaries(raw_articles)
        logger.info(f"📝 Generated summaries for {len(summarized_articles)} articles")
        
        # Step 3: Generate SEO and save each article
        saved_count = 0
        updated_count = 0
        for article in summarized_articles:
            try:
                # Generate SEO metadata
                seo_data = await news_service.generate_seo(
                    title=article.get("title", ""),
                    content=article.get("long_summary", "") or article.get("description", "")
                )
                
                # Combine all data
                from app.schemas.article import ArticleCreate
                final_article = ArticleCreate(
                    title=article.get("title", "Untitled"),
                    url=article.get("url", ""),
                    source=article.get("source", "unknown"),
                    published_at=article.get("published_at"),
                    short_summary=article.get("short_summary", "")[:200] if article.get("short_summary") else "",
                    long_summary=article.get("long_summary", ""),
                    meta_title=seo_data.get("meta_title", article.get("title", "")),
                    meta_description=seo_data.get("meta_description", article.get("short_summary", "")),
                    slug=seo_data.get("slug", ""),
                    tags=seo_data.get("tags", []),
                    thumbnail=article.get("thumbnail"),  # Include thumbnail from YouTube/other sources
                    description=article.get("description", "")  # Include description
                )
                
                # Check if article exists before saving
                file_path = storage_service.storage_path / f"{final_article.slug}.json"
                is_update = file_path.exists()
                
                # Save article (will update if duplicate slug exists)
                await storage_service.save_article(final_article)
                
                if is_update:
                    updated_count += 1
                    logger.info(f"🔄 Updated: {article.get('title', 'unknown')[:50]}...")
                else:
                    saved_count += 1
                    logger.info(f"✅ Saved: {article.get('title', 'unknown')[:50]}...")
                
            except Exception as e:
                logger.error(f"❌ Error processing article {article.get('title', 'unknown')}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        logger.info(f"🎉 Completed! Saved {saved_count} new articles, updated {updated_count} existing. Total processed: {len(raw_articles)}")
    except Exception as e:
        logger.error(f"❌ Error in scheduled task: {e}", exc_info=True)


def start_scheduler():
    """Start the scheduler if enabled."""
    if settings.SCHEDULER_ENABLED:
        # Add periodic job
        scheduler.add_job(
            collect_and_save_news,
            trigger=IntervalTrigger(seconds=settings.SCHEDULER_INTERVAL),
            id="collect_news",
            name="Collect and save news articles",
            replace_existing=True
        )
        scheduler.start()
        
        # Run immediately on startup (don't wait for first interval)
        # Use run_in_executor to avoid blocking
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, schedule the task
                asyncio.create_task(collect_and_save_news())
            else:
                # If loop is not running, run it
                loop.run_until_complete(collect_and_save_news())
        except RuntimeError:
            # If no event loop exists, create one
            asyncio.run(collect_and_save_news())
        
        logger.info(f"✅ Scheduler started. Running every {settings.SCHEDULER_INTERVAL} seconds (every {settings.SCHEDULER_INTERVAL // 60} minutes).")
        logger.info("🚀 Initial news collection started in background...")
    else:
        logger.info("Scheduler is disabled.")


def shutdown_scheduler():
    """Shutdown the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shut down.")

