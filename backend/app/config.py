"""Configuration settings for the application."""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AIDesk API"
    VERSION: str = "1.0.0"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    
    # Optional API Keys for Enhanced Data Collection
    YOUTUBE_API_KEY: Optional[str] = None
    BING_SEARCH_API_KEY: Optional[str] = None
    GOOGLE_SEARCH_API_KEY: Optional[str] = None
    GOOGLE_SEARCH_ENGINE_ID: Optional[str] = None
    SERPAPI_KEY: Optional[str] = None
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./aidesk.db"
    
    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-use-env-var")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Storage Configuration
    # Default to storage/news-data relative to project root
    STORAGE_PATH: str = "storage/news-data"
    
    # Scheduler Configuration
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_INTERVAL: int = 600  # 10 minutes in seconds (default) - runs master pipeline
    
    # CORS Configuration
    # Can be set via environment variable as comma-separated string
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,https://*.vercel.app,https://*.netlify.app,https://*.railway.app"
    
    def get_cors_origins(self) -> list[str]:
        """Parse CORS origins from environment variable."""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS if isinstance(self.CORS_ORIGINS, list) else []
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
