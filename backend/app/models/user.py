"""
User model

Represents user accounts with email/password authentication and OAuth support.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BaseModel


class User(BaseModel, Base):
    """
    User account model.

    Supports email/password authentication and OAuth providers (Google, GitHub).
    Includes soft delete functionality and profile management.

    Attributes:
        email: Unique email address used for login
        password_hash: Bcrypt hash (NULL for OAuth-only users)
        name: Display name for the user
        avatar_url: Profile picture URL
        bio: User biography/description
        email_verified: Email verification status
        auth_provider: Authentication provider ('email', 'google', 'github')
        provider_id: OAuth provider user ID (unique per provider)
        last_login_at: Timestamp of last login
        deleted_at: Soft delete timestamp (NULL if not deleted)

    Relationships:
        api_keys: User's LLM API keys
        topics: Discussion topics created by user
        characters: Custom characters created by user
        discussions: Discussion sessions created by user
    """

    __tablename__ = "users"

    # Email with unique constraint and index for fast lookups
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    # Password hash (nullable for OAuth-only users)
    password_hash: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    # Profile information
    name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Verification and auth
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    auth_provider: Mapped[str] = mapped_column(
        String(50),
        default='email',
        nullable=False
    )
    provider_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        unique=True
    )

    # Tracking
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )

    # Relationships
    api_keys = relationship(
        "UserApiKey",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    topics = relationship(
        "Topic",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    characters = relationship(
        "Character",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    discussions = relationship(
        "Discussion",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Indexes for common query patterns
    __table_args__ = (
        Index('idx_users_email_verified', 'email_verified'),
        Index('idx_users_auth_provider', 'auth_provider'),
        Index('idx_users_deleted_at', 'deleted_at'),
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"

    @property
    def is_active(self) -> bool:
        """Check if user account is active (not soft deleted)."""
        return self.deleted_at is None

    @property
    def is_oauth_user(self) -> bool:
        """Check if user registered via OAuth."""
        return self.auth_provider != 'email'
