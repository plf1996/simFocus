from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class APIKeyBase(BaseModel):
    provider: str = Field(..., description="LLM provider: 'openai', 'anthropic', 'custom'")
    key_name: str = Field(..., min_length=1, max_length=100)
    api_base_url: Optional[str] = None
    default_model: Optional[str] = None


class APIKeyCreate(APIKeyBase):
    api_key: str = Field(..., min_length=10, description="Raw API key (will be encrypted before storage)")


class APIKeyUpdate(BaseModel):
    key_name: Optional[str] = None
    api_base_url: Optional[str] = None
    default_model: Optional[str] = None
    is_active: Optional[bool] = None


class APIKeyResponse(APIKeyBase):
    id: UUID
    user_id: UUID
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class APIKeyWithDecrypted(APIKeyResponse):
    """For internal use only - contains decrypted key"""
    api_key: str  # Decrypted API key


class APIKeyUsageStats(BaseModel):
    total_calls: int
    total_tokens: int
    estimated_cost: float
