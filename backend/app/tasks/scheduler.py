"""Scheduled tasks for news collection."""
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.config import settings
import logging
import sys
from pathlib import Path

# Add parent directory to path to import main module functions
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def collect_and_save_news():
    """
    Scheduled task that runs the master pipeline every 10 minutes.
    This calls the process_all_news() function from main.py
    """
    try:
        logger.info("🤖 Starting scheduled news collection pipeline...")
        
        # Import the master pipeline function from main.py
        from main import process_all_news
        
        # Run the master pipeline
        result = await process_all_news(
            topic="AI news latest",
            max_articles=20
        )
        
        logger.info(f"🎉 Scheduled pipeline complete! Processed {result['count']} articles, saved {result['saved']}, errors: {len(result.get('errors', []))}")
        
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

