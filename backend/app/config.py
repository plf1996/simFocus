"""
Application configuration using Pydantic Settings

Loads and validates all environment variables for the application.
Supports multiple environments (development, testing, production).
"""
from functools import lru_cache
from typing import Any, Dict, Literal, Optional

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        app: Application-specific settings
        database: Database connection settings
        security: Security and encryption settings
        jwt: JWT token configuration
        cors: CORS configuration
        api: External API provider settings
        redis: Redis configuration
        logging: Logging configuration
    """

    # Application Settings
    APP_NAME: str = "simFocus"
    APP_VERSION: str = "0.1.0"
    APP_ENV: Literal["development", "testing", "production"] = Field(
        default="development",
        description="Application environment"
    )
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_ROOT: str = Field(
        default="/root/projects/simFocus",
        description="Project root directory path"
    )

    # Server Settings
    HOST: str = Field(
        default="0.0.0.0",
        description="Server host"
    )
    PORT: int = Field(
        default=8000,
        description="Server port"
    )
    WORKERS: int = Field(
        default=1,
        description="Number of worker processes"
    )

    # Database Settings
    DATABASE_HOST: str = Field(
        default="localhost",
        description="Database host"
    )
    DATABASE_PORT: int = Field(
        default=5432,
        description="Database port"
    )
    DATABASE_USER: str = Field(
        default="simfocus",
        description="Database username"
    )
    DATABASE_PASSWORD: SecretStr = Field(
        default="simfocus_password",
        description="Database password"
    )
    DATABASE_NAME: str = Field(
        default="simfocus",
        description="Database name"
    )
    DATABASE_POOL_SIZE: int = Field(
        default=20,
        description="Database connection pool size"
    )
    DATABASE_MAX_OVERFLOW: int = Field(
        default=10,
        description="Database connection pool max overflow"
    )
    DATABASE_POOL_TIMEOUT: int = Field(
        default=30,
        description="Database connection pool timeout in seconds"
    )
    DATABASE_POOL_RECYCLE: int = Field(
        default=3600,
        description="Database connection pool recycle time in seconds"
    )
    DATABASE_ECHO: bool = Field(
        default=False,
        description="Echo SQL queries for debugging"
    )

    # Security Settings
    SECRET_KEY: SecretStr = Field(
        default="your-secret-key-change-in-production",
        description="Application secret key for signing"
    )
    ENCRYPTION_KEY: Optional[SecretStr] = Field(
        default=None,
        description="AES-256 encryption key for sensitive data (32 bytes base64 encoded)"
    )

    # JWT Settings
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="JWT access token expiration time in minutes"
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="JWT refresh token expiration time in days"
    )

    # CORS Settings
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Allow credentials in CORS"
    )
    CORS_ALLOW_METHODS: list[str] = Field(
        default=["*"],
        description="Allowed CORS methods"
    )
    CORS_ALLOW_HEADERS: list[str] = Field(
        default=["*"],
        description="Allowed CORS headers"
    )

    # API Provider Settings
    OPENAI_API_KEY: Optional[SecretStr] = Field(
        default=None,
        description="OpenAI API key (optional server-side default)"
    )
    ANTHROPIC_API_KEY: Optional[SecretStr] = Field(
        default=None,
        description="Anthropic API key (optional server-side default)"
    )
    API_TIMEOUT: int = Field(
        default=120,
        description="External API timeout in seconds"
    )
    API_MAX_RETRIES: int = Field(
        default=3,
        description="Maximum number of API call retries"
    )
    API_RETRY_DELAY: float = Field(
        default=1.0,
        description="Initial retry delay in seconds (exponential backoff)"
    )

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        description="Requests per minute limit"
    )
    RATE_LIMIT_BURST: int = Field(
        default=100,
        description="Burst capacity for rate limiting"
    )

    # Discussion Settings
    DEFAULT_DISCUSSION_ROUNDS: int = Field(
        default=10,
        description="Default number of discussion rounds"
    )
    MAX_DISCUSSION_ROUNDS: int = Field(
        default=20,
        description="Maximum number of discussion rounds"
    )
    MIN_DISCUSSION_ROUNDS: int = Field(
        default=3,
        description="Minimum number of discussion rounds"
    )
    DISCUSSION_TIMEOUT_SECONDS: int = Field(
        default=300,
        description="Timeout for each discussion round in seconds"
    )

    # File Upload Settings
    MAX_UPLOAD_SIZE_MB: int = Field(
        default=10,
        description="Maximum file upload size in MB"
    )
    ALLOWED_UPLOAD_EXTENSIONS: list[str] = Field(
        default=["pdf", "txt", "md", "json"],
        description="Allowed file extensions for upload"
    )
    UPLOAD_DIR: str = Field(
        default="/tmp/simfocus/uploads",
        description="Directory for file uploads"
    )

    # Logging Settings
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    LOG_FORMAT: str = Field(
        default="json",
        description="Log format (json or text)"
    )
    LOG_FILE: Optional[str] = Field(
        default=None,
        description="Log file path (None for stdout)"
    )

    # Pagination Settings
    DEFAULT_PAGE_SIZE: int = Field(
        default=20,
        description="Default page size for pagination"
    )
    MAX_PAGE_SIZE: int = Field(
        default=100,
        description="Maximum page size for pagination"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("ENCRYPTION_KEY")
    @classmethod
    def validate_encryption_key(cls, v: Optional[SecretStr]) -> Optional[SecretStr]:
        """Validate encryption key format."""
        if v is not None:
            import base64
            try:
                key_str = v.get_secret_value()
                decoded = base64.b64decode(key_str)
                if len(decoded) != 32:  # AES-256 requires 32 bytes
                    raise ValueError(
                        "Encryption key must be 32 bytes (base64 encoded)"
                    )
            except Exception as e:
                raise ValueError(
                    f"Invalid encryption key format: {e}"
                )
        return v

    @property
    def database_url(self) -> str:
        """Generate SQLAlchemy async database URL."""
        password = self.DATABASE_PASSWORD.get_secret_value()
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{password}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @property
    def database_url_sync(self) -> str:
        """Generate SQLAlchemy sync database URL for Alembic."""
        password = self.DATABASE_PASSWORD.get_secret_value()
        return (
            f"postgresql+psycopg2://{self.DATABASE_USER}:{password}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.APP_ENV == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.APP_ENV == "testing"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.APP_ENV == "production"

    def get_provider_api_key(self, provider: str) -> Optional[str]:
        """
        Get API key for a specific provider.

        Args:
            provider: Provider name (openai, anthropic, etc.)

        Returns:
            API key or None if not configured
        """
        key_mapping = {
            "openai": self.OPENAI_API_KEY,
            "anthropic": self.ANTHROPIC_API_KEY,
        }
        key = key_mapping.get(provider.lower())
        return key.get_secret_value() if key else None


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    This function is cached to avoid reloading settings on every call.
    Use this function to access application settings throughout the app.

    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Convenience export
settings = get_settings()
