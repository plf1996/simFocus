from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class Topic(Base):
    __tablename__ = "topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    context = Column(Text, nullable=True)  # Additional background information
    attachments = Column(JSONB, nullable=True)  # Array of file metadata
    status = Column(String(20), default="draft", nullable=False, index=True)  # 'draft', 'ready', 'in_discussion', 'completed'
    template_id = Column(UUID(as_uuid=True), nullable=True)  # If created from template
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="topics")
    discussion = relationship("Discussion", back_populates="topic", uselist=False, cascade="all, delete-orphan")
