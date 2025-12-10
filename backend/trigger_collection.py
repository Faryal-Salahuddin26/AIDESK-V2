"""Script to manually trigger news collection."""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.tasks.scheduler import collect_and_save_news

async def main():
    print("🚀 Triggering news collection...")
    print("=" * 60)
    try:
        await collect_and_save_news()
        print("=" * 60)
        print("✅ Collection completed!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

