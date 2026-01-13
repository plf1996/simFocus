# Backend Design Document
# simFocus - AI Virtual Focus Group Platform

**Document Version**: 1.0
**Date**: 2026-01-12
**Author**: Backend Architect
**Status**: Design Phase

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Technology Stack & Dependencies](#2-technology-stack--dependencies)
3. [Database Models](#3-database-models)
4. [Pydantic Schemas](#4-pydantic-schemas)
5. [API Endpoints](#5-api-endpoints)
6. [Service Layer Design](#6-service-layer-design)
7. [Security Implementation](#7-security-implementation)
8. [Error Handling Strategy](#8-error-handling-strategy)
9. [WebSocket Protocol](#9-websocket-protocol)
10. [Caching Strategy](#10-caching-strategy)

---

## 1. Executive Summary

### 1.1 Backend Architecture Overview

The simFocus backend is built using **FastAPI** with a layered architecture:

- **API Layer**: FastAPI route handlers with automatic OpenAPI documentation
- **Service Layer**: Business logic orchestration (discussions, characters, reports)
- **Repository Layer**: Data access abstraction (SQLAlchemy 2.0 async)
- **External Services**: LLM provider integrations (OpenAI, Anthropic)
- **Infrastructure**: PostgreSQL, Redis, WebSocket (Socket.IO)

### 1.2 Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Async-First** | All I/O operations use async/await with SQLAlchemy 2.0 |
| **Type Safety** | Pydantic v2 for request/response validation |
| **Security** | JWT auth, AES-256-GCM encryption for API keys |
| **Scalability** | Redis caching, connection pooling, horizontal scaling ready |
| **Observability** | Structured logging, request IDs, error tracking |

---

## 2. Technology Stack & Dependencies

### 2.1 Core Dependencies

```txt
# Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy[asyncio]==2.0.25
asyncpg==0.29.0
alembic==1.13.0

# Cache & WebSocket
redis==5.0.1
aioredis==2.0.1
python-socketio==5.11.0
aiohttp==3.9.1

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic==2.5.3
pydantic-settings==2.1.0
cryptography==41.0.7

# LLM Providers
openai==1.10.0
anthropic==0.18.0

# Utilities
python-dotenv==1.0.0
httpx==0.26.0

# Testing
pytest==7.4.3
pytest-asyncio==0.23.3
pytest-cov==4.1.0
```

### 2.2 Project Structure (Backend)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Settings management
│   ├── dependencies.py            # FastAPI dependencies
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── topics.py
│   │   │   ├── characters.py
│   │   │   ├── discussions.py
│   │   │   ├── reports.py
│   │   │   └── websocket.py
│   │   └── deps.py
│   │
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── topic.py
│   │   ├── character.py
│   │   ├── discussion.py
│   │   ├── report.py
│   │   └── api_key.py
│   │
│   ├── schemas/                   # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── topic.py
│   │   ├── character.py
│   │   ├── discussion.py
│   │   ├── report.py
│   │   └── common.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── topic_service.py
│   │   ├── character_service.py
│   │   ├── discussion_service.py
│   │   ├── discussion_engine.py
│   │   ├── report_service.py
│   │   └── llm/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── openai.py
│   │       ├── anthropic.py
│   │       └── orchestrator.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py
│   │   ├── errors.py
│   │   └── constants.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py
│   │   └── base.py
│   │
│   ├── cache/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   └── decorators.py
│   │
│   ├── websocket/
│   │   ├── __init__.py
│   │   ├── manager.py
│   │   └── handlers.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── encryption.py
│   │   └── validators.py
│   │
│   └── prompts/
│       ├── __init__.py
│       ├── discussion_prompts.py
│       └── report_prompts.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── alembic/
│   └── versions/
│
├── .env.example
├── alembic.ini
├── pyproject.toml
└── requirements.txt
```

---

## 3. Database Models

### 3.1 Base Model

```python
# backend/app/models/base.py
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class UUIDMixin:
    """Mixin for UUID primary key."""

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False
    )
```

### 3.2 User Model

```python
# backend/app/models/user.py
from sqlalchemy import String, Boolean, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.models.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """
    User account model.

    Attributes:
        id: UUID primary key
        email: Unique email address
        password_hash: Bcrypt hash (NULL for OAuth-only users)
        name: Display name
        avatar_url: Profile picture URL
        bio: User biography
        email_verified: Email verification status
        auth_provider: Authentication provider ('email', 'google', 'github')
        provider_id: OAuth provider user ID
        last_login_at: Last login timestamp
        deleted_at: Soft delete timestamp
    """

    __tablename__ = "users"

    # Email with unique constraint and index
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
        nullable=True
    )

    # Relationships
    api_keys = relationship("UserAPIKey", back_populates="user", cascade="all, delete-orphan")
    topics = relationship("Topic", back_populates="user", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="user", cascade="all, delete-orphan")
    discussions = relationship("Discussion", back_populates="user", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_users_email_verified', 'email_verified'),
        Index('idx_users_auth_provider', 'auth_provider'),
        Index('idx_users_deleted_at', 'deleted_at'),
    )
```

### 3.3 User API Key Model

```python
# backend/app/models/api_key.py
from sqlalchemy import String, Boolean, Text, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.models.base import Base, UUIDMixin, TimestampMixin


class UserAPIKey(Base, UUIDMixin, TimestampMixin):
    """
    User's LLM API key with encryption.

    Attributes:
        id: UUID primary key
        user_id: Foreign key to users
        provider: API provider name ('openai', 'anthropic', 'custom')
        key_name: User-defined key name
        encrypted_key: AES-256-GCM encrypted API key
        api_base_url: Custom API endpoint (for proxies/local models)
        default_model: Default model to use
        is_active: Key activation status
        last_used_at: Last usage timestamp
    """

    __tablename__ = "user_api_keys"

    # Foreign key
    user_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True),
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

    # Encrypted credentials
    encrypted_key: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
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
        nullable=False
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationship
    user = relationship("User", back_populates="api_keys")

    # Indexes
    __table_args__ = (
        Index('idx_api_keys_user_provider', 'user_id', 'provider'),
        Index('idx_api_keys_is_active', 'is_active'),
    )
```

### 3.4 Topic Model

```python
# backend/app/models/topic.py
from sqlalchemy import String, Text, JSONB, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.models.base import Base, UUIDMixin, TimestampMixin


class Topic(Base, UUIDMixin, TimestampMixin):
    """
    Discussion topic.

    Attributes:
        id: UUID primary key
        user_id: Foreign key to users
        title: Topic title (10-200 chars)
        description: Detailed description (optional)
        context: Background information
        attachments: File metadata array (JSONB)
        status: Topic status ('draft', 'ready', 'in_discussion', 'completed')
        template_id: Source template if created from one
    """

    __tablename__ = "topics"

    # Foreign key
    user_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Content
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    context: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Attachments stored as JSONB
    attachments: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default='draft',
        nullable=False
    )
    template_id: Mapped[Optional[str]] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True
    )

    # Relationships
    user = relationship("User", back_populates="topics")
    discussions = relationship("Discussion", back_populates="topic", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_topics_user_status', 'user_id', 'status'),
        Index('idx_topics_status', 'status'),
    )
```

### 3.5 Character Model

```python
# backend/app/models/character.py
from sqlalchemy import String, Boolean, Text, JSONB, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.models.base import Base, UUIDMixin, TimestampMixin


class Character(Base, UUIDMixin, TimestampMixin):
    """
    AI character configuration.

    Attributes:
        id: UUID primary key
        user_id: Owner's user ID (NULL for system templates)
        name: Character display name
        avatar_url: Character avatar URL
        is_template: System preset flag
        is_public: Visibility flag (for P2 marketplace)
        config: Character configuration JSONB
        usage_count: Times used in discussions
        rating_avg: Average user rating
        rating_count: Number of ratings
    """

    __tablename__ = "characters"

    # Owner (NULL for system templates)
    user_id: Mapped[Optional[str]] = mapped_column(
        PGUUID(as_uuid=True),
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
    participants = relationship("DiscussionParticipant", back_populates="character", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_characters_user_template', 'user_id', 'is_template'),
        Index('idx_characters_is_template', 'is_template'),
    )
```

### 3.6 Discussion Model

```python
# backend/app/models/discussion.py
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.models.base import Base, UUIDMixin, TimestampMixin
from sqlalchemy.dialects.postgresql import UUID as PGUUID


class Discussion(Base, UUIDMixin, TimestampMixin):
    """
    Discussion session.

    Attributes:
        id: UUID primary key
        topic_id: Foreign key to topics
        user_id: Discussion creator
        discussion_mode: Discussion mode ('free', 'structured', 'creative', 'consensus')
        max_rounds: Maximum discussion rounds
        status: Current status
        current_round: Current round number
        current_phase: Discussion phase
        llm_provider: API provider used
        llm_model: Model used
        total_tokens_used: Total tokens consumed
        estimated_cost_usd: Estimated cost
        started_at: Start timestamp
        completed_at: Completion timestamp
    """

    __tablename__ = "discussions"

    # Foreign keys
    topic_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey('topics.id', ondelete='CASCADE'),
        nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Configuration
    discussion_mode: Mapped[str] = mapped_column(
        String(20),
        default='free',
        nullable=False
    )
    max_rounds: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False
    )

    # State
    status: Mapped[str] = mapped_column(
        String(20),
        default='initialized',
        nullable=False,
        index=True
    )
    current_round: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    current_phase: Mapped[str] = mapped_column(
        String(20),
        default='opening',
        nullable=False
    )

    # LLM usage
    llm_provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    llm_model: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    total_tokens_used: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    estimated_cost_usd: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 4),
        nullable=True
    )

    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    topic = relationship("Topic", back_populates="discussions")
    user = relationship("User", back_populates="discussions")
    participants = relationship("DiscussionParticipant", back_populates="discussion", cascade="all, delete-orphan")
    messages = relationship("DiscussionMessage", back_populates="discussion", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="discussion", uselist=False, cascade="all, delete-orphan")
    share_links = relationship("ShareLink", back_populates="discussion", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_discussions_user_status', 'user_id', 'status'),
        Index('idx_discussions_status', 'status'),
    )


class DiscussionParticipant(Base, UUIDMixin, TimestampMixin):
    """
    Discussion participant (character instance).

    Attributes:
        id: UUID primary key
        discussion_id: Foreign key to discussions
        character_id: Foreign key to characters
        position: Order for structured debates
        stance: Stance for structured mode ('pro', 'con', 'neutral')
        message_count: Number of messages sent
        total_tokens: Tokens consumed by this participant
    """

    __tablename__ = "discussion_participants"

    # Foreign keys
    discussion_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey('discussions.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    character_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey('characters.id', ondelete='CASCADE'),
        nullable=False
    )

    # Configuration
    position: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    stance: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )

    # Statistics
    message_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    total_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    # Relationships
    discussion = relationship("Discussion", back_populates="participants")
    character = relationship("Character", back_populates="participants")
    messages = relationship("DiscussionMessage", back_populates="participant")


class DiscussionMessage(Base, UUIDMixin, TimestampMixin):
    """
    Individual message in a discussion.

    Attributes:
        id: UUID primary key
        discussion_id: Foreign key to discussions
        participant_id: Foreign key to participants
        round: Discussion round number
        phase: Discussion phase
        content: Message text
        token_count: Token count
        is_injected_question: User-injected question flag
        parent_message_id: Parent message for threading
        metadata: Additional data (JSONB)
        tsv: Full-text search vector
    """

    __tablename__ = "discussion_messages"

    # Foreign keys
    discussion_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey('discussions.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    participant_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey('discussion_participants.id', ondelete='CASCADE'),
        nullable=False
    )

    # Context
    round: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    phase: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    # Content
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    token_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    # Flags
    is_injected_question: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    parent_message_id: Mapped[Optional[str]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey('discussion_messages.id', ondelete='SET NULL'),
        nullable=True
    )

    # Metadata (sentiment, topics, etc.)
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True
    )

    # Full-text search (PostgreSQL TSVECTOR)
    tsv: Mapped[Optional[str]] = mapped_column(
        TSVECTOR,
        nullable=True
    )

    # Relationships
    discussion = relationship("Discussion", back_populates="messages")
    participant = relationship("DiscussionParticipant", back_populates="messages")
    parent_message = relationship("DiscussionMessage", remote_side=[id], backref="replies")

    # Indexes
    __table_args__ = (
        Index('idx_messages_discussion_round', 'discussion_id', 'round'),
        Index('idx_messages_tsv', 'tsv', postgresql_using='gin'),
    )
