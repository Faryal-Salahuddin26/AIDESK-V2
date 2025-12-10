"""Simple script to trigger news collection immediately."""
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

from app.tasks.scheduler import collect_and_save_news

async def main():
    """Trigger collection immediately."""
    print("Starting news collection...")
    print(f"OpenAI API Key: {'Set' if os.getenv('OPENAI_API_KEY') else 'MISSING!'}")
    print(f"YouTube API Key: {'Set' if os.getenv('YOUTUBE_API_KEY') else 'Not set'}")
    print(f"Google Search API Key: {'Set' if os.getenv('GOOGLE_SEARCH_API_KEY') else 'Not set'}")
    print()
    
    try:
        await collect_and_save_news()
        print("\nCollection completed!")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

