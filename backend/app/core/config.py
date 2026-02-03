from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://simfocus:simfocus_dev_password@localhost:5432/simfocus"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-min-32-chars-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Encryption
    ENCRYPTION_KEY: str = os.getenv(
        "ENCRYPTION_KEY",
        "your-32-byte-encryption-key-change-this-in-prod"
    ).ljust(32, '0')[:32]  # Ensure exactly 32 bytes

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Environment
    ENVIRONMENT: str = "development"

    # LLM Providers
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Embedding API (strictly use these parameter names)
    Embedding_API_KEY: str = ""
    Embedding_BASR_URL: str = ""
    Embedding_MODEl: str = "text-embedding-v3"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Keycloak SSO
    KEYCLOAK_ENABLED: bool = os.getenv("KEYCLOAK_ENABLED", "true").lower() == "true"
    KEYCLOAK_SERVER_URL: str = os.getenv("KEYCLOAK_SERVER_URL", "https://keycloak.plfai.cn/")
    KEYCLOAK_REALM: str = os.getenv("KEYCLOAK_REALM", "simfocus")
    KEYCLOAK_FRONTEND_CLIENT_ID: str = os.getenv("KEYCLOAK_FRONTEND_CLIENT_ID", "simfocus-frontend")
    KEYCLOAK_BACKEND_CLIENT_ID: str = os.getenv("KEYCLOAK_BACKEND_CLIENT_ID", "simfocus-backend")
    KEYCLOAK_BACKEND_CLIENT_SECRET: str = os.getenv("KEYCLOAK_BACKEND_CLIENT_SECRET", "")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
