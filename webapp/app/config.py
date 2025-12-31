"""Application configuration."""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "JobMatch"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-this-in-production"

    # Database
    database_url: str = "sqlite:///./data/jobmatch.db"

    # Service URLs
    gateway_url: str = "http://localhost:8001"
    dashboard_url: str = "http://localhost:8002"

    # Gateway settings
    gateway_timeout: float = 5.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
