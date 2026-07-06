"""
DealOS AI — Application Configuration.

Centralized configuration using Pydantic Settings.
All values are loaded from environment variables with sensible defaults.

Why Pydantic Settings?
- Type-safe: catches misconfigurations at startup, not at runtime
- Validation: invalid values fail fast with clear error messages
- Documentation: every setting is self-documenting via field descriptions
- Environment binding: automatic .env file loading
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──
    app_name: str = Field(default="DealOS AI", description="Application display name")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development", description="Deployment environment"
    )
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging verbosity"
    )

    # ── Backend Server ──
    backend_host: str = Field(default="0.0.0.0", description="Server bind host")
    backend_port: int = Field(default=8000, description="Server bind port")
    backend_workers: int = Field(default=4, description="Uvicorn worker count")
    cors_origins: list[str] = Field(
        default=["http://localhost:5173"], description="Allowed CORS origins"
    )

    # ── PostgreSQL ──
    postgres_host: str = Field(default="localhost", description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_user: str = Field(default="dealos", description="PostgreSQL user")
    postgres_password: str = Field(default="dealos_dev_password", description="PostgreSQL password")
    postgres_db: str = Field(default="dealos", description="PostgreSQL database name")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        """Construct async database URL from components."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url_sync(self) -> str:
        """Construct sync database URL for Alembic migrations."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # ── Redis ──
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def redis_url(self) -> str:
        """Construct Redis connection URL."""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # ── MinIO ──
    minio_endpoint: str = Field(default="localhost:9000", description="MinIO endpoint")
    minio_access_key: str = Field(default="dealos_minio", description="MinIO access key")
    minio_secret_key: str = Field(default="dealos_minio_secret", description="MinIO secret key")
    minio_bucket: str = Field(default="dealos-documents", description="MinIO bucket name")
    minio_use_ssl: bool = Field(default=False, description="Use SSL for MinIO connection")

    # ── JWT ──
    jwt_secret_key: str = Field(
        default="your-super-secret-jwt-key-change-in-production",
        description="JWT signing secret",
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    jwt_access_token_expire_minutes: int = Field(
        default=15, description="Access token lifetime in minutes"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7, description="Refresh token lifetime in days"
    )

    # ── OpenAI ──
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model for agents")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small", description="Embedding model"
    )
    openai_embedding_dimensions: int = Field(
        default=1536, description="Embedding vector dimensions"
    )

    # ── Rate Limiting ──
    rate_limit_per_minute: int = Field(default=60, description="General rate limit per minute")
    auth_rate_limit_per_minute: int = Field(
        default=10, description="Auth endpoint rate limit per minute"
    )

    # ── File Upload ──
    max_file_size_mb: int = Field(default=50, description="Max file size in MB")
    allowed_extensions: list[str] = Field(
        default=["pdf", "docx", "xlsx", "csv", "pptx", "txt"],
        description="Allowed file extensions",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB to bytes for file validation."""
        return self.max_file_size_mb * 1024 * 1024


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return cached application settings.

    Uses lru_cache to ensure settings are loaded once and reused,
    avoiding repeated .env file parsing.
    """
    return Settings()
