from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class Character(Base):
    __tablename__ = "characters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)  # NULL for system templates
    name = Column(String(100), nullable=False)
    avatar_url = Column(Text, nullable=True)
    is_template = Column(Boolean, default=False, nullable=False, index=True)  # True for system templates
    is_public = Column(Boolean, default=False, nullable=False)  # For P2 character marketplace
    config = Column(JSONB, nullable=False)  # Character configuration
    usage_count = Column(Integer, default=0, nullable=False)
    rating_avg = Column(Numeric(3, 2), default=0.0, nullable=False)
    rating_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="characters")


# Character config JSONB structure:
# {
#   "age": 35,
#   "gender": "female",
#   "profession": "Product Manager",
#   "personality": {
#     "openness": 8,
#     "rigor": 6,
#     "critical_thinking": 9,
#     "optimism": 5
#   },
#   "knowledge": {
#     "fields": ["product_management", "ux_design"],
#     "experience_years": 10,
#     "representative_views": ["user-centric", "data-driven"]
#   },
#   "stance": "critical_exploration",  # 'support', 'oppose', 'neutral', 'critical_exploration'
#   "expression_style": "formal",  # 'formal', 'casual', 'technical', 'storytelling'
#   "behavior_pattern": "balanced"  # 'active', 'passive', 'balanced'
# }
