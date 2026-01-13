"""
Character model

Represents AI character configurations for discussions.
"""
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BaseModel


class Character(BaseModel, Base):
    """
    AI character configuration model.

    Stores character personas, personalities, and discussion behaviors.
    Supports both user-created characters and system templates.

    Attributes:
        user_id: Owner's user ID (NULL for system templates)
        name: Character display name
        avatar_url: Character avatar/image URL
        is_template: System preset flag (templates have no user_id)
        is_public: Visibility flag for sharing
        config: Complete character configuration as JSONB
        usage_count: Times used in discussions
        rating_avg: Average user rating (1-5 scale)
        rating_count: Number of ratings received

    Config JSONB Structure:
        {
            "age": int,
            "gender": str,
            "profession": str,
            "personality": {
                "openness": int,  # 1-10
                "rigor": int,  # 1-10
                "critical_thinking": int,  # 1-10
                "optimism": int  # 1-10
            },
            "knowledge": {
                "fields": [str],
                "experience_years": int,
                "representative_views": [str]
            },
            "stance": str,  # support/oppose/neutral/critical_exploration
            "expression_style": str,  # formal/casual/technical/storytelling
            "behavior_pattern": str  # active/passive/balanced
        }

    Relationships:
        user: Creator of the character (NULL for templates)
        participants: Discussion instances using this character
    """

    __tablename__ = "characters"

    # Owner (NULL for system templates)
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=True,
        index=True
    )

    # Basic info
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Template flags
    is_template: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # Character configuration (JSONB)
    config: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False
    )

    # Statistics
    usage_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    rating_avg: Mapped[Optional[float]] = mapped_column(
        Numeric(3, 2),
        nullable=True
    )
    rating_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="characters")
    participants = relationship(
        "DiscussionParticipant",
        back_populates="character",
        cascade="all, delete-orphan"
    )

    # Indexes for common query patterns
    __table_args__ = (
        Index('idx_characters_user_template', 'user_id', 'is_template'),
        Index('idx_characters_is_template', 'is_template'),
    )

    def __repr__(self) -> str:
        """String representation of Character."""
        template_mark = " [Template]" if self.is_template else ""
        return f"<Character(id={self.id}, name='{self.name}'{template_mark})>"

    @property
    def is_system_template(self) -> bool:
        """Check if this is a system template."""
        return self.is_template and self.user_id is None

    @property
    def personality_traits(self) -> dict:
        """Get personality traits from config."""
        return self.config.get('personality', {})

    @property
    def knowledge_background(self) -> dict:
        """Get knowledge background from config."""
        return self.config.get('knowledge', {})

    @property
    def profession(self) -> str:
        """Get character profession."""
        return self.config.get('profession', '')

    @property
    def stance(self) -> str:
        """Get character discussion stance."""
        return self.config.get('stance', 'neutral')

    def increment_usage(self) -> None:
        """Increment usage count (called after discussion participation)."""
        self.usage_count += 1

    def update_rating(self, new_rating: int) -> None:
        """
        Update rating with new value.

        Args:
            new_rating: Rating value from 1 to 5
        """
        # Calculate new average
        total_score = (self.rating_avg or 0) * self.rating_count + new_rating
        self.rating_count += 1
        self.rating_avg = total_score / self.rating_count
