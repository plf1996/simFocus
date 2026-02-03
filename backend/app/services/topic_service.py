from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, or_
from typing import Optional, List
from uuid import UUID

from app.models.topic import Topic
from app.models.discussion import Discussion
from app.schemas.topic import TopicCreate, TopicUpdate, TopicResponse, TopicListItem


class TopicService:
    """Service for topic management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_topic_by_id(self, topic_id: UUID, user_id: UUID) -> Optional[Topic]:
        """Get topic by ID (ensuring user owns it)"""
        result = await self.db.execute(
            select(Topic).where(
                and_(Topic.id == topic_id, Topic.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_user_topics(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Topic]:
        """Get topics for a user with optional status filter and pagination"""
        query = select(Topic).where(Topic.user_id == user_id)

        if status:
            query = query.where(Topic.status == status)

        query = query.order_by(desc(Topic.updated_at)).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_topic(self, user_id: UUID, topic_data: TopicCreate) -> Topic:
        """Create new topic"""
        topic = Topic(
            user_id=user_id,
            title=topic_data.title,
            description=topic_data.description,
            context=topic_data.context,
            attachments=topic_data.attachments,
            status="draft"
        )
        self.db.add(topic)
        await self.db.commit()
        await self.db.refresh(topic)
        return topic

    async def update_topic(
        self,
        topic_id: UUID,
        user_id: UUID,
        topic_data: TopicUpdate
    ) -> Optional[Topic]:
        """Update topic"""
        topic = await self.get_topic_by_id(topic_id, user_id)
        if not topic:
            return None

        # Cannot update topic if discussion is running
        if topic.status == "in_discussion":
            raise ValueError("Cannot update topic while discussion is in progress")

        update_data = topic_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(topic, field, value)

        await self.db.commit()
        await self.db.refresh(topic)
        return topic

    async def delete_topic(self, topic_id: UUID, user_id: UUID) -> bool:
        """Delete topic"""
        topic = await self.get_topic_by_id(topic_id, user_id)
        if not topic:
            return False

        # Cannot delete topic if discussion is running
        if topic.status == "in_discussion":
            raise ValueError("Cannot delete topic while discussion is in progress")

        await self.db.delete(topic)
        await self.db.commit()
        return True

    async def search_topics(
        self,
        user_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Topic]:
        """Search topics by title or description"""
        search_pattern = f"%{query}%"

        result = await self.db.execute(
            select(Topic)
            .where(
                and_(
                    Topic.user_id == user_id,
                    or_(
                        Topic.title.ilike(search_pattern),
                        Topic.description.ilike(search_pattern)
                    )
                )
            )
            .order_by(desc(Topic.updated_at))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def set_topic_status(
        self,
        topic_id: UUID,
        user_id: UUID,
        status: str
    ) -> Optional[Topic]:
        """Set topic status"""
        topic = await self.get_topic_by_id(topic_id, user_id)
        if not topic:
            return None

        topic.status = status
        await self.db.commit()
        await self.db.refresh(topic)
        return topic
