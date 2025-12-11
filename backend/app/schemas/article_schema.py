"""
Consistent article schema for the entire pipeline.
All articles must follow this structure.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class ArticleSchema:
    """Defines the consistent structure for all articles in the pipeline."""
    
    @staticmethod
    def create_raw_article(
        title: str,
        url: str,
        source: str,
        published_at: Optional[str] = None,
        description: Optional[str] = None,
        thumbnail: Optional[str] = None,
        video_url: Optional[str] = None,
        documentation_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a raw article structure from CollectorAgent.
        
        Returns:
            Dict with: title, url, source, published_at, description, thumbnail, video_url, documentation_url
        """
        return {
            "title": title.strip(),
            "url": url.strip(),
            "source": source.lower().strip(),
            "published_at": published_at or datetime.utcnow().isoformat(),
            "description": description.strip() if description else "",
            "thumbnail": thumbnail or "",
            "video_url": video_url or "",
            "documentation_url": documentation_url or "",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
    
    @staticmethod
    def add_summaries(
        article: Dict[str, Any],
        short_summary: str,
        long_summary: str
    ) -> Dict[str, Any]:
        """
        Add summaries to an article (from SummaryAgent).
        
        Returns:
            Article with added: short_summary, long_summary
        """
        article["short_summary"] = short_summary.strip()
        article["long_summary"] = long_summary.strip()
        article["updated_at"] = datetime.utcnow().isoformat()
        return article
    
    @staticmethod
    def add_seo(
        article: Dict[str, Any],
        meta_title: str,
        meta_description: str,
        slug: str,
        tags: List[str]
    ) -> Dict[str, Any]:
        """
        Add SEO metadata to an article (from SEOAgent).
        
        Returns:
            Article with added: meta_title, meta_description, slug, tags
        """
        article["meta_title"] = meta_title.strip()
        article["meta_description"] = meta_description.strip()
        article["slug"] = slug.strip()
        article["tags"] = [tag.strip() for tag in tags if tag.strip()]
        article["updated_at"] = datetime.utcnow().isoformat()
        return article
    
    @staticmethod
    def validate_article(article: Dict[str, Any]) -> tuple:
        """
        Validate that an article has all required fields.
        
        Returns:
            (is_valid, error_message)
        """
        required_fields = ["title", "url", "source", "slug"]
        
        for field in required_fields:
            if field not in article or not article[field]:
                return False, f"Missing required field: {field}"
        
        # Validate summaries exist
        if "short_summary" not in article or not article["short_summary"]:
            return False, "Missing required field: short_summary"
        
        if "long_summary" not in article or not article["long_summary"]:
            return False, "Missing required field: long_summary"
        
        # Validate SEO fields exist
        seo_fields = ["meta_title", "meta_description", "tags"]
        for field in seo_fields:
            if field not in article:
                return False, f"Missing required field: {field}"
        
        return True, None
    
    @staticmethod
    def get_final_article_structure() -> Dict[str, Any]:
        """
        Returns the complete structure of a final article.
        Useful for documentation and validation.
        """
        return {
            # Raw data from CollectorAgent
            "title": "string",
            "url": "string",
            "source": "string",
            "published_at": "ISO datetime string",
            "description": "string",
            "thumbnail": "string",
            "video_url": "string",
            "documentation_url": "string",
            
            # Summaries from SummaryAgent
            "short_summary": "string (100-150 chars)",
            "long_summary": "string (500-1200 words)",
            
            # SEO from SEOAgent
            "meta_title": "string (50-60 chars)",
            "meta_description": "string (150-160 chars)",
            "slug": "string (URL-friendly)",
            "tags": ["array of strings (5-10 tags)"],
            
            # Metadata
            "created_at": "ISO datetime string",
            "updated_at": "ISO datetime string",
        }

