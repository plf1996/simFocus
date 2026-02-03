from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from typing import Any

if False:
    from app.models.user import User

from app.core.database import get_db, async_session_factory
from app.api.dependencies import get_current_user
from app.schemas.discussion import (
    DiscussionCreate,
    DiscussionUpdate,
    DiscussionResponse,
    DiscussionListItem,
    DiscussionControl
)
from app.schemas.message import MessageResponse
from app.services.discussion_engine import DiscussionEngineService
from app.services.report_generator import ReportGeneratorService
from app.services.llm_orchestrator import LLMOrchestrator
from app.core.redis import get_cache_service


router = APIRouter(prefix="/api/discussions", tags=["Discussions"])


@router.get("", response_model=List[DiscussionListItem])
async def get_discussions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all discussions for current user"""
    from sqlalchemy import select
    from app.models.discussion import Discussion
    from app.models.topic import Topic

    # Query discussions with topic title
    result = await db.execute(
        select(Discussion, Topic.title)
        .join(Topic, Discussion.topic_id == Topic.id)
        .where(Discussion.user_id == current_user.id)
        .order_by(Discussion.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    discussions_with_titles = result.all()
    discussions_list = []
    for disc, topic_title in discussions_with_titles:
        # Create a dict with all fields plus topic_title
        disc_dict = {
            "id": disc.id,
            "topic_id": disc.topic_id,
            "topic_title": topic_title,
            "status": disc.status,
            "current_round": disc.current_round,
            "max_rounds": disc.max_rounds,
            "created_at": disc.created_at
        }
        discussions_list.append(DiscussionListItem(**disc_dict))

    return discussions_list


@router.post("", response_model=DiscussionResponse)
async def create_discussion(
    discussion_data: DiscussionCreate,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new discussion"""
    service = DiscussionEngineService(
            db,
            LLMOrchestrator(),
            await get_cache_service(),
            session_factory=async_session_factory
        )
    discussion = await service.create_discussion(current_user.id, discussion_data)
    return DiscussionResponse.model_validate(discussion)


@router.get("/{discussion_id}", response_model=DiscussionResponse)
async def get_discussion(
    discussion_id: UUID,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific discussion"""
    service = DiscussionEngineService(
            db,
            LLMOrchestrator(),
            await get_cache_service(),
            session_factory=async_session_factory
        )
    discussion = await service.get_discussion_by_id(discussion_id, current_user.id)

    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion not found"
        )

    return DiscussionResponse.model_validate(discussion)


@router.delete("/{discussion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_discussion(
    discussion_id: UUID,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a discussion"""
    service = DiscussionEngineService(
            db,
            LLMOrchestrator(),
            await get_cache_service(),
            session_factory=async_session_factory
        )
    discussion = await service.get_discussion_by_id(discussion_id, current_user.id)

    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion not found"
        )

    # TODO: Implement soft delete or cascade delete
    await db.delete(discussion)
    await db.commit()


