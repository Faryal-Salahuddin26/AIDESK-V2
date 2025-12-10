"""SEO agent - generates SEO metadata."""
from agents.base.agent_base import BaseAgent
from typing import Dict
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from seo_agent import SEOAgent as BackendSEOAgent


class SEOAgent(BaseAgent):
    """SEO agent wrapper."""
    
    def __init__(self):
        super().__init__("SEOAgent")
        self.backend_agent = BackendSEOAgent()
    
    async def generate_seo(self, title: str, content: str) -> Dict:
        """Generate SEO metadata."""
        return await self.backend_agent.generate_seo(title, content)
    
    async def process(self, title: str, content: str) -> Dict:
        """Process method for base agent interface."""
        return await self.generate_seo(title, content)

