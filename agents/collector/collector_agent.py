"""Collector agent - fetches news from multiple sources."""
from agents.base.agent_base import BaseAgent
from typing import List, Dict, Optional
# Import from backend agents (reuse existing implementation)
import sys
from pathlib import Path

# Add backend to path to reuse existing agents
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from collector_agent import CollectorAgent as BackendCollectorAgent


class CollectorAgent(BaseAgent):
    """Collector agent wrapper."""
    
    def __init__(self):
        super().__init__("CollectorAgent")
        self.backend_agent = BackendCollectorAgent()
    
    async def collect_articles(
        self,
        topic: Optional[str] = None,
        max_articles: int = 10
    ) -> List[Dict]:
        """Collect articles from all sources."""
        return await self.backend_agent.collect_articles(topic, max_articles)
    
    async def process(self, *args, **kwargs) -> Dict:
        """Process method for base agent interface."""
        articles = await self.collect_articles(*args, **kwargs)
        return {"articles": articles}

