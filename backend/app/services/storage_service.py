"""
Storage service for managing articles in a single JSON file.
All articles are stored in storage/news.json in append mode.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class StorageService:
    """Service for storing and retrieving articles from a single JSON file."""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize storage service.
        
        Args:
            storage_dir: Directory where news.json will be stored. Defaults to backend/storage/
        """
        if storage_dir is None:
            storage_dir = Path(__file__).parent.parent.parent / "storage"
        
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.news_file = self.storage_dir / "news.json"
        
        # Initialize file if it doesn't exist
        if not self.news_file.exists():
            self._initialize_file()
    
    def _initialize_file(self):
        """Initialize the news.json file with empty array."""
        try:
            with open(self.news_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)
            logger.info(f"Initialized news storage file: {self.news_file}")
        except Exception as e:
            logger.error(f"Error initializing news file: {e}")
            raise
    
    def save_article(self, article: Dict[str, Any]) -> bool:
        """
        Append a single article to news.json.
        
        Args:
            article: Article dictionary following ArticleSchema
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load existing articles
            articles = self.load_all_articles()
            
            # Check for duplicates by URL
            article_url = article.get("url", "").strip()
            if article_url:
                for existing in articles:
                    if existing.get("url", "").strip() == article_url:
                        logger.warning(f"Article with URL {article_url} already exists. Skipping.")
                        return False
            
            # Add article
            article["saved_at"] = datetime.utcnow().isoformat()
            articles.append(article)
            
            # Save back to file
            with open(self.news_file, "w", encoding="utf-8") as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved article: {article.get('title', 'Unknown')[:50]}... (slug: {article.get('slug', 'N/A')})")
            return True
            
        except Exception as e:
            logger.error(f"Error saving article: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def save_articles(self, articles: List[Dict[str, Any]]) -> int:
        """
        Append multiple articles to news.json.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Number of articles successfully saved
        """
        saved_count = 0
        for article in articles:
            if self.save_article(article):
                saved_count += 1
        
        logger.info(f"Saved {saved_count}/{len(articles)} articles")
        return saved_count
    
    def load_all_articles(self) -> List[Dict[str, Any]]:
        """
        Load all articles from news.json.
        
        Returns:
            List of all articles
        """
        try:
            if not self.news_file.exists():
                logger.warning(f"News file does not exist: {self.news_file}")
                return []
            
            with open(self.news_file, "r", encoding="utf-8") as f:
                articles = json.load(f)
            
            if not isinstance(articles, list):
                logger.error("News file does not contain a valid array. Reinitializing.")
                self._initialize_file()
                return []
            
            logger.debug(f"Loaded {len(articles)} articles from {self.news_file}")
            return articles
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing news.json: {e}")
            # Backup corrupted file
            backup_file = self.news_file.with_suffix(".json.backup")
            try:
                import shutil
                shutil.copy(self.news_file, backup_file)
                logger.info(f"Backed up corrupted file to {backup_file}")
            except:
                pass
            self._initialize_file()
            return []
        except Exception as e:
            logger.error(f"Error loading articles: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def get_articles(
        self,
        page: int = 1,
        limit: int = 50,
        reverse: bool = True
    ) -> tuple:
        """
        Get articles with pagination, sorted by published_at (newest first).
        
        Args:
            page: Page number (1-indexed)
            limit: Number of articles per page
            reverse: If True, newest first (default). If False, oldest first.
            
        Returns:
            (articles, total_count)
        """
        try:
            articles = self.load_all_articles()
            
            if not articles:
                return [], 0
            
            # Sort by published_at (newest first by default)
            articles.sort(
                key=lambda x: x.get("published_at", "") or x.get("created_at", ""),
                reverse=reverse
            )
            
            # Apply pagination
            total_count = len(articles)
            start = (page - 1) * limit
            end = start + limit
            paginated_articles = articles[start:end]
            
            logger.debug(f"Returning {len(paginated_articles)} articles (page {page}, limit {limit}, total {total_count})")
            return paginated_articles, total_count
            
        except Exception as e:
            logger.error(f"Error getting articles: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return [], 0
    
    def get_article_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Get a single article by slug.
        
        Args:
            slug: Article slug
            
        Returns:
            Article dictionary or None if not found
        """
        try:
            articles = self.load_all_articles()
            for article in articles:
                if article.get("slug", "").strip() == slug.strip():
                    return article
            return None
        except Exception as e:
            logger.error(f"Error getting article by slug: {e}")
            return None
    
    def delete_article(self, slug: str) -> bool:
        """
        Delete an article by slug.
        
        Args:
            slug: Article slug
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            articles = self.load_all_articles()
            original_count = len(articles)
            
            articles = [a for a in articles if a.get("slug", "").strip() != slug.strip()]
            
            if len(articles) == original_count:
                logger.warning(f"Article with slug '{slug}' not found")
                return False
            
            with open(self.news_file, "w", encoding="utf-8") as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Deleted article with slug: {slug}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting article: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored articles.
        
        Returns:
            Dictionary with stats
        """
        try:
            articles = self.load_all_articles()
            
            sources = {}
            for article in articles:
                source = article.get("source", "unknown")
                sources[source] = sources.get(source, 0) + 1
            
            return {
                "total_articles": len(articles),
                "sources": sources,
                "file_size": self.news_file.stat().st_size if self.news_file.exists() else 0,
                "file_path": str(self.news_file)
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "total_articles": 0,
                "sources": {},
                "file_size": 0,
                "file_path": str(self.news_file)
            }
