from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Encryption
    ENCRYPTION_KEY: str

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Environment
    ENVIRONMENT: str = "development"

    # LLM Providers
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Embedding API (strictly use these parameter names)
    EMBEDDING_API_KEY: str = ""
    EMBEDDING_BASE_URL: str = ""
    EMBEDDING_MODEL: str = "text-embedding-v3"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Keycloak SSO
    KEYCLOAK_ENABLED: bool = False
    KEYCLOAK_SERVER_URL: str = ""
    KEYCLOAK_REALM: str = ""
    KEYCLOAK_FRONTEND_CLIENT_ID: str = ""
    KEYCLOAK_BACKEND_CLIENT_ID: str = ""
    KEYCLOAK_BACKEND_CLIENT_SECRET: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
