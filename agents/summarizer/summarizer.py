"""Summarizer agent - generates article summaries."""
from agents.base.agent_base import BaseAgent
from typing import Dict
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from summary_agent import SummaryAgent as BackendSummaryAgent


class SummarizerAgent(BaseAgent):
    """Summarizer agent wrapper."""
    
    def __init__(self):
        super().__init__("SummarizerAgent")
        self.backend_agent = BackendSummaryAgent()
    
    async def summarize_article(self, article: Dict) -> Dict:
        """Generate summaries for an article."""
        return await self.backend_agent.summarize_article(article)
    
    async def process(self, article: Dict) -> Dict:
        """Process method for base agent interface."""
        return await self.summarize_article(article)

