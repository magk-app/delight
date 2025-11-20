"""
Application configuration and settings.
Loads environment variables using Pydantic Settings.
"""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    DATABASE_URL: str = ""  # Allow empty for better error messages

    # Authentication Configuration (Clerk)
    CLERK_SECRET_KEY: str  # Required: Session token verification
    CLERK_WEBHOOK_SECRET: str  # Required: Webhook signature validation

    # Application Configuration
    ENVIRONMENT: str = "development"
    INFRA_MODE: Optional[str] = "cloud-dev"

    # Infrastructure Configuration
    REDIS_URL: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    SENTRY_DSN: Optional[str] = None
    CORS_ORIGINS: Optional[str] = "http://localhost:3000,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",  # Allow extra fields from environment for flexibility
    )

    @property
    def async_database_url(self) -> str:
        """
        Convert DATABASE_URL to use asyncpg driver for async operations.
        Replaces postgresql:// with postgresql+asyncpg://
        Adds statement_cache_size=0 for pgbouncer Transaction Mode.
        """
        if not self.DATABASE_URL:
            raise ValueError(
                "DATABASE_URL is not set. Please set it in your .env file.\n"
                "Example: DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/delight"
            )
        
        # Convert to asyncpg driver
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        
        # Note: statement_cache_size must be set in connect_args, not URL
        # See app/db/session.py for the actual configuration
        
        return url
    
    @property
    def requires_ssl(self) -> bool:
        """Check if database connection requires SSL (Supabase/cloud databases)"""
        url = self.DATABASE_URL.lower()
        return "pooler.supabase.com" in url or "supabase.co" in url or "railway.app" in url


# Singleton settings instance
settings = Settings()
