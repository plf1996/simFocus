from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from typing import Any

if False:
    from app.models.user import User

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.topic import (
    TopicCreate,
    TopicUpdate,
    TopicResponse,
    TopicListItem
)
from app.services.topic_service import TopicService


router = APIRouter(prefix="/api/topics", tags=["Topics"])


@router.get("", response_model=List[TopicListItem])
async def get_topics(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all topics for current user with optional status filter"""
    service = TopicService(db)
    topics = await service.get_user_topics(current_user.id, status, skip, limit)
    return [TopicListItem.model_validate(topic) for topic in topics]


@router.post("", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic_data: TopicCreate,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new topic"""
    service = TopicService(db)
    topic = await service.create_topic(current_user.id, topic_data)
    return TopicResponse.model_validate(topic)


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(
    topic_id: UUID,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific topic"""
    service = TopicService(db)
    topic = await service.get_topic_by_id(topic_id, current_user.id)

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )

    return TopicResponse.model_validate(topic)


@router.patch("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: UUID,
    topic_data: TopicUpdate,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a topic"""
    service = TopicService(db)
    try:
        topic = await service.update_topic(topic_id, current_user.id, topic_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )

    return TopicResponse.model_validate(topic)


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: UUID,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a topic"""
    service = TopicService(db)
    try:
        success = await service.delete_topic(topic_id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )


@router.get("/search", response_model=List[TopicListItem])
async def search_topics(
    query: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search topics by title or description"""
    service = TopicService(db)
    topics = await service.search_topics(current_user.id, query, skip, limit)
    return [TopicListItem.model_validate(topic) for topic in topics]
