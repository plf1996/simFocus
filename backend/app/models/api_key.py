"""
User API Key model

Stores encrypted LLM API keys for users.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BaseModel


class UserApiKey(BaseModel, Base):
    """
    User's LLM API key with encryption.

    Stores API keys securely using AES-256-GCM encryption.
    Supports multiple providers (OpenAI, Anthropic, custom endpoints).

    Attributes:
        user_id: Foreign key to users
        provider: API provider name (openai/anthropic/custom)
        key_name: User-defined key name for identification
        encrypted_key: AES-256-GCM encrypted API key
        api_base_url: Custom API endpoint (for proxies/local models)
        default_model: Default model to use with this key
        is_active: Key activation status
        last_used_at: Timestamp of last usage

    Relationships:
        user: Owner of the API key

    Encryption:
        The encrypted_key field contains the base64-encoded result of:
        AES-256-GCM(nonce || ciphertext)

        Decryption requires the ENCRYPTION_KEY from settings.
    """

    __tablename__ = "user_api_keys"

    # Foreign key with CASCADE delete
    user_id: Mapped[str] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Provider information
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    key_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    # Encrypted credentials (AES-256-GCM)
    encrypted_key: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Optional custom endpoint configuration
    api_base_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    default_model: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    user = relationship("User", back_populates="api_keys")

    # Indexes
    __table_args__ = (
        Index('idx_api_keys_user_provider', 'user_id', 'provider'),
        Index('idx_api_keys_is_active', 'is_active'),
    )

    def __repr__(self) -> str:
        """String representation of UserApiKey."""
        return f"<UserApiKey(id={self.id}, provider='{self.provider}', name='{self.key_name}')>"

    @property
    def is_custom_endpoint(self) -> bool:
        """Check if this key uses a custom API endpoint."""
        return self.api_base_url is not None

    @property
    def display_name(self) -> str:
        """Get display name for UI."""
        return f"{self.provider.capitalize()}: {self.key_name}"

    def mark_used(self) -> None:
        """Update last_used_at timestamp."""
        self.last_used_at = datetime.utcnow()
