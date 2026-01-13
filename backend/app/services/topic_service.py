"""
Topic service

Manages discussion topic CRUD operations.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    NotFoundException,
    TopicNotFoundException,
    ValidationException,
)
from app.models.discussion import Discussion
from app.models.topic import Topic


class TopicService:
    """
    Topic management service.

    Handles:
    - Creating discussion topics
    - Retrieving topics by ID or listing with filters
    - Updating topic details
    - Deleting topics
    - Duplicating topics
    """

    # Valid topic statuses
    VALID_STATUSES = ["draft", "ready", "in_discussion", "completed"]

    # Editable statuses (topics in other states are locked)
    EDITABLE_STATUSES = ["draft", "ready"]

    def __init__(self, db: AsyncSession):
        """
        Initialize topic service with database session.

        Args:
            db: Async database session
        """
        self.db = db

    async def create_topic(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        context: Optional[str] = None,
        attachments: Optional[dict] = None,
        template_id: Optional[str] = None,
    ) -> Topic:
        """
        Create a new discussion topic.

        Args:
            user_id: User UUID as string
            title: Topic title (10-200 characters)
            description: Optional detailed description
            context: Optional background information
            attachments: Optional file metadata (JSONB dict)
            template_id: Optional source template ID

        Returns:
            Created Topic object

        Raises:
            ValidationException: If validation fails

        Example:
            >>> topic = await topic_service.create_topic(
            ...     user_id="123",
            ...     title="Should we launch feature X?",
            ...     description="Analyzing market demand for feature X",
            ...     context="We have received 50+ feature requests"
            ... )
        """
        # Validate title
        if not title or len(title) < 10:
            raise ValidationException(
                message="Title must be at least 10 characters",
                details={"min_length": 10, "provided_length": len(title or "")}
            )

        if len(title) > 200:
            raise ValidationException(
                message="Title must not exceed 200 characters",
                details={"max_length": 200, "provided_length": len(title)}
            )

        # Validate description
        if description is not None and len(description) > 2000:
            raise ValidationException(
                message="Description must not exceed 2000 characters",
                details={"max_length": 2000, "provided_length": len(description)}
            )

        # Validate context
        if context is not None and len(context) > 5000:
            raise ValidationException(
                message="Context must not exceed 5000 characters",
                details={"max_length": 5000, "provided_length": len(context)}
            )

        # Validate attachments format
        if attachments is not None:
            self._validate_attachments(attachments)

        # Validate template if provided
        if template_id:
            template = await self._get_topic_by_id(template_id)
            if not template:
                raise ValidationException(
                    message="Template topic not found",
                    details={"template_id": template_id}
                )

        # Create topic
        topic = Topic(
            user_id=UUID(user_id),
            title=title,
            description=description,
            context=context,
            attachments=attachments,
            status="draft",
            template_id=UUID(template_id) if template_id else None,
        )

        self.db.add(topic)
        await self.db.commit()
        await self.db.refresh(topic)

        return topic

    async def get_topic(self, topic_id: str) -> Topic:
        """
        Get topic by ID.

        Args:
            topic_id: Topic UUID as string

        Returns:
            Topic object

        Raises:
            TopicNotFoundException: If topic doesn't exist

        Example:
            >>> topic = await topic_service.get_topic(topic_id="123")
            >>> print(topic.title)
        """
        topic = await self._get_topic_by_id(topic_id)

        if not topic:
            raise TopicNotFoundException(topic_id=topic_id)

        return topic

    async def list_topics(
        self,
        user_id: str,
        status_filter: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[dict], int]:
        """
        List user's topics with pagination and filtering.

        Args:
            user_id: User UUID as string
            status_filter: Optional status filter
            search: Optional search term for title/description
            page: Page number (1-indexed)
            size: Page size (max 100)

        Returns:
            Tuple of (topics list, total count)

        Raises:
            ValidationException: If filters are invalid

        Example:
            >>> topics, total = await topic_service.list_topics(
            ...     user_id="123",
            ...     status_filter="draft",
            ...     page=1,
            ...     size=10
            ... )
        """
        # Validate pagination
        if page < 1:
            raise ValidationException(
                message="Page must be >= 1",
                details={"page": page}
            )

        if size < 1 or size > 100:
            raise ValidationException(
                message="Page size must be between 1 and 100",
                details={"size": size}
            )

        # Validate status filter
        if status_filter and status_filter not in self.VALID_STATUSES:
            raise ValidationException(
                message=f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}",
                details={"status_filter": status_filter, "valid_statuses": self.VALID_STATUSES}
            )

        # Build base query
        query = (
            select(Topic)
            .where(Topic.user_id == UUID(user_id))
        )

        # Apply status filter
        if status_filter:
            query = query.where(Topic.status == status_filter)

        # Apply search filter
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (Topic.title.ilike(search_pattern)) |
                (Topic.description.ilike(search_pattern))
            )

        # Get total count
        count_query = select(func.count(Topic.id))
        if status_filter:
            count_query = count_query.where(Topic.user_id == UUID(user_id), Topic.status == status_filter)
        else:
            count_query = count_query.where(Topic.user_id == UUID(user_id))

        if search:
            search_pattern = f"%{search}%"
            count_query = count_query.where(
                (Topic.title.ilike(search_pattern)) |
                (Topic.description.ilike(search_pattern))
            )

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Topic.created_at.desc())
        query = query.offset((page - 1) * size).limit(size)

        # Execute query
        result = await self.db.execute(query)
        topics = result.scalars().all()

        # Convert to dict format with discussion count
        topic_list = []
        for topic in topics:
            # Get discussion count
            count_result = await self.db.execute(
                select(func.count(Discussion.id)).where(
                    Discussion.topic_id == topic.id
                )
            )
            discussion_count = count_result.scalar() or 0

            topic_list.append({
                "id": str(topic.id),
                "title": topic.title,
                "status": topic.status,
                "created_at": topic.created_at,
                "discussion_count": discussion_count,
            })

        return topic_list, total

    async def update_topic(
        self,
        topic_id: str,
        user_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        context: Optional[str] = None,
        attachments: Optional[dict] = None,
        status: Optional[str] = None,
    ) -> Topic:
        """
        Update topic details.

        Only topics in 'draft' or 'ready' status can be updated.

        Args:
            topic_id: Topic UUID as string
            user_id: User UUID as string (for authorization)
            title: New title (optional)
            description: New description (optional)
            context: New context (optional)
            attachments: New attachments (optional)
            status: New status (optional)

        Returns:
            Updated Topic object

        Raises:
            TopicNotFoundException: If topic doesn't exist
            ValidationException: If validation fails or authorization denied

        Example:
            >>> topic = await topic_service.update_topic(
            ...     topic_id="123",
            ...     user_id="456",
            ...     title="Updated title",
            ...     status="ready"
            ... )
        """
        # Get topic
        topic = await self._get_topic_by_id(topic_id)

        if not topic:
            raise TopicNotFoundException(topic_id=topic_id)

        # Verify ownership
        if str(topic.user_id) != user_id:
            raise ValidationException(
                message="Topic does not belong to this user",
                details={"topic_id": topic_id, "user_id": user_id}
            )

        # Check if topic is editable
        if topic.status not in self.EDITABLE_STATUSES:
            raise ValidationException(
                message=f"Cannot update topic in '{topic.status}' status",
                details={
                    "current_status": topic.status,
                    "editable_statuses": self.EDITABLE_STATUSES
                }
            )

        # Update title
        if title is not None:
            if len(title) < 10 or len(title) > 200:
                raise ValidationException(
                    message="Title must be 10-200 characters",
                    details={"min_length": 10, "max_length": 200, "provided_length": len(title)}
                )
            topic.title = title

        # Update description
        if description is not None:
            if len(description) > 2000:
                raise ValidationException(
                    message="Description must not exceed 2000 characters",
                    details={"max_length": 2000, "provided_length": len(description)}
                )
            topic.description = description

        # Update context
        if context is not None:
            if len(context) > 5000:
                raise ValidationException(
                    message="Context must not exceed 5000 characters",
                    details={"max_length": 5000, "provided_length": len(context)}
                )
            topic.context = context

        # Update attachments
        if attachments is not None:
            self._validate_attachments(attachments)
            topic.attachments = attachments

        # Update status
        if status is not None:
            if status not in self.VALID_STATUSES:
                raise ValidationException(
                    message=f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}",
                    details={"status": status, "valid_statuses": self.VALID_STATUSES}
                )
            topic.status = status

        await self.db.commit()
        await self.db.refresh(topic)

        return topic

    async def delete_topic(self, topic_id: str, user_id: str) -> bool:
        """
        Delete a topic.

        Topics can only be deleted if they have no running discussions.

        Args:
            topic_id: Topic UUID as string
            user_id: User UUID as string (for authorization)

        Returns:
            True if deleted successfully

        Raises:
            TopicNotFoundException: If topic doesn't exist
            ValidationException: If topic has running discussions or ownership mismatch

        Example:
            >>> success = await topic_service.delete_topic(
            ...     topic_id="123",
            ...     user_id="456"
            ... )
        """
        # Get topic
        topic = await self._get_topic_by_id(topic_id)

        if not topic:
            raise TopicNotFoundException(topic_id=topic_id)

        # Verify ownership
        if str(topic.user_id) != user_id:
            raise ValidationException(
                message="Topic does not belong to this user",
                details={"topic_id": topic_id, "user_id": user_id}
            )

        # Check for running discussions
        running_result = await self.db.execute(
            select(func.count(Discussion.id)).where(
                Discussion.topic_id == UUID(topic_id),
                Discussion.status == "running"
            )
        )
        running_count = running_result.scalar() or 0

        if running_count > 0:
            raise ValidationException(
                message="Cannot delete topic with running discussions",
                details={"running_discussions": running_count}
            )

        # Delete topic (CASCADE will delete related discussions and messages)
        await self.db.delete(topic)
        await self.db.commit()

        return True

    async def duplicate_topic(
        self,
        topic_id: str,
        user_id: str,
    ) -> Topic:
        """
        Duplicate an existing topic.

        Creates a copy of the topic with the same content but a new ID.

        Args:
            topic_id: Topic UUID as string to duplicate
            user_id: User UUID as string (for authorization)

        Returns:
            New duplicated Topic object

        Raises:
            TopicNotFoundException: If topic doesn't exist
            ValidationException: If ownership mismatch

        Example:
            >>> new_topic = await topic_service.duplicate_topic(
            ...     topic_id="123",
            ...     user_id="456"
            ... )
        """
        # Get original topic
        original = await self._get_topic_by_id(topic_id)

        if not original:
            raise TopicNotFoundException(topic_id=topic_id)

        # Verify ownership
        if str(original.user_id) != user_id:
            raise ValidationException(
                message="Topic does not belong to this user",
                details={"topic_id": topic_id, "user_id": user_id}
            )

        # Create duplicate
        duplicate = Topic(
            user_id=UUID(user_id),
            title=f"{original.title} (Copy)",
            description=original.description,
            context=original.context,
            attachments=original.attachments,
            status="draft",
            template_id=original.id,  # Reference original as template
        )

        self.db.add(duplicate)
        await self.db.commit()
        await self.db.refresh(duplicate)

        return duplicate

    async def _get_topic_by_id(self, topic_id: str) -> Optional[Topic]:
        """
        Get topic by ID.

        Args:
            topic_id: Topic UUID as string

        Returns:
            Topic object or None
        """
        result = await self.db.execute(
            select(Topic).where(Topic.id == UUID(topic_id))
        )
        return result.scalar_one_or_none()

    def _validate_attachments(self, attachments: dict) -> None:
        """
        Validate attachments format.

        Args:
            attachments: Attachments dict to validate

        Raises:
            ValidationException: If format is invalid
        """
        if not isinstance(attachments, dict):
            raise ValidationException(
                message="Attachments must be a dictionary",
                details={"type": type(attachments).__name__}
            )

        # Check for 'files' key
        if "files" not in attachments:
            return  # No files to validate

        files = attachments["files"]
        if not isinstance(files, list):
            raise ValidationException(
                message="Attachments files must be a list",
                details={"files_type": type(files).__name__}
            )

        # Check file count limit
        if len(files) > 5:
            raise ValidationException(
                message="Maximum 5 files allowed",
                details={"file_count": len(files), "max_files": 5}
            )

        # Validate each file entry
        for i, file_entry in enumerate(files):
            if not isinstance(file_entry, dict):
                raise ValidationException(
                    message=f"File entry {i} must be a dictionary",
                    details={"entry_index": i, "type": type(file_entry).__name__}
                )

            # Check required fields
            required_fields = ["name", "url", "size", "type"]
            for field in required_fields:
                if field not in file_entry:
                    raise ValidationException(
                        message=f"File entry {i} missing required field: {field}",
                        details={"entry_index": i, "missing_field": field}
                    )
