"""
Report and ShareLink models

Contains discussion reports and shareable links.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BaseModel


class Report(BaseModel, Base):
    """
    Discussion report with insights and analysis.

    Stores AI-generated reports with viewpoints, consensus, controversies,
    and actionable recommendations.

    Attributes:
        discussion_id: Foreign key to discussions (one-to-one)
        overview: Discussion overview (JSONB)
        viewpoints_summary: Character viewpoints (JSONB array)
        consensus: Agreed conclusions (JSONB)
        controversies: Disagreement points (JSONB array)
        insights: Key insights (JSONB array)
        recommendations: Actionable recommendations (JSONB array)
        full_transcript_citation: Reference to messages
        quality_scores: Quality metrics (JSONB)
        generation_time_ms: Generation time in milliseconds

    JSONB Structures:
        overview: {
            "topic": str,
            "duration": str,
            "participant_count": int,
            "rounds_completed": int,
            "summary": str
        }

        viewpoints_summary: [{
            "character_id": str,
            "character_name": str,
            "stance": str,
            "key_points": [str],
            "participation_level": str
        }]

        consensus: {
            "agreements": [str],
            "common_ground": str,
            "confidence_level": float
        }

        controversies: [{
            "topic": str,
            "sides": [str],
            "intensity": str,  # low/medium/high
            "resolved": bool
        }]

        insights: [{
            "category": str,
            "insight": str,
            "supporting_evidence": [str]
        }]

        recommendations: [{
            "action": str,
            "priority": str,  # low/medium/high
            "rationale": str
        }]

        quality_scores: {
            "depth": float,  # 0-100
            "diversity": float,  # 0-100
            "constructive": float,  # 0-100
            "coherence": float,  # 0-100
            "overall": float  # 0-100
        }

    Relationships:
        discussion: Associated discussion (one-to-one)
    """

    __tablename__ = "reports"

    # Foreign key (one-to-one with discussion)
    discussion_id: Mapped[str] = mapped_column(
        ForeignKey('discussions.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )

    # Report sections (JSONB for flexibility)
    overview: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False
    )
    viewpoints_summary: Mapped[list] = mapped_column(
        JSONB,
        nullable=False
    )
    consensus: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False
    )
    controversies: Mapped[list] = mapped_column(
        JSONB,
        nullable=False
    )
    insights: Mapped[list] = mapped_column(
        JSONB,
        nullable=False
    )
    recommendations: Mapped[list] = mapped_column(
        JSONB,
        nullable=False
    )

    # Citations and metadata
    full_transcript_citation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    quality_scores: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False
    )
    generation_time_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    # Relationship
    discussion = relationship("Discussion", back_populates="report")

    def __repr__(self) -> str:
        """String representation of Report."""
        return f"<Report(id={self.id}, discussion_id={self.discussion_id})>"

    @property
    def overall_quality(self) -> float:
        """Get overall quality score."""
        return self.quality_scores.get('overall', 0.0)

    @property
    def participant_count(self) -> int:
        """Get number of participants from overview."""
        return self.overview.get('participant_count', 0)

    @property
    def rounds_completed(self) -> int:
        """Get rounds completed from overview."""
        return self.overview.get('rounds_completed', 0)

    @property
    def has_controversies(self) -> bool:
        """Check if report contains unresolved controversies."""
        return any(
            not c.get('resolved', True)
            for c in self.controversies
        )

    @property
    def priority_recommendations(self) -> list:
        """Get high-priority recommendations."""
        return [
            r for r in self.recommendations
            if r.get('priority') == 'high'
        ]


class ShareLink(BaseModel, Base):
    """
    Shareable link for discussions.

    Enables users to share discussions with optional password protection.

    Attributes:
        discussion_id: Foreign key to discussions
        user_id: Link creator
        slug: Short URL slug (unique)
        password_hash: Optional bcrypt password hash
        expires_at: Expiration timestamp (NULL = no expiry)
        access_count: Number of times accessed

    Relationships:
        discussion: Associated discussion
        user: Creator of the share link
    """

    __tablename__ = "share_links"

    # Foreign keys
    discussion_id: Mapped[str] = mapped_column(
        ForeignKey('discussions.id', ondelete='CASCADE'),
        nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    # Link configuration
    slug: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Statistics
    access_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    # Relationships
    discussion = relationship("Discussion", back_populates="share_links")

    # Constraints
    __table_args__ = (
        Index('idx_share_links_slug', 'slug'),
        Index('idx_share_links_discussion', 'discussion_id'),
    )

    def __repr__(self) -> str:
        """String representation of ShareLink."""
        return f"<ShareLink(id={self.id}, slug='{self.slug}')>"

    @property
    def has_password(self) -> bool:
        """Check if link has password protection."""
        return self.password_hash is not None

    @property
    def is_expired(self) -> bool:
        """Check if link has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def access_count_display(self) -> str:
        """Get formatted access count for display."""
        if self.access_count == 0:
            return "Never accessed"
        elif self.access_count == 1:
            return "Accessed once"
        else:
            return f"Accessed {self.access_count} times"

    def increment_access(self) -> None:
        """Increment access count."""
        self.access_count += 1
