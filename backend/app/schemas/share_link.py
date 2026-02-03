from pydantic import BaseModel, Field, ConfigDict, HttpUrl
from typing import Optional
from datetime import datetime
from uuid import UUID


class ShareLinkCreate(BaseModel):
    discussion_id: UUID
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="Optional password protection")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="Optional expiry in days")


class ShareLinkResponse(BaseModel):
    id: UUID
    discussion_id: UUID
    slug: str
    share_url: str  # Generated full URL
    has_password: bool
    expires_at: Optional[datetime] = None
    access_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ShareLinkAccess(BaseModel):
    discussion_id: UUID
    slug: str
    password: Optional[str] = None  # Required if link is password-protected
