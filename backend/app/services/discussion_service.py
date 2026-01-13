"""
Discussion service

Manages discussion lifecycle including creation, execution control,
and message injection.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    APIKeyNotFoundException,
    DiscussionNotFoundException,
    DiscussionNotActiveException,
    NotFoundException,
    TopicNotFoundException,
    ValidationException,
)
from app.models.character import Character
from app.models.discussion import Discussion, DiscussionParticipant
from app.models.topic import Topic
from app.services.api_key_service import ApiKeyService
from sqlalchemy.orm import joinedload


class DiscussionService:
    """
    Discussion management service.

    Handles:
    - Creating discussions with participants
    - Retrieving discussions
    - Listing user's discussions
    - Starting/pausing/resuming/stopping discussions
    - Injecting user questions into active discussions
    """

    # Valid discussion modes
    VALID_MODES = ["free", "structured", "creative", "consensus"]

    # Valid discussion statuses
    VALID_STATUSES = ["initialized", "running", "paused", "completed", "failed"]

    # Valid discussion phases
    VALID_PHASES = ["opening", "development", "debate", "closing"]

    # Valid participant stances (for structured mode)
    VALID_STANCES = ["pro", "con", "neutral"]

    def __init__(self, db: AsyncSession):
        """
        Initialize discussion service with database session.

        Args:
            db: Async database session
        """
        self.db = db

    async def create_discussion(
        self,
        user_id: str,
        topic_id: str,
        character_ids: list[str],
        discussion_mode: str = "free",
        max_rounds: int = 10,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
    ) -> Discussion:
        """
        Create a new discussion with participants.

        Args:
            user_id: User UUID as string
            topic_id: Topic UUID as string
            character_ids: List of character UUIDs (3-7 characters)
            discussion_mode: Discussion mode (default: "free")
            max_rounds: Maximum discussion rounds (default: 10, range: 5-20)
            llm_provider: Optional LLM provider (default: from active API key)
            llm_model: Optional LLM model (default: from active API key)

        Returns:
            Created Discussion object with participants

        Raises:
            ValidationException: If validation fails

        Example:
            >>> discussion = await discussion_service.create_discussion(
            ...     user_id="123",
            ...     topic_id="456",
            ...     character_ids=["789", "790", "791"],
            ...     discussion_mode="free",
            ...     max_rounds=10
            ... )
        """
        # Validate discussion mode
        if discussion_mode not in self.VALID_MODES:
            raise ValidationException(
                message=f"Invalid discussion mode. Must be one of: {', '.join(self.VALID_MODES)}",
                details={"discussion_mode": discussion_mode, "valid_modes": self.VALID_MODES}
            )

        # Validate max_rounds
        if not (5 <= max_rounds <= 20):
            raise ValidationException(
                message="max_rounds must be between 5 and 20",
                details={"max_rounds": max_rounds, "min": 5, "max": 20}
            )

        # Validate character count
        if not (3 <= len(character_ids) <= 7):
            raise ValidationException(
                message="Discussion must have 3-7 participants",
                details={"character_count": len(character_ids), "min": 3, "max": 7}
            )

        # Get topic
        topic = await self._get_topic_by_id(topic_id)
        if not topic:
            raise TopicNotFoundException(topic_id=topic_id)

        # Verify topic ownership
        if str(topic.user_id) != user_id:
            raise ValidationException(
                message="Topic does not belong to this user",
                details={"topic_id": topic_id, "user_id": user_id}
            )

        # Check topic is ready for discussion
        if topic.status not in ("ready", "completed"):
            raise ValidationException(
                message=f"Topic status must be 'ready' or 'completed', not '{topic.status}'",
                details={"topic_status": topic.status}
            )

        # Get characters and verify they exist
        characters = []
        for char_id in character_ids:
            character = await self._get_character_by_id(char_id)
            if not character:
                raise ValidationException(
                    message=f"Character not found",
                    details={"character_id": char_id}
                )
            characters.append(character)

        # Check for duplicates
        unique_ids = set(character_ids)
        if len(unique_ids) != len(character_ids):
            raise ValidationException(
                message="Duplicate characters in participant list",
                details={"character_ids": character_ids}
            )

        # Get API key info for provider/model
        api_key_service = ApiKeyService(self.db)
        try:
            api_key, base_url, default_model = await api_key_service.get_active_api_key(user_id)
            # Use provided or fall back to API key defaults
            final_provider = llm_provider or self._detect_provider_from_key(api_key)
            final_model = llm_model or default_model or self._get_default_model(final_provider)
        except APIKeyNotFoundException:
            raise ValidationException(
                message="No active API key found. Please configure an API key first.",
                details={"user_id": user_id}
            )

        # Create discussion
        discussion = Discussion(
            topic_id=UUID(topic_id),
            user_id=UUID(user_id),
            discussion_mode=discussion_mode,
            max_rounds=max_rounds,
            status="initialized",
            current_round=0,
            current_phase="opening",
            llm_provider=final_provider,
            llm_model=final_model,
            total_tokens_used=0,
            estimated_cost_usd=None,
            started_at=None,
            completed_at=None,
        )

        self.db.add(discussion)
        await self.db.flush()  # Get discussion ID without committing

        # Create participants
        participants = []
        for idx, character in enumerate(characters):
            # Determine stance for structured mode
            stance = None
            position = None

            if discussion_mode == "structured":
                # Assign stances in round-robin: pro, con, neutral, pro, con, neutral...
                stance = self.VALID_STANCES[idx % len(self.VALID_STANCES)]
                position = idx + 1

            participant = DiscussionParticipant(
                discussion_id=discussion.id,
                character_id=character.id,
                position=position,
                stance=stance,
                message_count=0,
                total_tokens=0,
            )

            self.db.add(participant)
            participants.append(participant)

        # Commit everything
        await self.db.commit()
        await self.db.refresh(discussion)

        # Load relationships for response
        discussion = await self._get_discussion_with_participants(str(discussion.id))

        return discussion

    async def get_discussion(self, discussion_id: str) -> Discussion:
        """
        Get discussion by ID with full details.

        Args:
            discussion_id: Discussion UUID as string

        Returns:
            Discussion object with relationships loaded

        Raises:
            DiscussionNotFoundException: If discussion doesn't exist

        Example:
            >>> discussion = await discussion_service.get_discussion(discussion_id="123")
            >>> print(f"Status: {discussion.status}, Round: {discussion.current_round}")
        """
        discussion = await self._get_discussion_with_participants(discussion_id)

        if not discussion:
            raise DiscussionNotFoundException(discussion_id=discussion_id)

        return discussion

    async def list_discussions(
        self,
        user_id: str,
        status_filter: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        """
        List user's discussions with filtering.

        Args:
            user_id: User UUID as string
            status_filter: Optional status filter
            limit: Maximum number of discussions to return

        Returns:
            List of discussion summary dicts

        Raises:
            ValidationException: If filters are invalid

        Example:
            >>> discussions = await discussion_service.list_discussions(
            ...     user_id="123",
            ...     status_filter="completed"
            ... )
        """
        # Validate status filter
        if status_filter and status_filter not in self.VALID_STATUSES:
            raise ValidationException(
                message=f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}",
                details={"status_filter": status_filter, "valid_statuses": self.VALID_STATUSES}
            )

        # Build query
        query = (
            select(Discussion)
            .where(Discussion.user_id == UUID(user_id))
            .options(selectinload(Discussion.topic))
        )

        # Apply status filter
        if status_filter:
            query = query.where(Discussion.status == status_filter)

        # Order and limit
        query = query.order_by(Discussion.created_at.desc()).limit(limit)

        # Execute query
        result = await self.db.execute(query)
        discussions = result.scalars().all()

        # Get participant counts
        discussion_list = []
        for discussion in discussions:
            # Get participant count
            count_result = await self.db.execute(
                select(DiscussionParticipant).where(
                    DiscussionParticipant.discussion_id == discussion.id
                )
            )
            participants = count_result.scalars().all()
            participant_count = len(participants)

            discussion_list.append({
                "id": str(discussion.id),
                "title": discussion.topic.title,
                "status": discussion.status,
                "discussion_mode": discussion.discussion_mode,
                "participant_count": participant_count,
                "created_at": discussion.created_at,
                "completed_at": discussion.completed_at,
            })

        return discussion_list

    async def start_discussion(self, discussion_id: str, user_id: str) -> Discussion:
        """
        Start a discussion.

        Initializes the discussion and begins the discussion engine.
        Status must transition from 'initialized' to 'running'.

        Args:
            discussion_id: Discussion UUID as string
            user_id: User UUID as string (for authorization)

        Returns:
            Updated Discussion object

        Raises:
            DiscussionNotFoundException: If discussion doesn't exist
            DiscussionNotActiveException: If discussion is not in valid state
            ValidationException: If authorization fails

        Example:
            >>> discussion = await discussion_service.start_discussion(
            ...     discussion_id="123",
            ...     user_id="456"
            ... )
        """
        # Get discussion
        discussion = await self._get_discussion_with_participants(discussion_id)

        if not discussion:
            raise DiscussionNotFoundException(discussion_id=discussion_id)

        # Verify ownership
        if str(discussion.user_id) != user_id:
            raise ValidationException(
                message="Discussion does not belong to this user",
                details={"discussion_id": discussion_id, "user_id": user_id}
            )

        # Check current status
        if discussion.status != "initialized":
            raise DiscussionNotActiveException(
                discussion_id=discussion_id,
                current_state=discussion.status
            )

        # Update status to running
        discussion.status = "running"
        discussion.started_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(discussion)

        # TODO: Trigger discussion engine to start generating messages
        # This should be done via background task or message queue
        # await self._start_discussion_engine(discussion)

        return discussion

    async def pause_discussion(self, discussion_id: str, user_id: str) -> Discussion:
        """
        Pause a running discussion.

        Args:
            discussion_id: Discussion UUID as string
            user_id: User UUID as string (for authorization)

        Returns:
            Updated Discussion object

        Raises:
            DiscussionNotFoundException: If discussion doesn't exist
            DiscussionNotActiveException: If discussion is not running
            ValidationException: If authorization fails

        Example:
            >>> discussion = await discussion_service.pause_discussion(
            ...     discussion_id="123",
            ...     user_id="456"
            ... )
        """
        # Get discussion
        discussion = await self._get_discussion_with_participants(discussion_id)

        if not discussion:
            raise DiscussionNotFoundException(discussion_id=discussion_id)

        # Verify ownership
        if str(discussion.user_id) != user_id:
            raise ValidationException(
                message="Discussion does not belong to this user",
                details={"discussion_id": discussion_id, "user_id": user_id}
            )

        # Check current status
        if discussion.status != "running":
            raise DiscussionNotActiveException(
                discussion_id=discussion_id,
                current_state=discussion.status
            )

        # Update status to paused
        discussion.status = "paused"

        await self.db.commit()
        await self.db.refresh(discussion)

        # TODO: Signal discussion engine to pause
        # This should update the cached state in Redis

        return discussion

    async def resume_discussion(self, discussion_id: str, user_id: str) -> Discussion:
        """
        Resume a paused discussion.

        Args:
            discussion_id: Discussion UUID as string
            user_id: User UUID as string (for authorization)

        Returns:
            Updated Discussion object

        Raises:
            DiscussionNotFoundException: If discussion doesn't exist
            DiscussionNotActiveException: If discussion is not paused
            ValidationException: If authorization fails

        Example:
            >>> discussion = await discussion_service.resume_discussion(
            ...     discussion_id="123",
            ...     user_id="456"
            ... )
        """
        # Get discussion
        discussion = await self._get_discussion_with_participants(discussion_id)

        if not discussion:
            raise DiscussionNotFoundException(discussion_id=discussion_id)

        # Verify ownership
        if str(discussion.user_id) != user_id:
            raise ValidationException(
                message="Discussion does not belong to this user",
                details={"discussion_id": discussion_id, "user_id": user_id}
            )

        # Check current status
        if discussion.status != "paused":
            raise DiscussionNotActiveException(
                discussion_id=discussion_id,
                current_state=discussion.status
            )

        # Update status to running
        discussion.status = "running"

        await self.db.commit()
        await self.db.refresh(discussion)

        # TODO: Signal discussion engine to resume
        # This should update the cached state in Redis

        return discussion

    async def stop_discussion(self, discussion_id: str, user_id: str) -> Discussion:
        """
        Stop a discussion and mark as completed.

        Triggers report generation.

        Args:
            discussion_id: Discussion UUID as string
            user_id: User UUID as string (for authorization)

        Returns:
            Updated Discussion object

        Raises:
            DiscussionNotFoundException: If discussion doesn't exist
            DiscussionNotActiveException: If discussion is already finished
            ValidationException: If authorization fails

        Example:
            >>> discussion = await discussion_service.stop_discussion(
            ...     discussion_id="123",
            ...     user_id="456"
            ... )
        """
        # Get discussion
        discussion = await self._get_discussion_with_participants(discussion_id)

        if not discussion:
            raise DiscussionNotFoundException(discussion_id=discussion_id)

        # Verify ownership
        if str(discussion.user_id) != user_id:
            raise ValidationException(
                message="Discussion does not belong to this user",
                details={"discussion_id": discussion_id, "user_id": user_id}
            )

        # Check if already finished
        if discussion.status in ("completed", "failed"):
            raise DiscussionNotActiveException(
                discussion_id=discussion_id,
                current_state=discussion.status
            )

        # Update status to completed
        discussion.status = "completed"
        discussion.completed_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(discussion)

        # TODO: Trigger report generation
        # await self._generate_report(discussion)

        return discussion

    async def inject_question(
        self,
        discussion_id: str,
        user_id: str,
        question: str,
    ) -> bool:
        """
        Inject a user question into an active discussion.

        The question will be included in the next discussion round.

        Args:
            discussion_id: Discussion UUID as string
            user_id: User UUID as string (for authorization)
            question: Question to inject (10-500 characters)

        Returns:
            True if question injected successfully

        Raises:
            DiscussionNotFoundException: If discussion doesn't exist
            DiscussionNotActiveException: If discussion is not active
            ValidationException: If validation fails

        Example:
            >>> success = await discussion_service.inject_question(
            ...     discussion_id="123",
            ...     user_id="456",
            ...     question="What about the cost implications?"
            ... )
        """
        # Validate question length
        if len(question) < 10 or len(question) > 500:
            raise ValidationException(
                message="Question must be 10-500 characters",
                details={"min_length": 10, "max_length": 500, "provided_length": len(question)}
            )

        # Get discussion
        discussion = await self._get_discussion_with_participants(discussion_id)

        if not discussion:
            raise DiscussionNotFoundException(discussion_id=discussion_id)

        # Verify ownership
        if str(discussion.user_id) != user_id:
            raise ValidationException(
                message="Discussion does not belong to this user",
                details={"discussion_id": discussion_id, "user_id": user_id}
            )

        # Check if discussion is active
        if discussion.status not in ("running", "paused"):
            raise DiscussionNotActiveException(
                discussion_id=discussion_id,
                current_state=discussion.status
            )

        # TODO: Store injected question for next round
        # This should be stored in Redis or database
        # await self._store_injected_question(discussion_id, question)

        return True

    async def delete_discussion(self, discussion_id: str, user_id: str) -> bool:
        """
        Delete a discussion.

        Performs soft delete. Can only delete discussions that are not currently running.
        Cascade deletes messages and participants.

        Args:
            discussion_id: Discussion UUID as string
            user_id: User UUID as string (for authorization)

        Returns:
            True if deleted successfully

        Raises:
            DiscussionNotFoundException: If discussion doesn't exist
            DiscussionNotActiveException: If discussion is currently running
            ValidationException: If authorization fails

        Example:
            >>> success = await discussion_service.delete_discussion(
            ...     discussion_id="123",
            ...     user_id="456"
            ... )
        """
        from app.models.discussion import DiscussionMessage

        # Get discussion
        discussion = await self._get_discussion_with_participants(discussion_id)

        if not discussion:
            raise DiscussionNotFoundException(discussion_id=discussion_id)

        # Verify ownership
        if str(discussion.user_id) != user_id:
            raise ValidationException(
                message="Discussion does not belong to this user",
                details={"discussion_id": discussion_id, "user_id": user_id}
            )

        # Check if discussion is running
        if discussion.status == "running":
            raise ValidationException(
                message="Cannot delete discussion that is currently running. Stop it first.",
                details={"discussion_id": discussion_id, "current_status": discussion.status}
            )

        # Delete messages
        await self.db.execute(
            delete(DiscussionMessage).where(
                DiscussionMessage.discussion_id == UUID(discussion_id)
            )
        )

        # Delete discussion (participants and report will be cascade deleted)
        await self.db.execute(
            delete(Discussion).where(
                Discussion.id == UUID(discussion_id)
            )
        )

        await self.db.commit()

        return True

    async def get_discussion_messages(
        self,
        discussion_id: str,
        user_id: str,
        round_filter: Optional[int] = None,
    ) -> list[dict]:
        """
        Get messages from a discussion.

        Args:
            discussion_id: Discussion UUID as string
            user_id: User UUID as string (for authorization)
            round_filter: Optional round number to filter messages

        Returns:
            List of message dictionaries with character info

        Raises:
            DiscussionNotFoundException: If discussion doesn't exist
            ValidationException: If authorization fails

        Example:
            >>> messages = await discussion_service.get_discussion_messages(
            ...     discussion_id="123",
            ...     user_id="456",
            ...     round_filter=3
            ... )
        """
        from app.models.discussion import DiscussionMessage

        # Get discussion to verify ownership
        discussion = await self._get_discussion_with_participants(discussion_id)

        if not discussion:
            raise DiscussionNotFoundException(discussion_id=discussion_id)

        # Verify ownership
        if str(discussion.user_id) != user_id:
            raise ValidationException(
                message="Discussion does not belong to this user",
                details={"discussion_id": discussion_id, "user_id": user_id}
            )

        # Build query for messages
        query = (
            select(DiscussionMessage)
            .join(DiscussionParticipant, DiscussionMessage.participant_id == DiscussionParticipant.id)
            .join(Character, DiscussionParticipant.character_id == Character.id)
            .where(DiscussionMessage.discussion_id == UUID(discussion_id))
            .order_by(DiscussionMessage.created_at.asc())
        )

        # Apply round filter if specified
        if round_filter is not None:
            query = query.where(DiscussionMessage.round == round_filter)

        # Execute query
        result = await self.db.execute(query)
        messages = result.scalars().all()

        # Format response
        message_list = []
        for msg in messages:
            # Get participant and character info
            participant = msg.participant
            character = participant.character if participant else None

            message_list.append({
                "id": str(msg.id),
                "participant_id": str(msg.participant_id),
                "character_name": character.name if character else "Unknown",
                "character_avatar": character.avatar_url if character else None,
                "round": msg.round,
                "phase": msg.phase,
                "content": msg.content,
                "token_count": msg.token_count,
                "is_injected_question": msg.is_injected_question,
                "created_at": msg.created_at,
            })

        return message_list

    async def _get_topic_by_id(self, topic_id: str) -> Optional[Topic]:
        """Get topic by ID."""
        result = await self.db.execute(
            select(Topic).where(Topic.id == UUID(topic_id))
        )
        return result.scalar_one_or_none()

    async def _get_character_by_id(self, character_id: str) -> Optional[Character]:
        """Get character by ID."""
        result = await self.db.execute(
            select(Character).where(Character.id == UUID(character_id))
        )
        return result.scalar_one_or_none()

    async def _get_discussion_with_participants(self, discussion_id: str) -> Optional[Discussion]:
        """
        Get discussion with participants loaded.

        Args:
            discussion_id: Discussion UUID as string

        Returns:
            Discussion object or None
        """
        result = await self.db.execute(
            select(Discussion)
            .options(
                selectinload(Discussion.participants).selectinload(DiscussionParticipant.character),
                selectinload(Discussion.topic),
            )
            .where(Discussion.id == UUID(discussion_id))
        )
        return result.scalar_one_or_none()

    def _detect_provider_from_key(self, api_key: str) -> str:
        """
        Detect LLM provider from API key format.

        Args:
            api_key: API key string

        Returns:
            Provider name (openai, anthropic, or custom)
        """
        # OpenAI keys start with 'sk-'
        if api_key.startswith("sk-"):
            return "openai"

        # Anthropic keys start with 'sk-ant-'
        if api_key.startswith("sk-ant-"):
            return "anthropic"

        # Default to custom
        return "custom"

    def _get_default_model(self, provider: str) -> str:
        """
        Get default model for provider.

        Args:
            provider: Provider name

        Returns:
            Default model identifier
        """
        defaults = {
            "openai": "gpt-4",
            "anthropic": "claude-3-opus-20240229",
            "custom": "gpt-3.5-turbo",
        }
        return defaults.get(provider, "gpt-3.5-turbo")
