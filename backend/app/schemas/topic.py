"""
Topic schemas

Provides request/response schemas for topic management operations.
"""
from datetime import datetime

from pydantic import BaseModel, Field


class TopicCreateRequest(BaseModel):
    """Topic creation request."""

    title: str = Field(
        ...,
        min_length=10,
        max_length=200,
        description="Topic title"
    )
    description: str | None = Field(
        None,
        max_length=2000,
        description="Detailed description of the topic"
    )
    context: str | None = Field(
        None,
        max_length=5000,
        description="Background information for discussion"
    )
    attachments: list[dict] | None = Field(
        None,
        max_length=5,
        description="File attachments (max 5 files)"
    )


class TopicUpdateRequest(BaseModel):
    """Topic update request."""

    title: str | None = Field(
        None,
        min_length=10,
        max_length=200,
        description="Updated topic title"
    )
    description: str | None = Field(
        None,
        max_length=2000,
        description="Updated description"
    )
    context: str | None = Field(
        None,
        max_length=5000,
        description="Updated background information"
    )
    status: str | None = Field(
        None,
        pattern='^(draft|ready|in_discussion|completed)$',
        description="Updated topic status"
    )


class TopicResponse(BaseModel):
    """Full topic response."""

    id: str = Field(
        ...,
        description="Topic ID"
    )
    user_id: str = Field(
        ...,
        description="Owner user ID"
    )
    title: str = Field(
        ...,
        description="Topic title"
    )
    description: str | None = Field(
        None,
        description="Topic description"
    )
    context: str | None = Field(
        None,
        description="Background information"
    )
    attachments: dict | None = Field(
        None,
        description="File attachments"
    )
    status: str = Field(
        ...,
        description="Topic status"
    )
    created_at: datetime = Field(
        ...,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        ...,
        description="Last update timestamp"
    )

    model_config = {
        "from_attributes": True
    }


class TopicListResponse(BaseModel):
    """Topic list item (summary view)."""

    id: str = Field(
        ...,
        description="Topic ID"
    )
    title: str = Field(
        ...,
        description="Topic title"
    )
    status: str = Field(
        ...,
        description="Topic status"
    )
    created_at: datetime = Field(
        ...,
        description="Creation timestamp"
    )
    discussion_count: int = Field(
        ...,
        ge=0,
        description="Number of discussions created from this topic"
    )

    model_config = {
        "from_attributes": True
    }
