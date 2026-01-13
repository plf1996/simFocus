"""
Topic model

Represents discussion topics created by users.
"""
from typing import Optional

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BaseModel


class Topic(BaseModel, Base):
    """
    Discussion topic model.

    Stores the subject matter for AI character discussions.
    Includes support for attachments and template-based creation.

    Attributes:
        user_id: Foreign key to users table
        title: Topic title (10-200 characters)
        description: Detailed description of the topic
        context: Background information for the discussion
        attachments: File metadata array stored as JSONB
        status: Topic status workflow
        template_id: Source template ID if created from one

    Relationships:
        user: Creator of the topic
        discussions: Discussion sessions based on this topic

    Status Values:
        draft: Topic is being prepared
        ready: Topic is ready for discussion
        in_discussion: Topic is currently being discussed
        completed: Discussion has finished
    """

    __tablename__ = "topics"

    # Foreign key to users with CASCADE delete
    user_id: Mapped[str] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Content fields
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    context: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Attachments stored as JSONB array
    # Format: [{"name": "file.pdf", "url": "...", "size": 1234, "type": "pdf"}]
    attachments: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True
    )

    # Status workflow
    status: Mapped[str] = mapped_column(
        String(20),
        default='draft',
        nullable=False,
        index=True
    )
    template_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey('topics.id', ondelete='SET NULL'),
        nullable=True
    )

    # Relationships
    user = relationship("User", back_populates="topics")
    discussions = relationship(
        "Discussion",
        back_populates="topic",
        cascade="all, delete-orphan"
    )

    # Indexes for common query patterns
    __table_args__ = (
        Index('idx_topics_user_status', 'user_id', 'status'),
        Index('idx_topics_status', 'status'),
    )

    def __repr__(self) -> str:
        """String representation of Topic."""
        return f"<Topic(id={self.id}, title='{self.title}', status='{self.status}')>"

    @property
    def is_active(self) -> bool:
        """Check if topic can be used for new discussions."""
        return self.status in ('ready', 'completed')

    @property
    def attachment_count(self) -> int:
        """Get number of attachments."""
        if self.attachments and isinstance(self.attachments, dict):
            files = self.attachments.get('files', [])
            return len(files) if files else 0
        return 0
