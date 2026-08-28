"""
Central configuration for RankPilot AI.

All application settings are loaded from environment variables or the .env file.
Other modules should import `settings` from this file instead of hardcoding values.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =====================================================
    # Application
    # =====================================================
    APP_NAME: str = "RankPilot AI"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # =====================================================
    # API
    # =====================================================
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # =====================================================
    # AI Configuration
    # =====================================================
    LLM_PROVIDER: str = "gemini"

    GEMINI_API_KEY: str = Field(default="")
    GEMINI_MODEL: str = "gemini-3.5-flash"
    GEMINI_FALLBACK_MODEL: str = "gemini-3.5-flash-lite"

    # =====================================================
    # Database
    # =====================================================
    
    DATABASE_URL: str = "sqlite:///./rankpilot.db"

    # =====================================================
    # Website Crawler
    # =====================================================
    MAX_CRAWL_PAGES: int = 100
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_TIMEOUT: int = 20
    USER_AGENT: str = "RankPilotAI/2.0"

    # =====================================================
    # Reports
    # =====================================================
    REPORT_DIRECTORY: str = "reports"

    # =====================================================
    # Security
    # =====================================================
    SECRET_KEY: str = Field(default="")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    """
    return Settings()


settings = get_settings()