```

### 3.7 Report Model

```python
# backend/app/models/report.py
from sqlalchemy import Text, JSONB, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.models.base import Base, UUIDMixin, TimestampMixin
from sqlalchemy.dialects.postgresql import UUID as PGUUID


class Report(Base, UUIDMixin, TimestampMixin):
    """
    Discussion report with insights and analysis.

    Attributes:
        id: UUID primary key
        discussion_id: Foreign key to discussions (unique)
        overview: Discussion overview (JSONB)
        viewpoints_summary: Character viewpoints (JSONB)
        consensus: Agreed conclusions (JSONB)
        controversies: Disagreement points (JSONB)
        insights: Key insights (JSONB)
        recommendations: Actionable recommendations (JSONB)
        full_transcript_citation: Reference to messages
        quality_scores: Quality metrics (JSONB)
        generation_time_ms: Generation time
    """

    __tablename__ = "reports"

    # Foreign key (one-to-one)
    discussion_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True),
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


class ShareLink(Base, UUIDMixin, TimestampMixin):
    """
    Shareable link for discussions.

    Attributes:
        id: UUID primary key
        discussion_id: Foreign key to discussions
        user_id: Link creator
        slug: Short URL slug
        password_hash: Optional password protection
        expires_at: Expiration timestamp
        access_count: Number of accesses
    """

    __tablename__ = "share_links"

    # Foreign keys
    discussion_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey('discussions.id', ondelete='CASCADE'),
        nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True),
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
```

---

## 4. Pydantic Schemas

### 4.1 Common Schemas

```python
# backend/app/schemas/common.py
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, List
from datetime import datetime

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(ge=1, default=1)
    size: int = Field(ge=1, le=100, default=20)


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(cls, items: List[T], total: int, page: int, size: int):
        """Create paginated response."""
        pages = (total + size - 1) // size
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: dict

    @classmethod
    def create(
        cls,
        code: str,
        message: str,
        details: Optional[dict] = None,
        request_id: Optional[str] = None
    ):
        """Create error response."""
        error_data = {
            "code": code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        if details:
            error_data["details"] = details
        if request_id:
            error_data["request_id"] = request_id
        return cls(error=error_data)


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str
```

### 4.2 Authentication Schemas

```python
# backend/app/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    name: Optional[str] = Field(None, max_length=100)


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Password reset request."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Password reset confirmation."""
    token: str
    new_password: str = Field(min_length=8, max_length=100)


class VerifyEmailRequest(BaseModel):
    """Email verification request."""
    token: str
```

### 4.3 User Schemas

```python
# backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    """User profile response."""
    id: str
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    email_verified: bool
    auth_provider: str
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    """User profile update request."""
    name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)


