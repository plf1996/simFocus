"""
Topic management API routes

Provides endpoints for creating and managing discussion topics.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user, get_topic_service
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.topic import (
    TopicCreateRequest,
    TopicListResponse,
    TopicResponse,
    TopicUpdateRequest,
)
from app.services.topic_service import TopicService

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get(
    "",
    response_model=PaginatedResponse[TopicListResponse],
    summary="List user topics",
)
async def list_topics(
    current_user: Annotated[User, Depends(get_current_user)],
    topic_service: Annotated[TopicService, Depends(get_topic_service)],
    pagination: Annotated[dict, Depends()] = Depends(lambda: {
        "page": 1,
        "size": 20,
    }),
    status_filter: Annotated[str | None, Query(alias="status", description="Filter by topic status")] = None,
    search: Annotated[str | None, Query(description="Search in title and description")] = None,
):
    """
    Get paginated list of user's topics.

    - **status**: Filter by status (draft, ready, in_discussion, completed)
    - **search**: Search in title and description fields
    - **page**: Page number (starts from 1)
    - **size**: Items per page (max 100)
    """
    page = pagination.get("page", 1)
    size = pagination.get("size", 20)

    topics, total = await topic_service.list_topics(
        user_id=str(current_user.id),
        status_filter=status_filter,
        search=search,
        page=page,
        size=size,
    )

    return PaginatedResponse(
        items=topics,
        total=total,
        page=page,
        size=size,
    )


@router.post(
    "",
    response_model=TopicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new topic",
)
async def create_topic(
    data: TopicCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    topic_service: Annotated[TopicService, Depends(get_topic_service)],
):
    """
    Create a new discussion topic.

    - **title**: Topic title (10-200 characters)
    - **description**: Optional detailed description
    - **context**: Optional background information
    - **attachments**: Optional file attachments (max 5)
    """
    topic = await topic_service.create_topic(
        user_id=str(current_user.id),
        title=data.title,
        description=data.description,
        context=data.context,
        attachments=data.attachments,
        template_id=data.template_id,
    )
    return topic


@router.get(
    "/{topic_id}",
    response_model=TopicResponse,
    summary="Get topic by ID",
)
async def get_topic(
    topic_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    topic_service: Annotated[TopicService, Depends(get_topic_service)],
):
    """
    Get topic details.

    Returns full topic information including attachments.
    """
    topic = await topic_service.get_topic(topic_id=topic_id)
    return topic


@router.patch(
    "/{topic_id}",
    response_model=TopicResponse,
    summary="Update topic",
)
async def update_topic(
    topic_id: str,
    data: TopicUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    topic_service: Annotated[TopicService, Depends(get_topic_service)],
):
    """
    Update topic details.

    Can only update topics with draft or ready status.
    Topics in discussion or completed cannot be modified.
    """
    topic = await topic_service.update_topic(
        topic_id=topic_id,
        user_id=str(current_user.id),
        title=data.title,
        description=data.description,
        context=data.context,
        attachments=data.attachments,
        status=data.status,
    )
    return topic


@router.delete(
    "/{topic_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Delete topic",
)
async def delete_topic(
    topic_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    topic_service: Annotated[TopicService, Depends(get_topic_service)],
):
    """
    Delete topic and associated discussions.

    This will cascade delete all discussions created from this topic.
    Cannot delete topics with active discussions.
    """
    await topic_service.delete_topic(
        topic_id=topic_id,
        user_id=str(current_user.id),
    )
    return MessageResponse(message="Topic deleted successfully")


@router.post(
    "/{topic_id}/duplicate",
    response_model=TopicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate topic",
)
async def duplicate_topic(
    topic_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    topic_service: Annotated[TopicService, Depends(get_topic_service)],
):
    """
    Create a copy of existing topic.

    Creates a new topic with same content but new ID and status reset to draft.
    """
    topic = await topic_service.duplicate_topic(
        topic_id=topic_id,
        user_id=str(current_user.id),
    )
    return topic
