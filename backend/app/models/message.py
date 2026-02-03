from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class DiscussionMessage(Base):
    __tablename__ = "discussion_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    discussion_id = Column(UUID(as_uuid=True), ForeignKey("discussions.id", ondelete="CASCADE"), nullable=False, index=True)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("discussion_participants.id", ondelete="CASCADE"), nullable=False)
    round = Column(Integer, nullable=False)
    phase = Column(String(20), nullable=False)  # 'opening', 'development', 'debate', 'closing'
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=True)
    is_injected_question = Column(Boolean, default=False, nullable=False)  # User-injected question
    parent_message_id = Column(UUID(as_uuid=True), ForeignKey("discussion_messages.id"), nullable=True)  # For threading
    meta_data = Column(JSONB, nullable=True)  # Additional data like sentiment, topics, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    tsv = Column(TSVECTOR, nullable=True)  # Full-text search

    # Relationships
    discussion = relationship("Discussion", back_populates="messages")
    participant = relationship("DiscussionParticipant", back_populates="messages")
    parent_message = relationship("DiscussionMessage", remote_side=[id], backref="replies")