class UserStatsResponse(BaseModel):
    """User usage statistics."""
    total_discussions: int
    total_topics: int
    total_characters: int
    total_tokens_used: int
    estimated_cost_usd: float


class APIKeyCreateRequest(BaseModel):
    """API key creation request."""
    provider: str = Field(..., pattern='^(openai|anthropic|custom)$')
    key_name: str = Field(..., min_length=1, max_length=100)
    api_key: str = Field(..., min_length=10)
    api_base_url: Optional[str] = None
    default_model: Optional[str] = None


class APIKeyResponse(BaseModel):
    """API key response (without actual key)."""
    id: str
    provider: str
    key_name: str
    api_base_url: Optional[str] = None
    default_model: Optional[str] = None
    is_active: bool
    last_used_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
```

### 4.4 Topic Schemas

```python
# backend/app/schemas/topic.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TopicCreateRequest(BaseModel):
    """Topic creation request."""
    title: str = Field(..., min_length=10, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    context: Optional[str] = Field(None, max_length=5000)
    attachments: Optional[List[dict]] = Field(None, max_length=5)


class TopicUpdateRequest(BaseModel):
    """Topic update request."""
    title: Optional[str] = Field(None, min_length=10, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    context: Optional[str] = Field(None, max_length=5000)
    status: Optional[str] = Field(None, pattern='^(draft|ready|completed)$')


class TopicResponse(BaseModel):
    """Topic response."""
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    context: Optional[str] = None
    attachments: Optional[List[dict]] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TopicListResponse(BaseModel):
    """Topic list item."""
    id: str
    title: str
    status: str
    created_at: datetime
    discussion_count: int

    class Config:
        from_attributes = True
```

### 4.5 Character Schemas

```python
# backend/app/schemas/character.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PersonalityTraits(BaseModel):
    """Character personality traits."""
    openness: int = Field(..., ge=1, le=10)
    rigor: int = Field(..., ge=1, le=10)
    critical_thinking: int = Field(..., ge=1, le=10)
    optimism: int = Field(..., ge=1, le=10)


class KnowledgeBackground(BaseModel):
    """Character knowledge background."""
    fields: List[str] = Field(..., min_length=1)
    experience_years: int = Field(..., ge=0)
    representative_views: List[str]


class CharacterConfig(BaseModel):
    """Complete character configuration."""
    age: int = Field(..., ge=18, le=100)
    gender: str = Field(..., pattern='^(male|female|other|prefer_not_to_say)$')
    profession: str = Field(..., min_length=2, max_length=100)
    personality: PersonalityTraits
    knowledge: KnowledgeBackground
    stance: str = Field(..., pattern='^(support|oppose|neutral|critical_exploration)$')
    expression_style: str = Field(..., pattern='^(formal|casual|technical|storytelling)$')
    behavior_pattern: str = Field(..., pattern='^(active|passive|balanced)$')


class CharacterCreateRequest(BaseModel):
    """Character creation request."""
    name: str = Field(..., min_length=2, max_length=100)
    avatar_url: Optional[str] = None
    config: CharacterConfig
    is_public: bool = False


class CharacterUpdateRequest(BaseModel):
    """Character update request."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    avatar_url: Optional[str] = None
    config: Optional[CharacterConfig] = None
    is_public: Optional[bool] = None


class CharacterResponse(BaseModel):
    """Character response."""
    id: str
    user_id: Optional[str] = None
    name: str
    avatar_url: Optional[str] = None
    is_template: bool
    is_public: bool
    config: CharacterConfig
    usage_count: int
    rating_avg: Optional[float] = None
    rating_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class CharacterTemplateResponse(BaseModel):
    """Character template list item."""
    id: str
    name: str
    avatar_url: Optional[str] = None
    config: CharacterConfig
    usage_count: int
    rating_avg: Optional[float] = None

    class Config:
        from_attributes = True
```

### 4.6 Discussion Schemas

```python
# backend/app/schemas/discussion.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DiscussionCreateRequest(BaseModel):
    """Discussion creation request."""
    topic_id: str
    character_ids: List[str] = Field(..., min_length=3, max_length=7)
    discussion_mode: str = Field('free', pattern='^(free|structured|creative|consensus)$')
    max_rounds: int = Field(10, ge=5, le=20)


class DiscussionResponse(BaseModel):
    """Discussion response."""
    id: str
    topic_id: str
    user_id: str
    discussion_mode: str
    max_rounds: int
    status: str
    current_round: int
    current_phase: str
    llm_provider: str
    llm_model: str
    total_tokens_used: int
    estimated_cost_usd: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DiscussionListResponse(BaseModel):
    """Discussion list item."""
    id: str
    title: str  # From topic
    status: str
    discussion_mode: str
    participant_count: int
    created_at: datetime
    completed_at: Optional[datetime] = None


class ParticipantResponse(BaseModel):
    """Discussion participant response."""
    id: str
    character_id: str
    character_name: str
    position: Optional[int] = None
    stance: Optional[str] = None
    message_count: int


class MessageResponse(BaseModel):
    """Discussion message response."""
    id: str
    participant_id: str
    character_name: str
    character_avatar: Optional[str] = None
    round: int
    phase: str
    content: str
    token_count: int
    is_injected_question: bool
    created_at: datetime


class DiscussionDetailResponse(DiscussionResponse):
    """Discussion with full details."""
    topic: dict
    participants: List[ParticipantResponse]
    messages: List[MessageResponse]


class InjectQuestionRequest(BaseModel):
    """Inject question into discussion."""
    question: str = Field(..., min_length=10, max_length=500)
```

### 4.7 Report Schemas

```python
# backend/app/schemas/report.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ReportResponse(BaseModel):
    """Full report response."""
    id: str
    discussion_id: str
    overview: dict
    viewpoints_summary: List[dict]
    consensus: dict
    controversies: List[dict]
    insights: List[dict]
    recommendations: List[dict]
    quality_scores: dict
    generation_time_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReportSummaryResponse(BaseModel):
    """Report summary for list view."""
    id: str
    discussion_id: str
    discussion_title: str
    overview: dict
    quality_scores: dict
    created_at: datetime


class ShareLinkCreateRequest(BaseModel):
    """Share link creation request."""
    password: Optional[str] = None
    expires_in_days: Optional[int] = None


class ShareLinkResponse(BaseModel):
    """Share link response."""
    id: str
    slug: str
    discussion_title: str
    has_password: bool
    expires_at: Optional[datetime] = None
    access_count: int
    created_at: datetime
```

---

## 5. API Endpoints

### 5.1 Authentication Endpoints

```python
# backend/app/api/v1/auth.py
from fastapi import APIRouter, status
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse,
    ForgotPasswordRequest, ResetPasswordRequest, VerifyEmailRequest
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user"
)
async def register(data: RegisterRequest):
    """
    Register a new user account.

    - **email**: Valid email address
    - **password**: At least 8 characters
    - **name**: Optional display name

    Returns JWT tokens on successful registration.
    """
    pass


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login"
)
async def login(data: LoginRequest):
    """
    Authenticate user with email and password.

    Returns JWT access and refresh tokens.
    """
    pass


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token"
)
async def refresh_token(data: RefreshTokenRequest):
    """
    Obtain new access token using refresh token.
    """
    pass


@router.post(
    "/verify-email",
    response_model=MessageResponse,
    summary="Verify email address"
)
async def verify_email(data: VerifyEmailRequest):
    """
    Verify user email with verification token.
    """
    pass


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request password reset"
)
async def forgot_password(data: ForgotPasswordRequest):
    """
    Send password reset email.
    """
    pass


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password"
)
async def reset_password(data: ResetPasswordRequest):
    """
    Reset password with reset token.
    """
    pass
```

### 5.2 User Management Endpoints

```python
# backend/app/api/v1/users.py
from fastapi import APIRouter, Depends, status
from app.schemas.user import (
    UserResponse, UserUpdateRequest, UserStatsResponse,
    APIKeyCreateRequest, APIKeyResponse
)
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile"
)
async def get_current_user(
    current_user: User = Depends(get_current_user)
):
    """Get authenticated user's profile."""
    pass


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update user profile"
)
async def update_user_profile(
    data: UserUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update user profile information."""
    pass


@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="Delete user account"
)
async def delete_user_account(
    current_user: User = Depends(get_current_user)
):
    """Permanently delete user account and all data."""
    pass


@router.get(
    "/me/stats",
    response_model=UserStatsResponse,
    summary="Get user statistics"
)
async def get_user_stats(
    current_user: User = Depends(get_current_user)
):
    """Get user usage statistics."""
    pass


@router.get(
    "/me/api-keys",
    response_model=List[APIKeyResponse],
    summary="List user API keys"
)
async def list_api_keys(
    current_user: User = Depends(get_current_user)
):
    """Get all API keys for current user."""
    pass


@router.post(
    "/me/api-keys",
    response_model=APIKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add new API key"
)
async def create_api_key(
    data: APIKeyCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Add a new LLM API key.

    The key will be encrypted using AES-256-GCM.
    """
    pass


@router.delete(
    "/me/api-keys/{key_id}",
    response_model=MessageResponse,
    summary="Delete API key"
)
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete an API key."""
    pass


@router.patch(
    "/me/api-keys/{key_id}",
    response_model=APIKeyResponse,
    summary="Update API key"
)
async def update_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user)
):
    """Update API key (name, active status, etc.)."""
    pass
```

### 5.3 Topic Endpoints

```python
# backend/app/api/v1/topics.py
from fastapi import APIRouter, Depends, status
from app.schemas.topic import (
    TopicCreateRequest, TopicUpdateRequest, TopicResponse, TopicListResponse
)
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get(
    "",
    response_model=PaginatedResponse[TopicListResponse],
    summary="List user topics"
)
async def list_topics(
    pagination: PaginationParams = Depends(),
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get paginated list of user's topics.

    - **status**: Filter by status (draft, ready, in_discussion, completed)
    - **search**: Search in title and description
    """
    pass


@router.post(
    "",
    response_model=TopicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new topic"
)
async def create_topic(
    data: TopicCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new discussion topic."""
    pass


@router.get(
    "/{topic_id}",
    response_model=TopicResponse,
    summary="Get topic by ID"
)
async def get_topic(
    topic_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get topic details."""
    pass


@router.patch(
    "/{topic_id}",
    response_model=TopicResponse,
    summary="Update topic"
)
async def update_topic(
    topic_id: str,
    data: TopicUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Update topic details.

    Can only update topics with draft or ready status.
    """
    pass


@router.delete(
    "/{topic_id}",
    response_model=MessageResponse,
    summary="Delete topic"
)
async def delete_topic(
    topic_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete topic and associated discussions."""
    pass


@router.post(
    "/{topic_id}/duplicate",
    response_model=TopicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate topic"
)
async def duplicate_topic(
    topic_id: str,
    current_user: User = Depends(get_current_user)
):
    """Create a copy of existing topic."""
    pass
```

### 5.4 Character Endpoints

```python
# backend/app/api/v1/characters.py
from fastapi import APIRouter, Depends, status
from app.schemas.character import (
    CharacterCreateRequest, CharacterUpdateRequest,
    CharacterResponse, CharacterTemplateResponse
)

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get(
    "",
    response_model=List[CharacterResponse],
    summary="List user characters"
)
async def list_characters(
    current_user: User = Depends(get_current_user)
):
    """Get all characters created by user."""
    pass


@router.post(
    "",
    response_model=CharacterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create custom character"
)
async def create_character(
    data: CharacterCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new custom character."""
    pass


@router.get(
    "/templates",
    response_model=List[CharacterTemplateResponse],
    summary="List character templates"
)
async def list_character_templates(
    category: Optional[str] = None,
    limit: int = 50
):
    """
    Get system preset character templates.

    - **category**: Filter by category (product, academic, business, creative)
    """
    pass


@router.get(
    "/{character_id}",
    response_model=CharacterResponse,
    summary="Get character by ID"
)
async def get_character(
    character_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get character details."""
    pass


@router.patch(
    "/{character_id}",
    response_model=CharacterResponse,
    summary="Update character"
)
async def update_character(
    character_id: str,
    data: CharacterUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update character configuration."""
    pass


@router.delete(
    "/{character_id}",
    response_model=MessageResponse,
    summary="Delete character"
)
async def delete_character(
    character_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete character (only if not used in active discussions)."""
    pass


@router.post(
    "/{character_id}/rate",
    response_model=MessageResponse,
    summary="Rate character"
)
async def rate_character(
    character_id: str,
    rating: int = Field(..., ge=1, le=5),
    current_user: User = Depends(get_current_user)
):
    """Rate character quality (1-5 stars)."""
    pass
```

### 5.5 Discussion Endpoints

```python
# backend/app/api/v1/discussions.py
from fastapi import APIRouter, Depends, status
from app.schemas.discussion import (
    DiscussionCreateRequest, DiscussionResponse, DiscussionDetailResponse,
    DiscussionListResponse, MessageResponse, InjectQuestionRequest
)
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/discussions", tags=["discussions"])


@router.get(
    "",
    response_model=List[DiscussionListResponse],
    summary="List user discussions"
)
async def list_discussions(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get all discussions for current user."""
    pass


@router.post(
    "",
    response_model=DiscussionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new discussion"
)
async def create_discussion(
    data: DiscussionCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new discussion.

    Validates topic ownership and character availability.
    """
    pass


@router.get(
    "/{discussion_id}",
    response_model=DiscussionDetailResponse,
    summary="Get discussion details"
)
async def get_discussion(
    discussion_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get full discussion details with messages."""
    pass


@router.delete(
    "/{discussion_id}",
    response_model=MessageResponse,
    summary="Delete discussion"
)
async def delete_discussion(
    discussion_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete discussion (only if not running)."""
    pass


@router.post(
    "/{discussion_id}/start",
    response_model=DiscussionResponse,
    summary="Start discussion"
)
async def start_discussion(
    discussion_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Start the discussion engine.

    Validates API keys and begins character discussion.
    """
    pass


@router.post(
    "/{discussion_id}/pause",
    response_model=DiscussionResponse,
    summary="Pause discussion"
)
async def pause_discussion(
    discussion_id: str,
    current_user: User = Depends(get_current_user)
):
    """Pause running discussion."""
    pass


@router.post(
    "/{discussion_id}/resume",
    response_model=DiscussionResponse,
    summary="Resume discussion"
)
async def resume_discussion(
    discussion_id: str,
    current_user: User = Depends(get_current_user)
):
    """Resume paused discussion."""
    pass


@router.post(
    "/{discussion_id}/stop",
    response_model=DiscussionResponse,
    summary="Stop discussion"
)
async def stop_discussion(
    discussion_id: str,
    current_user: User = Depends(get_current_user)
):
    """Stop discussion and trigger report generation."""
    pass


@router.post(
    "/{discussion_id}/inject-question",
    response_model=MessageResponse,
    summary="Inject question into discussion"
)
async def inject_question(
    discussion_id: str,
    data: InjectQuestionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Inject a guiding question into active discussion.

    Question will be included in next discussion round.
    """
    pass


@router.get(
    "/{discussion_id}/messages",
    response_model=List[MessageResponse],
    summary="Get discussion messages"
)
async def get_discussion_messages(
    discussion_id: str,
    round: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get messages from discussion.

    - **round**: Filter by specific round (optional)
    """
    pass
```

### 5.6 Report Endpoints

```python
# backend/app/api/v1/reports.py
from fastapi import APIRouter, Depends, status, Response
from fastapi.responses import FileResponse
from app.schemas.report import (
    ReportResponse, ReportSummaryResponse,
    ShareLinkCreateRequest, ShareLinkResponse
)
from typing import Literal

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get(
    "/discussions/{discussion_id}",
    response_model=ReportResponse,
    summary="Get discussion report"
)
async def get_discussion_report(
    discussion_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get generated report for discussion."""
    pass


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    summary="Get report by ID"
)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get report by ID."""
    pass


@router.get(
    "/{report_id}/export/{format}",
    summary="Export report"
)
async def export_report(
    report_id: str,
    format: Literal['pdf', 'markdown', 'json'],
    current_user: User = Depends(get_current_user)
):
    """
    Export report in specified format.

    Returns file download.
    """
    pass


@router.post(
    "/discussions/{discussion_id}/share",
    response_model=ShareLinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create share link"
)
async def create_share_link(
    discussion_id: str,
    data: ShareLinkCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create shareable link for discussion."""
    pass


@router.get(
    "/share/{slug}",
    summary="Access shared discussion"
)
async def access_shared_discussion(
    slug: str,
    password: Optional[str] = None
):
    """Access discussion via share link (no auth required)."""
    pass
```

---

## 6. Service Layer Design

### 6.1 Service Interface Pattern

```python
# backend/app/services/base.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

ModelType = TypeVar("ModelType")


class BaseService(ABC, Generic[ModelType]):
    """Base service with common CRUD operations."""

    @abstractmethod
    async def get(self, id: str) -> Optional[ModelType]:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[ModelType]:
        """List entities with pagination."""
        pass

    @abstractmethod
    async def create(self, **kwargs) -> ModelType:
        """Create new entity."""
        pass

    @abstractmethod
    async def update(self, id: str, **kwargs) -> Optional[ModelType]:
        """Update entity."""
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete entity."""
        pass
```

### 6.2 Authentication Service

```python
# backend/app/services/auth_service.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.security import create_access_token, create_refresh_token
from app.core.errors import NotFoundError, ValidationError
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    """Authentication and authorization service."""

    def __init__(
        self,
        user_repo: UserRepository,
        settings: Settings
    ):
        self.user_repo = user_repo
        self.settings = settings
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def register(
        self,
        email: str,
        password: str,
        name: Optional[str] = None
    ) -> dict:
        """
        Register new user.

        Returns:
            dict with access_token, refresh_token, token_type, expires_in

        Raises:
            ValidationError: If email already exists
        """
        # Check if email exists
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ValidationError("EMAIL_ALREADY_EXISTS", "Email already registered")

        # Hash password
        password_hash = self.pwd_context.hash(password)

        # Create user
        user = await self.user_repo.create(
            email=email,
            password_hash=password_hash,
            name=name,
            auth_provider='email'
        )

        # Generate tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    async def login(
        self,
        email: str,
        password: str
    ) -> dict:
        """
        Authenticate user.

        Returns:
            dict with tokens

        Raises:
            NotFoundError: If user not found
            ValidationError: If password incorrect
        """
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise NotFoundError("USER_NOT_FOUND", "Invalid credentials")

        if not user.password_hash:
            raise ValidationError("OAUTH_ONLY", "Use OAuth login")

        if not self.pwd_context.verify(password, user.password_hash):
            raise ValidationError("INVALID_PASSWORD", "Invalid credentials")

        # Update last login
        await self.user_repo.update(user.id, last_login_at=datetime.utcnow())

        # Generate tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    async def verify_token(self, token: str) -> str:
        """
        Verify JWT token and return user ID.

        Raises:
            ValidationError: If token invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.settings.JWT_SECRET_KEY,
                algorithms=[self.settings.JWT_ALGORITHM]
            )
            user_id = payload.get("sub")
            if not user_id:
                raise ValidationError("INVALID_TOKEN", "Invalid token")
            return user_id
        except JWTError:
            raise ValidationError("INVALID_TOKEN", "Invalid token")
```

### 6.3 Discussion Engine Service

```python
# backend/app/services/discussion_engine.py
from typing import Optional, List, Dict, AsyncGenerator
from datetime import datetime

from app.models.discussion import (
    Discussion, DiscussionParticipant, DiscussionMessage
)
from app.core.errors import ValidationError
from app.services.llm.orchestrator import LLMOrchestrator
from app.cache.client import RedisClient
from app.prompts.discussion_prompts import DiscussionPrompts


class DiscussionEngine:
    """
    Core discussion orchestration engine.

    Manages state machine, coordinates LLM calls, handles streaming.
    """

    PHASES = ['opening', 'development', 'debate', 'closing']
    PHASE_ROUNDS = {
        'opening': (1, 2),
        'development': (3, 8),
        'debate': (9, 13),
        'closing': (14, 15)
    }

    def __init__(
        self,
        llm_orchestrator: LLMOrchestrator,
        redis: RedisClient,
        prompts: DiscussionPrompts
    ):
        self.llm = llm_orchestrator
        self.redis = redis
        self.prompts = prompts

    async def start_discussion(
        self,
        discussion: Discussion,
        participants: List[DiscussionParticipant]
    ) -> AsyncGenerator[Dict, None]:
        """
        Start discussion and stream messages.

        Yields:
            dict with message_type and data for WebSocket broadcast

        Example yield:
            {
                "type": "message",
                "data": {
                    "message_id": "uuid",
                    "character_id": "uuid",
                    "content": "text",
                    "round": 1,
                    "phase": "opening"
                }
            }
        """
        # Validate API keys
        await self._validate_api_keys(discussion.user_id)

        # Update discussion status
        discussion.status = 'running'
        discussion.started_at = datetime.utcnow()

        # Cache state for recovery
        await self._cache_state(discussion, participants)

        # Start message loop
        async for message_data in self._discussion_loop(discussion, participants):
            # Update state
            await self._update_state(discussion, message_data)

            # Yield for WebSocket broadcast
            yield message_data

    async def _discussion_loop(
        self,
        discussion: Discussion,
        participants: List[DiscussionParticipant]
    ) -> AsyncGenerator[Dict, None]:
        """Main discussion loop."""

        current_round = 0
        current_phase = 'opening'
        injected_questions = []

        while current_round < discussion.max_rounds:
            current_round += 1

            # Determine phase
            current_phase = self._get_phase_for_round(current_round)

            # Check for pause
            if await self._is_paused(discussion.id):
                await self._wait_for_resume(discussion.id)

            # Check for injected questions
            question = await self._get_injected_question(discussion.id)
            if question:
                injected_questions.append(question)

            # Generate messages for this round
            for participant in participants:
                # Skip if character already spoke this round
                if await self._has_spoken_this_round(
                    discussion.id, participant.id, current_round
                ):
                    continue

                # Emit "thinking" event
                yield {
                    "type": "character_thinking",
                    "data": {
                        "character_id": participant.character_id,
                        "character_name": participant.character.name
                    }
                }

                # Get conversation history
                history = await self._get_history(
                    discussion.id, participant.id, current_round
                )

                # Generate prompt
                prompt = self.prompts.generate_discussion_prompt(
                    topic=discussion.topic.title,
                    character_config=participant.character.config,
                    phase=current_phase,
                    history=history,
                    injected_questions=injected_questions,
                    discussion_mode=discussion.discussion_mode
                )

                # Call LLM
                try:
                    response = await self.llm.generate_completion(
                        user_id=discussion.user_id,
                        messages=prompt,
                        stream=True
                    )

                    # Stream response
                    content = ""
                    message_id = None

                    async for chunk in response:
                        if not message_id:
                            message_id = str(uuid4())

                        content += chunk
                        yield {
                            "type": "message",
                            "data": {
                                "message_id": message_id,
                                "character_id": participant.character_id,
                                "character_name": participant.character.name,
                                "content": content,
                                "round": current_round,
                                "phase": current_phase,
                                "is_streaming": True
                            }
                        }

                    # Message complete
                    yield {
                        "type": "message_complete",
                        "data": {"message_id": message_id}
                    }

                    # Save to database
                    await self._save_message(
                        discussion_id=discussion.id,
                        participant_id=participant.id,
                        round=current_round,
                        phase=current_phase,
                        content=content
                    )

                except Exception as e:
                    yield {
                        "type": "error",
                        "data": {
                            "code": "LLM_API_ERROR",
                            "message": str(e),
                            "retryable": True
                        }
                    }

            # Update discussion state
            discussion.current_round = current_round
            discussion.current_phase = current_phase

            # Emit status update
            yield {
                "type": "status",
                "data": {
                    "status": "running",
                    "current_round": current_round,
                    "total_rounds": discussion.max_rounds,
                    "current_phase": current_phase,
                    "progress_percentage": int((current_round / discussion.max_rounds) * 100)
                }
            }

        # Discussion complete
        discussion.status = 'completed'
        discussion.completed_at = datetime.utcnow()

        yield {
            "type": "status",
            "data": {"status": "completed"}
        }

    def _get_phase_for_round(self, round: int) -> str:
        """Determine discussion phase for round."""
        for phase, (start, end) in self.PHASE_ROUNDS.items():
            if start <= round <= end:
                return phase
        return 'closing'

    async def _validate_api_keys(self, user_id: str):
        """Validate user has active API keys."""
        keys = await self.api_key_repo.get_active_keys(user_id)
        if not keys:
            raise ValidationError("NO_API_KEY", "No active API key configured")

    async def _cache_state(
        self,
        discussion: Discussion,
        participants: List[DiscussionParticipant]
    ):
        """Cache discussion state for recovery."""
        state = {
            "discussion_id": str(discussion.id),
            "current_round": discussion.current_round,
            "current_phase": discussion.current_phase,
            "participant_ids": [str(p.id) for p in participants]
        }
        await self.redis.setex(
            f"discussion_state:{discussion.id}",
            3600,  # 1 hour TTL
            state
        )
```

### 6.4 Report Service

```python
# backend/app/services/report_service.py
from typing import Dict, List
import time

from app.models.discussion import Discussion, DiscussionMessage
from app.models.report import Report
from app.services.llm.orchestrator import LLMOrchestrator
from app.prompts.report_prompts import ReportPrompts


class ReportService:
    """Discussion report generation service."""

    def __init__(
        self,
        llm_orchestrator: LLMOrchestrator,
        prompts: ReportPrompts
    ):
        self.llm = llm_orchestrator
        self.prompts = prompts

    async def generate_report(
        self,
        discussion: Discussion,
        messages: List[DiscussionMessage]
    ) -> Report:
        """
        Generate comprehensive discussion report.

        Performance target: < 10 seconds
        """
        start_time = time.time()

        # Prepare transcript
        transcript = self._prepare_transcript(messages)

        # Generate overview
        overview = await self._generate_overview(discussion, transcript)

        # Generate viewpoints summary
        viewpoints = await self._generate_viewpoints(discussion, messages)

        # Generate consensus
        consensus = await self._generate_consensus(transcript)

        # Generate controversies
        controversies = await self._generate_controversies(transcript)

        # Generate insights
        insights = await self._generate_insights(transcript)

        # Generate recommendations
        recommendations = await self._generate_recommendations(transcript)

        # Calculate quality scores
        quality_scores = self._calculate_quality_scores(messages)

        generation_time_ms = int((time.time() - start_time) * 1000)

        # Create report
        report = Report(
            discussion_id=discussion.id,
            overview=overview,
            viewpoints_summary=viewpoints,
            consensus=consensus,
            controversies=controversies,
            insights=insights,
            recommendations=recommendations,
            quality_scores=quality_scores,
            generation_time_ms=generation_time_ms
        )

        return report

    async def _generate_overview(
        self,
        discussion: Discussion,
        transcript: str
    ) -> Dict:
        """Generate discussion overview."""
        prompt = self.prompts.overview_prompt(
            topic=discussion.topic.title,
            participant_count=len(discussion.participants),
            duration=str(discussion.completed_at - discussion.started_at),
            transcript=transcript
        )

        response = await self.llm.generate_json(
            user_id=discussion.user_id,
            messages=prompt
        )
        return response

    def _calculate_quality_scores(self, messages: List[DiscussionMessage]) -> Dict:
        """Calculate discussion quality metrics."""
        total_messages = len(messages)
        total_tokens = sum(m.token_count for m in messages)

        # Depth: average message length
        avg_length = total_tokens / total_messages if total_messages > 0 else 0
        depth_score = min(100, (avg_length / 200) * 100)

        # Diversity: unique participants
        participant_diversity = len(set(m.participant_id for m in messages))
        diversity_score = (participant_diversity / 7) * 100  # Max 7 participants

        # Coherence: round progression
        rounds = len(set(m.round for m in messages))
        coherence_score = (rounds / 20) * 100  # Max 20 rounds

        # Constructive: presence of consensus
        constructive_score = 70  # Base score, enhanced by LLM analysis

        return {
            "depth": round(depth_score, 2),
            "diversity": round(diversity_score, 2),
            "constructive": round(constructive_score, 2),
            "coherence": round(coherence_score, 2),
            "overall": round((depth_score + diversity_score + constructive_score + coherence_score) / 4, 2)
        }
```

---

## 7. Security Implementation

### 7.1 JWT Authentication

```python
# backend/app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext

from app.config import get_settings


settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(user_id: str) -> str:
    """Create JWT access token."""
    expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token (longer expiry)."""
    expires_delta = timedelta(days=30)
    expire = datetime.utcnow() + expires_delta

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """Verify JWT and return user ID."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        return user_id
    except jwt.JWTError:
        return None


def hash_password(password: str) -> str:
    """Hash password with bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

### 7.2 API Key Encryption

```python
# backend/app/utils/encryption.py
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import os

from app.config import get_settings


settings = get_settings()


class APIKeyEncryption:
    """AES-256-GCM encryption for API keys."""

    def __init__(self):
        # Master key from environment (32 bytes)
        key = settings.ENCRYPTION_KEY
        if len(key) != 32:
            raise ValueError("Encryption key must be 32 bytes")
        self.cipher = AESGCM(key.encode() if isinstance(key, str) else key)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt API key.

        Returns base64-encoded (nonce + ciphertext).
        """
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        ciphertext = self.cipher.encrypt(nonce, plaintext.encode(), None)
        return base64.b64encode(nonce + ciphertext).decode()

    def decrypt(self, encrypted: str) -> str:
        """Decrypt encrypted API key."""
        data = base64.b64decode(encrypted)
        nonce, ciphertext = data[:12], data[12:]
        decrypted = self.cipher.decrypt(nonce, ciphertext, None)
        return decrypted.decode()


# Singleton instance
encryption = APIKeyEncryption()
```

### 7.3 Rate Limiting

```python
# backend/app/core/rate_limit.py
from fastapi import Request, HTTPException
from redis import Redis
from typing import Optional

from app.cache.client import get_redis


class RateLimiter:
    """Token bucket rate limiter using Redis."""

    def __init__(self, redis: Redis):
        self.redis = redis

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int
    ) -> bool:
        """
        Check if request is within rate limit.

        Args:
            key: Rate limit key (e.g., "user:123:discussions")
            limit: Max requests per window
            window: Time window in seconds

        Returns:
            True if within limit, False otherwise
        """
        current = await self.redis.incr(key)

        if current == 1:
            # Set expiry on first request
            await self.redis.expire(key, window)

        return current <= limit

    async def get_rate_limit_headers(
        self,
        key: str,
        limit: int,
        window: int
    ) -> dict:
        """Get rate limit headers for response."""
        current = await self.redis.get(key)
        remaining = max(0, limit - int(current)) if current else limit

        ttl = await self.redis.ttl(key)
        reset = ttl if ttl > 0 else window

        return {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset)
        }


# Rate limit configurations
RATE_LIMITS = {
    "auth_endpoints": {"limit": 5, "window": 60},  # 5 requests per minute
    "api_mutation": {"limit": 60, "window": 60},   # 60 requests per minute
    "discussion_create": {"limit": 10, "window": 3600},  # 10 per hour
    "character_create": {"limit": 100, "window": 3600},  # 100 per hour
}


async def check_discussion_rate_limit(user_id: str) -> bool:
    """Check discussion creation rate limit."""
    redis = get_redis()
    limiter = RateLimiter(redis)

    key = f"ratelimit:discussion_create:{user_id}"
    config = RATE_LIMITS["discussion_create"]

    return await limiter.check_rate_limit(
        key=key,
        limit=config["limit"],
        window=config["window"]
    )
```

---

## 8. Error Handling Strategy

### 8.1 Custom Exceptions

```python
# backend/app/core/errors.py
from typing import Optional, Any
from fastapi import HTTPException, status


class BaseAPIError(HTTPException):
    """Base exception for API errors."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[dict] = None
    ):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(
            status_code=status_code,
            detail={
                "code": code,
                "message": message,
                "details": details
            }
        )


class NotFoundError(BaseAPIError):
    """Resource not found."""

    def __init__(
        self,
        code: str = "RESOURCE_NOT_FOUND",
        message: str = "Resource not found",
        details: Optional[dict] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class ValidationError(BaseAPIError):
    """Validation error."""

    def __init__(
        self,
        code: str = "VALIDATION_ERROR",
        message: str = "Invalid input",
        details: Optional[dict] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class AuthenticationError(BaseAPIError):
    """Authentication failed."""

    def __init__(
        self,
        code: str = "AUTH_FAILED",
        message: str = "Authentication failed",
        details: Optional[dict] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class AuthorizationError(BaseAPIError):
    """Authorization failed."""

    def __init__(
        self,
        code: str = "ACCESS_DENIED",
        message: str = "Access denied",
        details: Optional[dict] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class RateLimitError(BaseAPIError):
    """Rate limit exceeded."""

    def __init__(
        self,
        code: str = "RATE_LIMIT_EXCEEDED",
        message: str = "Too many requests",
        details: Optional[dict] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


class ExternalServiceError(BaseAPIError):
    """External service (LLM API) error."""

    def __init__(
        self,
        code: str = "EXTERNAL_SERVICE_ERROR",
        message: str = "External service error",
        details: Optional[dict] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details
        )
```

### 8.2 Global Exception Handler

```python
# backend/app/api/deps.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.errors import BaseAPIError
import logging

logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions."""

    # Log error
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={"path": request.url.path, "method": request.method}
    )

    # Return generic error
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "SERVER_ERROR",
                "message": "Internal server error",
                "request_id": getattr(request.state, "request_id", None)
            }
        }
    )


async def api_error_handler(request: Request, exc: BaseAPIError):
    """Handle custom API errors."""

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "request_id": getattr(request.state, "request_id", None),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )
```

---

## 9. WebSocket Protocol

### 9.1 Connection Manager

```python
# backend/app/websocket/manager.py
from typing import Dict, Set
from fastapi import WebSocket
import uuid


class ConnectionManager:
    """Manage WebSocket connections for real-time discussion updates."""

    def __init__(self):
        # Map: discussion_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Map: websocket -> user_id
        self.connection_users: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, discussion_id: str, user_id: str):
        """Connect client to discussion."""
        await websocket.accept()

        if discussion_id not in self.active_connections:
            self.active_connections[discussion_id] = set()

        self.active_connections[discussion_id].add(websocket)
        self.connection_users[websocket] = user_id

    def disconnect(self, websocket: WebSocket):
        """Disconnect client."""
        discussion_id = self._get_discussion_id(websocket)
        if discussion_id and discussion_id in self.active_connections:
            self.active_connections[discussion_id].discard(websocket)
            if not self.active_connections[discussion_id]:
                del self.active_connections[discussion_id]

        if websocket in self.connection_users:
            del self.connection_users[websocket]

    async def broadcast_to_discussion(
        self,
        discussion_id: str,
        message: dict
    ):
        """Broadcast message to all connections in discussion."""
        if discussion_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[discussion_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)

            # Cleanup disconnected
            for conn in disconnected:
                self.disconnect(conn)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific client."""
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)

    def _get_discussion_id(self, websocket: WebSocket) -> str:
        """Get discussion ID for connection."""
        for discussion_id, connections in self.active_connections.items():
            if websocket in connections:
                return discussion_id
        return None


# Singleton instance
manager = ConnectionManager()
```

### 9.2 WebSocket Endpoint

```python
# backend/app/api/v1/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from app.websocket.manager import manager
from app.api.deps import get_current_user_ws

router = APIRouter()


@router.websocket("/ws/discussions/{discussion_id}")
async def discussion_websocket(
    websocket: WebSocket,
    discussion_id: str,
    token: str = Query(...),
    current_user: User = Depends(get_current_user_ws)
):
    """
    WebSocket endpoint for real-time discussion updates.

    Query parameters:
        token: JWT access token

    Message types (client -> server):
        - {"action": "subscribe", "data": {"discussion_id": "uuid"}}
        - {"action": "control", "data": {"control_type": "pause"}}
        - {"action": "ping"}

    Message types (server -> client):
        - {"type": "message", "data": {...}}
        - {"type": "status", "data": {...}}
        - {"type": "error", "data": {...}}
    """
    # Verify discussion access
    discussion = await discussion_service.get_discussion(discussion_id, current_user.id)
    if not discussion:
        await websocket.close(code=1008, reason="Discussion not found")
        return

    # Connect
    await manager.connect(websocket, discussion_id, current_user.id)

    # Send confirmation
    await manager.send_personal_message(
        {
            "type": "connected",
            "data": {
                "discussion_id": discussion_id,
                "status": discussion.status
            }
        },
        websocket
    )

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "subscribe":
                # Already subscribed via URL
                pass

            elif action == "control":
                # Handle control commands (pause, resume, etc.)
                control_type = data["data"].get("control_type")
                await handle_control_command(discussion_id, control_type, current_user.id)

            elif action == "ping":
                # Respond with pong
                await manager.send_personal_message(
                    {"type": "pong"},
                    websocket
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
```

---

## 10. Caching Strategy

### 10.1 Redis Client

```python
# backend/app/cache/client.py
from redis import asyncio as aioredis
from typing import Optional
from app.config import get_settings


class RedisClient:
    """Async Redis client wrapper."""

    def __init__(self):
        self.client: Optional[aioredis.Redis] = None

    async def connect(self):
        """Initialize Redis connection."""
        settings = get_settings()
        self.client = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

    async def disconnect(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        if not self.client:
            return None
        return await self.client.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None):
        """Set value with optional expiry."""
        if not self.client:
            return
        await self.client.set(key, value, ex=ex)

    async def setex(self, key: str, time: int, value: str):
        """Set value with expiry."""
        if not self.client:
            return
        await self.client.setex(key, time, value)

    async def delete(self, *keys: str):
        """Delete keys."""
        if not self.client:
            return
        await self.client.delete(*keys)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self.client:
            return False
        return await self.client.exists(key) > 0

    async def incr(self, key: str) -> int:
        """Increment value."""
        if not self.client:
            return 0
        return await self.client.incr(key)

    async def expire(self, key: str, time: int):
        """Set expiry on key."""
        if not self.client:
            return
        await self.client.expire(key, time)

    async def ttl(self, key: str) -> int:
        """Get time to live."""
        if not self.client:
            return -1
        return await self.client.ttl(key)


# Singleton
_redis_client: Optional[RedisClient] = None


async def get_redis() -> RedisClient:
    """Get Redis client singleton."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
        await _redis_client.connect()
    return _redis_client
