"""
Base database models with common fields and mixins

Provides reusable mixins for UUID primary keys and timestamps.
"""
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """
    Base class for all ORM models.

    All models should inherit from this class to be registered
    with the SQLAlchemy metadata.
    """
    pass


class UUIDMixin:
    """
    Mixin that adds UUID primary key to model.

    Attributes:
        id: Primary key using UUID (auto-generated)

    Example:
        >>> class User(UUIDMixin, Base):
        ...     __tablename__ = "users"
        ...     name: Mapped[str] = mapped_column(String)
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower() + "s"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        index=True,
    )


class TimestampMixin:
    """
    Mixin that adds timestamp fields to model.

    Attributes:
        created_at: Timestamp when record was created (auto-set)
        updated_at: Timestamp when record was last updated (auto-updated)

    Example:
        >>> class User(TimestampMixin, Base):
        ...     __tablename__ = "users"
        ...     name: Mapped[str] = mapped_column(String)
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class BaseModel(UUIDMixin, TimestampMixin):
    """
    Base model with UUID and timestamps.

    All models should inherit from this unless they need custom configuration.

    This is NOT an abstract class - models should inherit from both
    BaseModel and Base to be properly registered with SQLAlchemy.

    Attributes:
        id: UUID primary key
        created_at: Creation timestamp
        updated_at: Last update timestamp

    Example:
        >>> from app.db.base import Base, BaseModel
        >>> class User(BaseModel, Base):
        ...     name: Mapped[str] = mapped_column(String(100))
        ...     email: Mapped[str] = mapped_column(String(255), unique=True)
    """

    # __abstract__ = True  # DO NOT set abstract - models inherit from both BaseModel and Base

    def to_dict(self) -> dict[str, Any]:
        """
        Convert model instance to dictionary.

        Returns:
            Dictionary representation of the model
        """
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
        }

    def __repr__(self) -> str:
        """String representation of model."""
        class_name = self.__class__.__name__
        return f"<{class_name}(id={self.id})>"