@router.post("/{discussion_id}/start", response_model=DiscussionResponse)
async def start_discussion(
    discussion_id: UUID,
    provider_name: Optional[str] = Query(None),
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a discussion"""
    from sqlalchemy import select
    from app.models.api_key import UserAPIKey

    # Get user's API keys
    result = await db.execute(
        select(UserAPIKey).where(
            UserAPIKey.user_id == current_user.id,
            UserAPIKey.is_active == True
        )
    )
    api_keys = result.scalars().all()

    if not api_keys:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active API key found. Please configure your API key first."
        )

    # Create orchestrator and register providers
    orchestrator = LLMOrchestrator()

    # Use the first API key if provider_name is 'default', otherwise find the matching one
    selected_key = None
    if provider_name and provider_name != "default":
        for api_key_obj in api_keys:
            if api_key_obj.key_name == provider_name:
                selected_key = api_key_obj
                break
    else:
        selected_key = api_keys[0]  # Use first API key

    # Register all user's API keys as providers
    for api_key_obj in api_keys:
        # Decrypt API key
        from app.core.security import decrypt_api_key
        decrypted_key = decrypt_api_key(api_key_obj.encrypted_key)

        # Register provider
        orchestrator.register_provider(
            name=api_key_obj.key_name,
            provider_type=api_key_obj.provider,
            api_key=decrypted_key,
            base_url=api_key_obj.api_base_url,
            model=api_key_obj.default_model
        )

    service = DiscussionEngineService(
        db,
        orchestrator,
        await get_cache_service(),
        session_factory=async_session_factory
    )

    try:
        # Use the selected key's name as provider
        actual_provider_name = selected_key.key_name
        discussion = await service.start_discussion(discussion_id, current_user.id, actual_provider_name)

        # Ensure all attributes are loaded before serialization
        _ = discussion.id, discussion.topic_id, discussion.user_id, discussion.discussion_mode
        _ = discussion.max_rounds, discussion.status, discussion.current_round
        _ = discussion.current_phase, discussion.llm_provider, discussion.llm_model
        _ = discussion.total_tokens_used, discussion.estimated_cost_usd
        _ = discussion.started_at, discussion.completed_at, discussion.created_at, discussion.updated_at

        return DiscussionResponse.model_validate(discussion)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{discussion_id}/pause", response_model=DiscussionResponse)
async def pause_discussion(
    discussion_id: UUID,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Pause a running discussion"""
    service = DiscussionEngineService(
            db,
            LLMOrchestrator(),
            await get_cache_service(),
            session_factory=async_session_factory
        )

    try:
        discussion = await service.pause_discussion(discussion_id, current_user.id)
        return DiscussionResponse.model_validate(discussion)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{discussion_id}/resume", response_model=DiscussionResponse)
async def resume_discussion(
    discussion_id: UUID,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Resume a paused discussion"""
    service = DiscussionEngineService(
            db,
            LLMOrchestrator(),
            await get_cache_service(),
            session_factory=async_session_factory
        )

    try:
        discussion = await service.resume_discussion(discussion_id, current_user.id)
        return DiscussionResponse.model_validate(discussion)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{discussion_id}/stop", response_model=DiscussionResponse)
async def stop_discussion(
    discussion_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stop a discussion and generate report"""
    service = DiscussionEngineService(
            db,
            LLMOrchestrator(),
            await get_cache_service(),
            session_factory=async_session_factory
        )

    try:
        discussion = await service.stop_discussion(discussion_id, current_user.id)

        # Generate report in background
        if discussion.status == "completed":
            report_service = ReportGeneratorService(db, LLMOrchestrator())
            background_tasks.add_task(report_service.generate_report, discussion_id)

        return DiscussionResponse.model_validate(discussion)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{discussion_id}/inject-question", response_model=MessageResponse)
async def inject_question(
    discussion_id: UUID,
    question: str,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Inject a user question into the discussion"""
    service = DiscussionEngineService(
            db,
            LLMOrchestrator(),
            await get_cache_service(),
            session_factory=async_session_factory
        )

    try:
        message = await service.inject_question(discussion_id, current_user.id, question)
        return MessageResponse.model_validate(message)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{discussion_id}/messages", response_model=List[MessageResponse])
async def get_discussion_messages(
    discussion_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a discussion"""
    service = DiscussionEngineService(
            db,
            LLMOrchestrator(),
            await get_cache_service(),
            session_factory=async_session_factory
        )

    try:
        messages = await service.get_discussion_messages(discussion_id, current_user.id, skip, limit)

        # Enrich with character info
        from app.models.participant import DiscussionParticipant
        from app.models.character import Character
        from sqlalchemy import select

        enriched_messages = []
        for msg in messages:
            # Check if this is a user-injected question (special UUID)
            if msg.is_injected_question or str(msg.participant_id) == "00000000-0000-0000-0000-000000000000":
                enriched_message = MessageResponse(
                    id=msg.id,
                    discussion_id=msg.discussion_id,
                    participant_id=msg.participant_id,
                    character_name="User",
                    character_avatar_url=None,
                    content=msg.content,
                    phase=msg.phase,
                    round=msg.round,
                    token_count=msg.token_count,
                    is_injected_question=msg.is_injected_question,
                    metadata=msg.meta_data,
                    created_at=msg.created_at
                )
                enriched_messages.append(enriched_message)
            else:
                # Get participant and character
                result = await db.execute(
                    select(DiscussionParticipant, Character)
                    .join(Character, DiscussionParticipant.character_id == Character.id)
                    .where(DiscussionParticipant.id == msg.participant_id)
                )
                participant_data = result.first()

                if participant_data:
                    participant, character = participant_data
                    enriched_message = MessageResponse(
                        id=msg.id,
                        discussion_id=msg.discussion_id,
                        participant_id=msg.participant_id,
                        character_name=character.name,
                        character_avatar_url=character.avatar_url,
                        content=msg.content,
                        phase=msg.phase,
                        round=msg.round,
                        token_count=msg.token_count,
                        is_injected_question=msg.is_injected_question,
                        metadata=msg.meta_data,
                        created_at=msg.created_at
                    )
                    enriched_messages.append(enriched_message)
                else:
                    # Fallback for missing participant data
                    enriched_message = MessageResponse(
                        id=msg.id,
                        discussion_id=msg.discussion_id,
                        participant_id=msg.participant_id,
                        character_name="Unknown",
                        character_avatar_url=None,
                        content=msg.content,
                        phase=msg.phase,
                        round=msg.round,
                        token_count=msg.token_count,
                        is_injected_question=msg.is_injected_question,
                        metadata=msg.meta_data,
                        created_at=msg.created_at
                    )
                    enriched_messages.append(enriched_message)

        return enriched_messages
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
