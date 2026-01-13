"""
Common Pydantic schemas

Provides reusable schemas for pagination, error responses, and common patterns.
"""
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    page: int = Field(
        default=1,
        ge=1,
        description="Page number (starts from 1)"
    )
    size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page (max 100)"
    )

    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T] = Field(
        default_factory=list,
        description="List of items for current page"
    )
    total: int = Field(
        ge=0,
        description="Total number of items across all pages"
    )
    page: int = Field(
        ge=1,
        description="Current page number"
    )
    size: int = Field(
        ge=1,
        description="Number of items per page"
    )
    pages: int = Field(
        ge=0,
        description="Total number of pages"
    )

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        size: int
    ) -> "PaginatedResponse[T]":
        """
        Create paginated response from items and metadata.

        Args:
            items: List of items for current page
            total: Total number of items
            page: Current page number
            size: Items per page

        Returns:
            PaginatedResponse instance
        """
        pages = (total + size - 1) // size if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: dict[str, Any] = Field(
        ...,
        description="Error details containing code, message, and optional metadata"
    )

    @classmethod
    def create(
        cls,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> "ErrorResponse":
        """
        Create error response from error details.

        Args:
            code: Error code for programmatic handling
            message: Human-readable error message
            details: Additional error context
            request_id: Request ID for tracing

        Returns:
            ErrorResponse instance
        """
        error_data: dict[str, Any] = {
            "code": code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if details:
            error_data["details"] = details
        if request_id:
            error_data["request_id"] = request_id
        return cls(error=error_data)


class MessageResponse(BaseModel):
    """Simple message response for successful operations."""

    message: str = Field(
        ...,
        description="Success message"
    )


class IdResponse(BaseModel):
    """Response containing ID of created resource."""

    id: str = Field(
        ...,
        description="ID of created resource"
    )
