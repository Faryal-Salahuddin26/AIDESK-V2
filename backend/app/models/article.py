"""Article database model."""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class Article(Base):
    """Article model for database storage."""
    
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    url = Column(String, nullable=False)
    source = Column(String, nullable=False)
    
    # Summaries
    short_summary = Column(Text)
    long_summary = Column(Text)
    
    # SEO Metadata
    meta_title = Column(String)
    meta_description = Column(Text)
    tags = Column(JSON)  # Store as JSON array
    
    # Metadata
    published_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

