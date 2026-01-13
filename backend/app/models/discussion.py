"""
Discussion models

Contains Discussion, DiscussionParticipant, and DiscussionMessage models.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BaseModel


class Discussion(BaseModel, Base):
    """
    Discussion session model.

    Orchestrates AI character discussions with state management and token tracking.

    Attributes:
        topic_id: Foreign key to topics
        user_id: Discussion creator
        discussion_mode: Mode of discussion (free/structured/creative/consensus)
        max_rounds: Maximum discussion rounds
        status: Current discussion status
        current_round: Current round number (0-max_rounds)
        current_phase: Current discussion phase
        llm_provider: API provider used (openai/anthropic/custom)
        llm_model: Model identifier used
        total_tokens_used: Cumulative token consumption
        estimated_cost_usd: Estimated API cost
        started_at: Discussion start timestamp
        completed_at: Discussion completion timestamp

    Discussion Modes:
        free: Characters speak freely, balanced participation
        structured: Pro/con/neutral stances with ordered turns
        creative: "Yes, and" brainstorming mode
        consensus: Focused on finding common ground

    Status Values:
        initialized: Ready to start
        running: Discussion in progress
        paused: Temporarily paused
        completed: Finished successfully
        failed: Error during execution

    Relationships:
        topic: Associated topic
        user: Creator
        participants: Characters in discussion
        messages: All messages
        report: Generated report (one-to-one)
        share_links: Sharing links
    """

    __tablename__ = "discussions"

    # Foreign keys
    topic_id: Mapped[str] = mapped_column(
        ForeignKey('topics.id', ondelete='CASCADE'),
        nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Configuration
    discussion_mode: Mapped[str] = mapped_column(
        String(20),
        default='free',
        nullable=False
    )
    max_rounds: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False
    )

    # State
    status: Mapped[str] = mapped_column(
        String(20),
        default='initialized',
        nullable=False,
        index=True
    )
    current_round: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    current_phase: Mapped[str] = mapped_column(
        String(20),
        default='opening',
        nullable=False
    )

    # LLM usage tracking
    llm_provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    llm_model: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    total_tokens_used: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    estimated_cost_usd: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 4),
        nullable=True
    )

    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    topic = relationship("Topic", back_populates="discussions")
    user = relationship("User", back_populates="discussions")
    participants = relationship(
        "DiscussionParticipant",
        back_populates="discussion",
        cascade="all, delete-orphan"
    )
    messages = relationship(
        "DiscussionMessage",
        back_populates="discussion",
        cascade="all, delete-orphan"
    )
    report = relationship(
        "Report",
        back_populates="discussion",
        uselist=False,
        cascade="all, delete-orphan"
    )
    share_links = relationship(
        "ShareLink",
        back_populates="discussion",
        cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index('idx_discussions_user_status', 'user_id', 'status'),
        Index('idx_discussions_status', 'status'),
    )

    def __repr__(self) -> str:
        """String representation of Discussion."""
        return f"<Discussion(id={self.id}, status='{self.status}', round={self.current_round})>"

    @property
    def is_active(self) -> bool:
        """Check if discussion is currently running."""
        return self.status == 'running'

    @property
    def is_finished(self) -> bool:
        """Check if discussion has completed."""
        return self.status in ('completed', 'failed')

    @property
    def progress_percentage(self) -> float:
        """Calculate discussion progress."""
        if self.max_rounds == 0:
            return 0.0
        return min(100.0, (self.current_round / self.max_rounds) * 100)


class DiscussionParticipant(BaseModel, Base):
    """
    Discussion participant (character instance) model.

    Links characters to discussions with role-specific configuration.

    Attributes:
        discussion_id: Foreign key to discussions
        character_id: Foreign key to characters
        position: Speaking order for structured debates
        stance: Stance for structured mode (pro/con/neutral)
        message_count: Number of messages sent
        total_tokens: Tokens consumed by this participant

    Relationships:
        discussion: Parent discussion
        character: Associated character
        messages: Messages from this participant
    """

    __tablename__ = "discussion_participants"

    # Foreign keys
    discussion_id: Mapped[str] = mapped_column(
        ForeignKey('discussions.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    character_id: Mapped[str] = mapped_column(
        ForeignKey('characters.id', ondelete='CASCADE'),
        nullable=False
    )

    # Configuration for structured modes
    position: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    stance: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )

    # Statistics
    message_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    total_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    # Relationships
    discussion = relationship("Discussion", back_populates="participants")
    character = relationship("Character", back_populates="participants")
    messages = relationship("DiscussionMessage", back_populates="participant")

    def __repr__(self) -> str:
        """String representation of DiscussionParticipant."""
        return f"<DiscussionParticipant(id={self.id}, character_id={self.character_id})>"


class DiscussionMessage(BaseModel, Base):
    """
    Individual discussion message model.

    Stores each message with context, metadata, and full-text search support.

    Attributes:
        discussion_id: Foreign key to discussions
        participant_id: Foreign key to participants
        round: Discussion round number
        phase: Discussion phase when sent
        content: Message text content
        token_count: Approximate token count
        is_injected_question: User-injected question flag
        parent_message_id: Parent message for threading
        message_metadata: Additional data (sentiment, topics, etc.)
        tsv: Full-text search vector

    Phases:
        opening: Initial introductions and positions
        development: Exploring viewpoints
        debate: Direct disagreement and challenge
        closing: Summary and conclusion

    Relationships:
        discussion: Parent discussion
        participant: Sender participant
        parent_message: Threaded parent (self-reference)
        replies: Threaded responses

    Message Metadata Structure:
        {
            "sentiment": str,  # positive/neutral/negative
            "topics": [str],  # Extracted topics
            "perspective": str,  # Key perspective
            "agreement_level": float  # 0-1
        }
    """

    __tablename__ = "discussion_messages"

    # Foreign keys
    discussion_id: Mapped[str] = mapped_column(
        ForeignKey('discussions.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    participant_id: Mapped[str] = mapped_column(
        ForeignKey('discussion_participants.id', ondelete='CASCADE'),
        nullable=False
    )

    # Context
    round: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    phase: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    # Content
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    token_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    # Flags
    is_injected_question: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    parent_message_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey('discussion_messages.id', ondelete='SET NULL'),
        nullable=True
    )

    # Message metadata (sentiment, topics, etc.)
    # Note: Renamed from 'metadata' to avoid conflict with SQLAlchemy reserved attribute
    message_metadata: Mapped[Optional[dict]] = mapped_column(
        'metadata',  # Column name stays 'metadata' for DB compatibility
        JSONB,
        nullable=True
    )

    # Full-text search (PostgreSQL TSVECTOR)
    tsv: Mapped[Optional[str]] = mapped_column(
        TSVECTOR,
        nullable=True
    )

    # Relationships
    discussion = relationship("Discussion", back_populates="messages")
    participant = relationship("DiscussionParticipant", back_populates="messages")
    parent_message = relationship(
        "DiscussionMessage",
        remote_side="DiscussionMessage.id",
        backref="replies"
    )

    # Indexes
    __table_args__ = (
        Index('idx_messages_discussion_round', 'discussion_id', 'round'),
        Index('idx_messages_tsv', 'tsv', postgresql_using='gin'),
    )

    def __repr__(self) -> str:
        """String representation of DiscussionMessage."""
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<DiscussionMessage(id={self.id}, round={self.round}, content='{content_preview}')>"

    @property
    def sentiment(self) -> str:
        """Get message sentiment from metadata."""
        if self.message_metadata:
            return self.message_metadata.get('sentiment', 'neutral')
        return 'neutral'

    @property
    def topics(self) -> list:
        """Get extracted topics from metadata."""
        if self.message_metadata:
            return self.message_metadata.get('topics', [])
        return []
