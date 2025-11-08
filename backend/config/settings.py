"""
Configuration settings for the Mulan Marketing Agent system.
Loads environment variables and provides centralized configuration.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_key: str = Field(..., env="SUPABASE_KEY")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Reddit API
    reddit_client_id: str = Field(..., env="REDDIT_CLIENT_ID")
    reddit_client_secret: str = Field(..., env="REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = Field(..., env="REDDIT_USER_AGENT")
    reddit_username: Optional[str] = Field(default=None, env="REDDIT_USERNAME")
    reddit_password: Optional[str] = Field(default=None, env="REDDIT_PASSWORD")
    
    # Quora (Selenium-based scraping)
    quora_email: Optional[str] = Field(default=None, env="QUORA_EMAIL")
    quora_password: Optional[str] = Field(default=None, env="QUORA_PASSWORD")
    
    # Mulan Agent
    mulan_agent_url: str = Field(..., env="MULAN_AGENT_URL")
    mulan_agent_api_key: str = Field(..., env="MULAN_AGENT_API_KEY")
    
    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    
    # Rate Limiting
    crawl_interval_hours: int = Field(default=6, env="CRAWL_INTERVAL_HOURS")
    max_requests_per_minute: int = Field(default=30, env="MAX_REQUESTS_PER_MINUTE")
    
    # Crawler Settings
    reddit_subreddits: str = Field(
        default="artificialintelligence,machinelearning,deeplearning,videoproduction,videoediting",
        env="REDDIT_SUBREDDITS"
    )
    quora_topics: str = Field(
        default="Artificial Intelligence,Video Editing,Machine Learning",
        env="QUORA_TOPICS"
    )
    max_posts_per_crawl: int = Field(default=100, env="MAX_POSTS_PER_CRAWL")
    
    # Response Settings
    auto_post_enabled: bool = Field(default=False, env="AUTO_POST_ENABLED")
    min_confidence_score: float = Field(default=0.7, env="MIN_CONFIDENCE_SCORE")
    
    # Application
    environment: str = Field(default="development", env="ENVIRONMENT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

