"""News processing service."""
from typing import List, Dict, Optional
import sys
from pathlib import Path

# Add backend directory to path to import agents
backend_path = Path(__file__).parent.parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

try:
    from collector_agent import CollectorAgent
    from summary_agent import SummaryAgent
    from seo_agent import SEOAgent
except ImportError:
    # Fallback if agents not found
    CollectorAgent = None
    SummaryAgent = None
    SEOAgent = None


class NewsService:
    """Service for processing news articles."""
    
    def __init__(self):
        if CollectorAgent is None:
            raise ImportError("CollectorAgent not found. Make sure agents are properly installed.")
        self.collector = CollectorAgent()
        self.summarizer = SummaryAgent()
        self.seo_agent = SEOAgent()
    
    async def collect_news(
        self,
        topic: Optional[str] = None,
        max_articles: int = 10
    ) -> List[Dict]:
        """Collect news from multiple sources."""
        return await self.collector.collect_articles(topic, max_articles)
    
    async def generate_summaries(
        self,
        articles: List[Dict]
    ) -> List[Dict]:
        """Generate summaries for articles."""
        summarized = []
        for article in articles:
            summaries = await self.summarizer.summarize_article(article)
            article.update(summaries)
            summarized.append(article)
        return summarized
    
    async def generate_seo(
        self,
        title: str,
        content: str
    ) -> Dict:
        """Generate SEO metadata."""
        return await self.seo_agent.generate_seo(title, content)

