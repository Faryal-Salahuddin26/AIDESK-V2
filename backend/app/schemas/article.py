"""Article Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ArticleBase(BaseModel):
    """Base article schema."""
    title: str
    url: str
    source: str
    published_at: Optional[datetime] = None


class ArticleCreate(ArticleBase):
    """Schema for creating an article."""
    short_summary: Optional[str] = None
    long_summary: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    slug: Optional[str] = None
    tags: Optional[List[str]] = []
    thumbnail: Optional[str] = None
    description: Optional[str] = None
    video_url: Optional[str] = None  # YouTube video URL
    documentation_url: Optional[str] = None  # Official documentation URL


class ArticleUpdate(BaseModel):
    """Schema for updating an article."""
    title: Optional[str] = None
    short_summary: Optional[str] = None
    long_summary: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    tags: Optional[List[str]] = None


class ArticleResponse(ArticleBase):
    """Schema for article response."""
    id: Optional[int] = None
    slug: Optional[str] = None
    short_summary: Optional[str] = None
    long_summary: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    tags: List[str] = []
    thumbnail: Optional[str] = None
    video_url: Optional[str] = None
    documentation_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """Schema for article list response."""
    articles: List[ArticleResponse]
    count: int
    page: Optional[int] = 1
    total_pages: Optional[int] = 1

