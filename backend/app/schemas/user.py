"""
User schemas

Provides request/response schemas for user management operations.
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    """User profile response."""

    id: str = Field(
        ...,
        description="User ID"
    )
    email: EmailStr = Field(
        ...,
        description="User email address"
    )
    name: str | None = Field(
        None,
        description="Display name"
    )
    avatar_url: str | None = Field(
        None,
        description="Profile picture URL"
    )
    bio: str | None = Field(
        None,
        description="User biography"
    )
    email_verified: bool = Field(
        ...,
        description="Email verification status"
    )
    auth_provider: str = Field(
        ...,
        description="Authentication provider (email, google, github)"
    )
    created_at: datetime = Field(
        ...,
        description="Account creation timestamp"
    )
    last_login_at: datetime | None = Field(
        None,
        description="Last login timestamp"
    )

    model_config = {
        "from_attributes": True
    }


class UserUpdateRequest(BaseModel):
    """User profile update request."""

    name: str | None = Field(
        None,
        max_length=100,
        description="Display name"
    )
    avatar_url: str | None = Field(
        None,
        description="Profile picture URL"
    )
    bio: str | None = Field(
        None,
        max_length=500,
        description="User biography"
    )


class UserStatsResponse(BaseModel):
    """User usage statistics."""

    total_discussions: int = Field(
        ...,
        ge=0,
        description="Total number of discussions created"
    )
    total_topics: int = Field(
        ...,
        ge=0,
        description="Total number of topics created"
    )
    total_characters: int = Field(
        ...,
        ge=0,
        description="Total number of custom characters created"
    )
    total_tokens_used: int = Field(
        ...,
        ge=0,
        description="Total LLM tokens consumed"
    )
    estimated_cost_usd: float = Field(
        ...,
        ge=0,
        description="Estimated total API cost in USD"
    )


class APIKeyCreateRequest(BaseModel):
    """API key creation request."""

    provider: str = Field(
        ...,
        pattern='^(openai|anthropic|custom)$',
        description="API provider name"
    )
    key_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User-defined key name"
    )
    api_key: str = Field(
        ...,
        min_length=10,
        description="API key string (will be encrypted)"
    )
    api_base_url: str | None = Field(
        None,
        description="Custom API endpoint URL (for custom providers)"
    )
    default_model: str | None = Field(
        None,
        max_length=100,
        description="Default model to use with this key"
    )


class APIKeyUpdateRequest(BaseModel):
    """API key update request."""

    key_name: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="New key name"
    )
    api_base_url: str | None = Field(
        None,
        description="New custom API endpoint URL"
    )
    default_model: str | None = Field(
        None,
        max_length=100,
        description="New default model"
    )
    is_active: bool | None = Field(
        None,
        description="Active status"
    )


class APIKeyResponse(BaseModel):
    """API key response (without actual key value)."""

    id: str = Field(
        ...,
        description="API key ID"
    )
    provider: str = Field(
        ...,
        description="API provider name"
    )
    key_name: str = Field(
        ...,
        description="User-defined key name"
    )
    api_base_url: str | None = Field(
        None,
        description="Custom API endpoint URL"
    )
    default_model: str | None = Field(
        None,
        description="Default model"
    )
    is_active: bool = Field(
        ...,
        description="Active status"
    )
    last_used_at: datetime | None = Field(
        None,
        description="Last usage timestamp"
    )
    created_at: datetime = Field(
        ...,
        description="Creation timestamp"
    )

    model_config = {
        "from_attributes": True
    }
