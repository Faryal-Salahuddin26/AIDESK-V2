"""Simple script to collect news immediately without scheduler dependency."""
import asyncio
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.services.news_service import NewsService
from app.services.storage_service import StorageService
from app.schemas.article import ArticleCreate

async def main():
    """Collect and save news immediately."""
    print("=" * 70)
    print("AI DESK - News Collection")
    print("=" * 70)
    print()
    
    # Check API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    google_key = os.getenv('GOOGLE_SEARCH_API_KEY')
    
    print("API Keys Status:")
    print(f"  OpenAI: {'SET' if openai_key else 'MISSING - REQUIRED!'}")
    print(f"  YouTube: {'SET' if youtube_key else 'Not set (optional)'}")
    print(f"  Google Search: {'SET' if google_key else 'Not set (optional)'}")
    print()
    
    if not openai_key:
        print("ERROR: OPENAI_API_KEY is required!")
        print("Please set it in your .env file")
        return
    
    try:
        news_service = NewsService()
        storage_service = StorageService()
        
        # Step 1: Collect news
        print("Step 1: Collecting articles from sources...")
        print("-" * 70)
        raw_articles = await news_service.collect_news(
            topic="AI news latest",
            max_articles=15
        )
        
        if not raw_articles:
            print("WARNING: No articles collected from sources!")
            print("This might be due to:")
            print("  - RSS feeds not accessible")
            print("  - API rate limits")
            print("  - Network issues")
            return
        
        print(f"SUCCESS: Collected {len(raw_articles)} raw articles")
        for i, article in enumerate(raw_articles[:5], 1):
            print(f"  {i}. {article.get('title', 'No title')[:60]}...")
        if len(raw_articles) > 5:
            print(f"  ... and {len(raw_articles) - 5} more")
        print()
        
        # Step 2: Generate summaries
        print("Step 2: Generating summaries using OpenAI...")
        print("-" * 70)
        summarized_articles = await news_service.generate_summaries(raw_articles)
        print(f"SUCCESS: Generated summaries for {len(summarized_articles)} articles")
        print()
        
        # Step 3: Generate SEO and save
        print("Step 3: Generating SEO metadata and saving articles...")
        print("-" * 70)
        saved_count = 0
        updated_count = 0
        
        for article in summarized_articles:
            try:
                # Generate SEO metadata
                seo_data = await news_service.generate_seo(
                    title=article.get("title", ""),
                    content=article.get("long_summary", "") or article.get("description", "")
                )
                
                # Create final article
                # Convert published_at to datetime if it's a string
                published_at = article.get("published_at")
                if isinstance(published_at, str):
                    try:
                        from dateutil import parser as date_parser
                        published_at = date_parser.parse(published_at)
                    except:
                        from datetime import datetime
                        published_at = datetime.now()
                elif published_at is None:
                    from datetime import datetime
                    published_at = datetime.now()
                
                final_article = ArticleCreate(
                    title=article.get("title", "Untitled"),
                    url=article.get("url", ""),
                    source=article.get("source", "unknown"),
                    published_at=published_at,
                    short_summary=article.get("short_summary", "")[:200] if article.get("short_summary") else "",
                    long_summary=article.get("long_summary", ""),
                    meta_title=seo_data.get("meta_title", article.get("title", "")),
                    meta_description=seo_data.get("meta_description", article.get("short_summary", "")),
                    slug=seo_data.get("slug", ""),
                    tags=seo_data.get("tags", []),
                    thumbnail=article.get("thumbnail"),
                    description=article.get("description", ""),
                    video_url=article.get("video_url"),  # YouTube video URL
                    documentation_url=article.get("documentation_url")  # Official documentation URL
                )
                
                # Check if exists
                file_path = storage_service.storage_path / f"{final_article.slug}.json"
                is_update = file_path.exists()
                
                # Save article
                await storage_service.save_article(final_article)
                
                if is_update:
                    updated_count += 1
                    print(f"  Updated: {final_article.title[:55]}...")
                else:
                    saved_count += 1
                    print(f"  Saved: {final_article.title[:55]}...")
                
            except Exception as e:
                print(f"  ERROR processing article: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print()
        print("=" * 70)
        print(f"COMPLETED!")
        print(f"  New articles saved: {saved_count}")
        print(f"  Articles updated: {updated_count}")
        print(f"  Total processed: {len(summarized_articles)}")
        print("=" * 70)
        
        # Check storage
        storage_files = list(storage_service.storage_path.glob("*.json"))
        print(f"\nStorage directory now contains {len(storage_files)} articles")
        print(f"Location: {storage_service.storage_path}")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

