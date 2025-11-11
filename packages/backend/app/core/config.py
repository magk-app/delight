"""
Application configuration and settings.
Loads environment variables using Pydantic Settings.
"""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    DATABASE_URL: str

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
        """
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
        return self.DATABASE_URL


# Singleton settings instance
settings = Settings()
