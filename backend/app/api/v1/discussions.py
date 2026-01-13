"""
Discussion management API routes

Provides endpoints for creating and managing AI character discussions.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user, get_discussion_service
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.discussion import (
    DiscussionControlRequest,
    DiscussionCreateRequest,
    DiscussionDetailResponse,
    DiscussionListResponse,
    DiscussionResponse,
    InjectQuestionRequest,
    MessageResponse as DiscussionMessageResponse,
)
from app.services.discussion_service import DiscussionService

router = APIRouter(prefix="/discussions", tags=["discussions"])


@router.get(
    "",
    response_model=list[DiscussionListResponse],
    summary="List user discussions",
)
async def list_discussions(
    current_user: Annotated[User, Depends(get_current_user)],
    discussion_service: Annotated[DiscussionService, Depends(get_discussion_service)],
    status_filter: Annotated[
        str | None,
        Query(alias="status", description="Filter by discussion status")
    ] = None,
):
    """
    Get all discussions for current user.

    - **status**: Optional filter by status
    Returns summary view with topic title, status, and participant count.
    """
    discussions = await discussion_service.list_discussions(
        user_id=str(current_user.id),
        status_filter=status_filter,
        limit=50,
    )
    return discussions


@router.post(
    "",
    response_model=DiscussionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new discussion",
)
async def create_discussion(
    data: DiscussionCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    discussion_service: Annotated[DiscussionService, Depends(get_discussion_service)],
):
    """
    Create a new discussion.

    - **topic_id**: Topic to discuss
    - **character_ids**: 3-7 character IDs to participate
    - **discussion_mode**: Mode of discussion (free, structured, creative, consensus)
    - **max_rounds**: Maximum rounds (5-20, default 10)

    Validates topic ownership and character availability.
    """
    discussion = await discussion_service.create_discussion(
        user_id=str(current_user.id),
        topic_id=data.topic_id,
        character_ids=data.character_ids,
        discussion_mode=data.discussion_mode,
        max_rounds=data.max_rounds,
        llm_provider=data.llm_provider,
        llm_model=data.llm_model,
    )
    return discussion


@router.get(
    "/{discussion_id}",
    response_model=DiscussionDetailResponse,
    summary="Get discussion details",
)
async def get_discussion(
    discussion_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    discussion_service: Annotated[DiscussionService, Depends(get_discussion_service)],
):
    """
    Get full discussion details with messages.

    Returns topic info, participants, and all messages.
    """
    discussion = await discussion_service.get_discussion(discussion_id=discussion_id)
    return discussion


@router.delete(
    "/{discussion_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Delete discussion",
)
async def delete_discussion(
    discussion_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    discussion_service: Annotated[DiscussionService, Depends(get_discussion_service)],
):
    """
    Delete discussion.

    Can only delete discussions that are not currently running.
    """
    # DiscussionService doesn't have a delete method yet, so we'll add a placeholder
    # TODO: Implement delete in DiscussionService
    return MessageResponse(message="Discussion deletion not yet implemented")


@router.post(
    "/{discussion_id}/start",
    response_model=DiscussionResponse,
    summary="Start discussion",
)
async def start_discussion(
    discussion_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    discussion_service: Annotated[DiscussionService, Depends(get_discussion_service)],
):
    """
    Start the discussion engine.

    Validates API keys and begins character discussion.
    Changes status from 'initialized' to 'running'.
    """
    discussion = await discussion_service.start_discussion(
        discussion_id=discussion_id,
        user_id=str(current_user.id),
    )
    return discussion


@router.post(
    "/{discussion_id}/pause",
    response_model=DiscussionResponse,
    summary="Pause discussion",
)
async def pause_discussion(
    discussion_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    discussion_service: Annotated[DiscussionService, Depends(get_discussion_service)],
):
    """
    Pause running discussion.

    Temporarily pauses message generation.
    Can be resumed with /resume endpoint.
    """
    discussion = await discussion_service.pause_discussion(
        discussion_id=discussion_id,
        user_id=str(current_user.id),
    )
    return discussion


@router.post(
    "/{discussion_id}/resume",
    response_model=DiscussionResponse,
    summary="Resume discussion",
)
async def resume_discussion(
    discussion_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    discussion_service: Annotated[DiscussionService, Depends(get_discussion_service)],
):
    """
    Resume paused discussion.

    Continues message generation from where it left off.
    """
    discussion = await discussion_service.resume_discussion(
        discussion_id=discussion_id,
        user_id=str(current_user.id),
    )
    return discussion


@router.post(
    "/{discussion_id}/stop",
    response_model=DiscussionResponse,
    summary="Stop discussion",
)
async def stop_discussion(
    discussion_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    discussion_service: Annotated[DiscussionService, Depends(get_discussion_service)],
):
    """
    Stop discussion and trigger report generation.

    Immediately stops discussion and generates final report.
    Changes status to 'completed'.
    """
    discussion = await discussion_service.stop_discussion(
        discussion_id=discussion_id,
        user_id=str(current_user.id),
    )
    return discussion


@router.post(
    "/{discussion_id}/inject-question",
    response_model=MessageResponse,
    summary="Inject question into discussion",
)
async def inject_question(
    discussion_id: str,
    data: InjectQuestionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    discussion_service: Annotated[DiscussionService, Depends(get_discussion_service)],
):
    """
    Inject a guiding question into active discussion.

    Question will be included in next discussion round.
    Only works for running or paused discussions.
    """
    await discussion_service.inject_question(
        discussion_id=discussion_id,
        user_id=str(current_user.id),
        question=data.question,
    )
    return MessageResponse(message="Question injected successfully")


@router.get(
    "/{discussion_id}/messages",
    response_model=list[DiscussionMessageResponse],
    summary="Get discussion messages",
)
async def get_discussion_messages(
    discussion_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    discussion_service: Annotated[DiscussionService, Depends(get_discussion_service)],
    round: Annotated[
        int | None,
        Query(ge=1, description="Filter by specific round number")
    ] = None,
):
    """
    Get messages from discussion.

    - **round**: Optional filter for specific round
    Returns messages with character info and metadata.
    """
    # TODO: Implement get_messages in DiscussionService
    # For now, return empty list
    discussion = await discussion_service.get_discussion(discussion_id=discussion_id)
    # Verify ownership
    if str(discussion.user_id) != str(current_user.id):
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Discussion does not belong to this user")

    return []
