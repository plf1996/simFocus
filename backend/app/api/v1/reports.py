"""
Reports API routes

Provides endpoints for accessing and sharing discussion reports.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.models.report import Report, ShareLink
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.report import ReportResponse, ShareLinkCreateRequest, ShareLinkResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timedelta
import secrets
import bcrypt

router = APIRouter(prefix="/reports", tags=["reports"])


# Minimal database session dependency (reusing existing pattern)
async def get_db():
    """Get database session."""
    from app.db.session import async_session_maker
    async with async_session_maker() as session:
        yield session


@router.get(
    "/discussions/{discussion_id}",
    response_model=ReportResponse,
    summary="Get report by discussion ID",
)
async def get_report_by_discussion(
    discussion_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get the report for a specific discussion.

    Returns the AI-generated report with insights, consensus,
    controversies, and recommendations.
    """
    # Get report
    result = await db.execute(
        select(Report).where(Report.discussion_id == UUID(discussion_id))
    )
    report = result.scalar_one_or_none()

    if not report:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(
            message="Report not found for this discussion",
            details={"discussion_id": discussion_id}
        )

    # Verify ownership through discussion
    from app.models.discussion import Discussion
    discussion_result = await db.execute(
        select(Discussion).where(Discussion.id == UUID(discussion_id))
    )
    discussion = discussion_result.scalar_one_or_none()

    if not discussion or str(discussion.user_id) != str(current_user.id):
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("You don't have permission to access this report")

    return report


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    summary="Get report by ID",
)
async def get_report(
    report_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get a specific report by ID.

    Returns the full report with all sections.
    """
    # Get report
    result = await db.execute(
        select(Report).where(Report.id == UUID(report_id))
    )
    report = result.scalar_one_or_none()

    if not report:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(message="Report not found")

    # Verify ownership through discussion
    from app.models.discussion import Discussion
    discussion_result = await db.execute(
        select(Discussion).where(Discussion.id == report.discussion_id)
    )
    discussion = discussion_result.scalar_one_or_none()

    if not discussion or str(discussion.user_id) != str(current_user.id):
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("You don't have permission to access this report")

    return report


class ShareLinkRequest(BaseModel):
    """Create share link request."""

    password: str | None = None
    expires_in_days: int | None = None


@router.post(
    "/discussions/{discussion_id}/share",
    response_model=ShareLinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create share link for discussion",
)
async def create_share_link(
    discussion_id: str,
    data: ShareLinkRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create a shareable link for a discussion.

    Optionally protected with password and expiration.
    """
    # Verify discussion ownership
    from app.models.discussion import Discussion
    discussion_result = await db.execute(
        select(Discussion).where(Discussion.id == UUID(discussion_id))
    )
    discussion = discussion_result.scalar_one_or_none()

    if not discussion or str(discussion.user_id) != str(current_user.id):
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("You don't have permission to share this discussion")

    # Generate unique slug
    slug = secrets.token_urlsafe(12)

    # Hash password if provided
    password_hash = None
    if data.password:
        password_hash = bcrypt.hashpw(
            data.password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    # Calculate expiration
    expires_at = None
    if data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=data.expires_in_days)

    # Create share link
    share_link = ShareLink(
        discussion_id=UUID(discussion_id),
        user_id=UUID(str(current_user.id)),
        slug=slug,
        password_hash=password_hash,
        expires_at=expires_at,
        access_count=0,
    )

    db.add(share_link)
    await db.commit()
    await db.refresh(share_link)

    # Build response
    return ShareLinkResponse(
        id=str(share_link.id),
        slug=share_link.slug,
        discussion_title=discussion.topic.title if discussion.topic else "Discussion",
        has_password=share_link.has_password,
        expires_at=share_link.expires_at,
        access_count=share_link.access_count,
        created_at=share_link.created_at,
    )


@router.get(
    "/share/{slug}",
    summary="Access shared discussion",
)
async def access_shared_discussion(
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    password: str | None = Query(None, description="Password if link is protected"),
):
    """
    Access a shared discussion via share link.

    Returns discussion, messages, and report if available.
    """
    # Get share link
    result = await db.execute(
        select(ShareLink).where(ShareLink.slug == slug)
    )
    share_link = result.scalar_one_or_none()

    if not share_link:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(message="Share link not found or has expired")

    # Check expiration
    if share_link.is_expired:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(message="Share link has expired")

    # Check password
    if share_link.has_password:
        if not password:
            from app.core.exceptions import UnauthorizedException
            raise UnauthorizedException(message="Password required")

        if not bcrypt.checkpw(
            password.encode('utf-8'),
            share_link.password_hash.encode('utf-8')
        ):
            from app.core.exceptions import UnauthorizedException
            raise UnauthorizedException(message="Invalid password")

    # Get discussion with data
    from app.models.discussion import Discussion, DiscussionParticipant
    from app.models.discussion import DiscussionMessage

    discussion_result = await db.execute(
        select(Discussion).where(Discussion.id == share_link.discussion_id)
    )
    discussion = discussion_result.scalar_one_or_none()

    if not discussion:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(message="Discussion not found")

    # Get participants
    participants_result = await db.execute(
        select(DiscussionParticipant).where(
            DiscussionParticipant.discussion_id == discussion.id
        )
    )
    participants = participants_result.scalars().all()

    # Get messages
    messages_result = await db.execute(
        select(DiscussionMessage).where(
            DiscussionMessage.discussion_id == discussion.id
        ).order_by(DiscussionMessage.created_at.asc())
    )
    messages = messages_result.scalars().all()

    # Get report
    report_result = await db.execute(
        select(Report).where(Report.discussion_id == discussion.id)
    )
    report = report_result.scalar_one_or_none()

    # Increment access count
    share_link.increment_access()
    await db.commit()

    # Build response
    return {
        "discussion": {
            "id": str(discussion.id),
            "discussion_mode": discussion.discussion_mode,
            "status": discussion.status,
            "current_round": discussion.current_round,
            "max_rounds": discussion.max_rounds,
            "created_at": discussion.created_at,
            "completed_at": discussion.completed_at,
        },
        "topic": {
            "id": str(discussion.topic.id),
            "title": discussion.topic.title,
            "description": discussion.topic.description,
        },
        "participants": [
            {
                "id": str(p.id),
                "character_name": p.character.name if p.character else "Unknown",
                "stance": p.stance,
                "position": p.position,
            }
            for p in participants
        ],
        "messages": [
            {
                "id": str(m.id),
                "round": m.round,
                "phase": m.phase,
                "content": m.content,
                "created_at": m.created_at,
            }
            for m in messages
        ],
        "report": ReportResponse.model_validate(report) if report else None,
    }


@router.delete(
    "/share/{slug}",
    response_model=MessageResponse,
    summary="Delete share link",
)
async def delete_share_link(
    slug: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Delete a share link.

    Only the link creator can delete it.
    """
    # Get share link
    result = await db.execute(
        select(ShareLink).where(ShareLink.slug == slug)
    )
    share_link = result.scalar_one_or_none()

    if not share_link:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(message="Share link not found")

    # Verify ownership
    if str(share_link.user_id) != str(current_user.id):
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("You don't have permission to delete this link")

    # Delete
    await db.execute(
        select(ShareLink).where(ShareLink.id == share_link.id)
    )
    await db.commit()

    return MessageResponse(message="Share link deleted successfully")