```

### 10.2 Cache Decorators

```python
# backend/app/cache/decorators.py
from functools import wraps
from typing import Optional, Callable
import json
import hashlib

from app.cache.client import get_redis


def cache_result(
    ttl: int = 3600,
    key_prefix: str = "",
    key_builder: Optional[Callable] = None
):
    """
    Cache function result in Redis.

    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
        key_builder: Custom function to build cache key
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            redis = await get_redis()

            # Build cache key
            if key_builder:
                key = key_builder(*args, **kwargs)
            else:
                # Default: hash function args
                key_data = f"{key_prefix}:{func.__name__}:{args}:{kwargs}"
                key = hashlib.md5(key_data.encode()).hexdigest()

            # Try cache
            cached = await redis.get(key)
            if cached:
                return json.loads(cached)

            # Call function
            result = await func(*args, **kwargs)

            # Cache result
            await redis.setex(key, ttl, json.dumps(result))

            return result
        return wrapper
    return decorator


def invalidate_cache(
    key_pattern: str,
    key_builder: Optional[Callable] = None
):
    """
    Invalidate cache keys matching pattern.

    Note: This requires Redis SCAN in production.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            redis = await get_redis()

            if key_builder:
                key = key_builder(*args, **kwargs)
                await redis.delete(key)
            else:
                # Delete by pattern (simplified)
                await redis.delete(key_pattern)

            return result
        return wrapper
    return decorator
