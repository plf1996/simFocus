from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import uuid
from app.core.database import Base


class Discussion(Base):
    __tablename__ = "discussions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    discussion_mode = Column(String(20), default="free", nullable=False)  # 'free', 'structured', 'creative', 'consensus'
    max_rounds = Column(Integer, default=10, nullable=False)
    status = Column(String(20), default="initialized", nullable=False, index=True)  # 'initialized', 'running', 'paused', 'completed', 'failed', 'cancelled'
    current_round = Column(Integer, default=0, nullable=False)
    current_phase = Column(String(20), default="opening", nullable=False)  # 'opening', 'development', 'debate', 'closing'
    llm_provider = Column(String(50), nullable=True)  # Which API was used
    llm_model = Column(String(100), nullable=True)  # Which model
    total_tokens_used = Column(Integer, default=0, nullable=False)
    estimated_cost_usd = Column(Numeric(10, 4), default=0.0, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    topic = relationship("Topic", back_populates="discussion")
    user = relationship("User", back_populates="discussions")
    participants = relationship("DiscussionParticipant", back_populates="discussion", cascade="all, delete-orphan")
    messages = relationship("DiscussionMessage", back_populates="discussion", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="discussion", uselist=False, cascade="all, delete-orphan")

    @hybrid_property
    def progress_percentage(self) -> float:
        """Calculate progress including phases (each round has 4 phases)"""
        phases = ["opening", "development", "debate", "closing"]

        # Safe index lookup
        try:
            current_phase_index = phases.index(self.current_phase) if self.current_phase in phases else 0
        except (ValueError, AttributeError):
            current_phase_index = 0

        total_phases = len(phases)
        phase_progress = current_phase_index / total_phases

        # Combined progress
        progress = ((self.current_round + phase_progress) / self.max_rounds * 100) if self.max_rounds > 0 else 0

        return min(progress, 100)  # Cap at 100%
