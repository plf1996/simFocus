from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class DiscussionParticipant(Base):
    __tablename__ = "discussion_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    discussion_id = Column(UUID(as_uuid=True), ForeignKey("discussions.id", ondelete="CASCADE"), nullable=False, index=True)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    position = Column(Integer, nullable=False)  # Order for structured debates
    stance = Column(String(20), nullable=True)  # For structured mode: 'pro', 'con', 'neutral'
    message_count = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    discussion = relationship("Discussion", back_populates="participants")
    character = relationship("Character")
    messages = relationship("DiscussionMessage", back_populates="participant", cascade="all, delete-orphan")
