"""
Report schemas

Provides request/response schemas for discussion reports.
"""
from datetime import datetime

from pydantic import BaseModel, Field


class ReportResponse(BaseModel):
    """Full discussion report response."""

    id: str = Field(
        ...,
        description="Report ID"
    )
    discussion_id: str = Field(
        ...,
        description="Associated discussion ID"
    )
    overview: dict = Field(
        ...,
        description="Discussion overview and summary"
    )
    viewpoints_summary: list[dict] = Field(
        ...,
        description="Character viewpoint summaries"
    )
    consensus: dict = Field(
        ...,
        description="Agreed conclusions"
    )
    controversies: list[dict] = Field(
        ...,
        description="Points of disagreement"
    )
    insights: list[dict] = Field(
        ...,
        description="Key insights from discussion"
    )
    recommendations: list[dict] = Field(
        ...,
        description="Actionable recommendations"
    )
    quality_scores: dict = Field(
        ...,
        description="Quality metrics"
    )
    generation_time_ms: int = Field(
        ...,
        ge=0,
        description="Report generation time in milliseconds"
    )
    created_at: datetime = Field(
        ...,
        description="Report creation timestamp"
    )

    model_config = {
        "from_attributes": True
    }


class ReportSummaryResponse(BaseModel):
    """Report summary for list view."""

    id: str = Field(
        ...,
        description="Report ID"
    )
    discussion_id: str = Field(
        ...,
        description="Associated discussion ID"
    )
    discussion_title: str = Field(
        ...,
        description="Discussion title"
    )
    overview: dict = Field(
        ...,
        description="Brief overview"
    )
    quality_scores: dict = Field(
        ...,
        description="Quality metrics"
    )
    created_at: datetime = Field(
        ...,
        description="Report creation timestamp"
    )


class ShareLinkCreateRequest(BaseModel):
    """Share link creation request."""

    password: str | None = Field(
        None,
        min_length=8,
        max_length=100,
        description="Optional password protection"
    )
    expires_in_days: int | None = Field(
        None,
        ge=1,
        le=365,
        description="Expiration in days (NULL for no expiration)"
    )


class ShareLinkResponse(BaseModel):
    """Share link response."""

    id: str = Field(
        ...,
        description="Share link ID"
    )
    slug: str = Field(
        ...,
        description="URL slug for sharing"
    )
    discussion_title: str = Field(
        ...,
        description="Discussion title"
    )
    has_password: bool = Field(
        ...,
        description="Whether password protection is enabled"
    )
    expires_at: datetime | None = Field(
        None,
        description="Expiration timestamp"
    )
    access_count: int = Field(
        ...,
        ge=0,
        description="Number of times accessed"
    )
    created_at: datetime = Field(
        ...,
        description="Link creation timestamp"
    )
