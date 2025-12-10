"""Storage service for articles."""
import json
from pathlib import Path
from typing import List, Optional, Dict
from app.schemas.article import ArticleCreate, ArticleResponse
from app.config import settings


class StorageService:
    """Service for storing and retrieving articles."""
    
    def __init__(self):
        # Handle both relative and absolute paths
        storage_path = settings.STORAGE_PATH
        if not Path(storage_path).is_absolute():
            # Relative to project root
            project_root = Path(__file__).parent.parent.parent
            self.storage_path = project_root / storage_path
        else:
            self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def save_article(self, article: ArticleCreate) -> Dict:
        """Save article to JSON file. Updates if article with same slug already exists."""
        if not article.slug:
            raise ValueError("Article must have a slug")
        
        from datetime import datetime
        
        file_path = self.storage_path / f"{article.slug}.json"
        
        # Check if article already exists - update it instead of skipping
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                # Update existing article with new data (preserve created_at)
                existing_created_at = existing.get("created_at")
                # Merge new data
                article_dict = article.model_dump()
                article_dict["created_at"] = existing_created_at or article_dict.get("created_at") or datetime.now().isoformat()
                article_dict["updated_at"] = datetime.now().isoformat()
                
                # Convert datetime objects to ISO format strings for JSON serialization
                for key, value in article_dict.items():
                    if isinstance(value, datetime):
                        article_dict[key] = value.isoformat()
                
                # Ensure thumbnail is preserved if new one is not provided
                if not article_dict.get("thumbnail") and existing.get("thumbnail"):
                    article_dict["thumbnail"] = existing.get("thumbnail")
                # Write updated article
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(article_dict, f, indent=2, ensure_ascii=False)
                return article_dict
            except Exception as e:
                print(f"Error reading existing article, overwriting: {e}")
                # If can't read, continue to save new one
                pass
        
        article_dict = article.model_dump()
        now = datetime.now().isoformat()
        article_dict["created_at"] = article_dict.get("created_at") or now
        article_dict["updated_at"] = now
        
        # Convert datetime objects to ISO format strings for JSON serialization
        for key, value in article_dict.items():
            if isinstance(value, datetime):
                article_dict[key] = value.isoformat()
        
        # Ensure thumbnail, video_url, and documentation_url are included if available
        if hasattr(article, 'thumbnail') and article.thumbnail:
            article_dict["thumbnail"] = article.thumbnail
        if hasattr(article, 'video_url') and article.video_url:
            article_dict["video_url"] = article.video_url
        if hasattr(article, 'documentation_url') and article.documentation_url:
            article_dict["documentation_url"] = article.documentation_url
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(article_dict, f, indent=2, ensure_ascii=False)
        
        return article_dict
    
    async def get_article_by_slug(self, slug: str) -> Optional[Dict]:
        """Get article by slug."""
        file_path = self.storage_path / f"{slug}.json"
        
        if not file_path.exists():
            return None
        
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    async def list_articles(
        self,
        page: int = 1,
        limit: int = 20
    ) -> Dict:
        """List all articles with pagination."""
        articles = []
        
        for file_path in self.storage_path.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    article = json.load(f)
                    articles.append(article)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
        
        # Sort by published_at (newest first)
        articles.sort(
            key=lambda x: x.get("published_at", ""),
            reverse=True
        )
        
        # Pagination
        total = len(articles)
        start = (page - 1) * limit
        end = start + limit
        paginated_articles = articles[start:end]
        
        return {
            "articles": paginated_articles,
            "count": len(paginated_articles),
            "page": page,
            "total_pages": (total + limit - 1) // limit
        }