```

---

## Summary

This backend design document provides:

1. **Complete Database Models**: All SQLAlchemy 2.0 async models with relationships and indexes
2. **Pydantic Schemas**: Request/response DTOs for all API endpoints with validation
3. **REST API Structure**: Complete endpoint specifications with methods and parameters
4. **Service Layer**: Business logic interfaces for discussion engine, authentication, reports
5. **Security Implementation**: JWT auth, AES-256-GCM encryption, rate limiting
6. **WebSocket Protocol**: Real-time communication protocol for discussion updates
7. **Caching Strategy**: Redis-based caching with decorators

### Next Steps for Implementation

1. Set up project structure and dependencies
2. Create database migrations with Alembic
3. Implement authentication and user management
4. Build discussion engine with LLM integration
5. Add WebSocket real-time updates
6. Implement report generation
7. Add comprehensive testing
8. Deploy with Docker Compose

### Performance Considerations

- Target: < 2s response time (excluding LLM calls)
- Target: < 10s first message latency
- Target: 5-10s per character message generation
- Use connection pooling for database and Redis
- Implement exponential backoff for LLM API retries
- Cache active discussion state in Redis

### Security Checklist

- [x] JWT authentication with refresh tokens
- [x] AES-256-GCM API key encryption
- [x] Rate limiting per endpoint
- [x] CORS configuration
- [x] Input validation with Pydantic
- [x] SQL injection prevention (ORM)
- [x] HTTPS/WSS enforcement
- [ ] Audit logging for sensitive operations

---

**Document Status**: Ready for Implementation
**Maintainer**: Backend Architect
**Last Updated**: 2026-01-12
