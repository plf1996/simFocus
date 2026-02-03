from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    discussion_id = Column(UUID(as_uuid=True), ForeignKey("discussions.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    overview = Column(JSONB, nullable=True)
    summary = Column(Text, nullable=True)  # LLM-generated comprehensive summary in Markdown
    viewpoints_summary = Column(JSONB, nullable=True)  # Array of character viewpoints
    consensus = Column(JSONB, nullable=True)
    controversies = Column(JSONB, nullable=True)  # Array of disagreement points
    insights = Column(JSONB, nullable=True)
    recommendations = Column(JSONB, nullable=True)
    transcript = Column(Text, nullable=True)  # Full discussion transcript in Markdown
    full_transcript_citation = Column(JSONB, nullable=True)  # Reference to messages (deprecated, kept for compatibility)
    quality_scores = Column(JSONB, nullable=True)  # depth, diversity, constructive, coherence
    generation_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    discussion = relationship("Discussion", back_populates="report")
