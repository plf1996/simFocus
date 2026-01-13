"""
Database models package

Exports all SQLAlchemy ORM models for the simFocus application.
All models inherit from BaseModel which provides UUID primary key
and timestamp fields (created_at, updated_at).

Available Models:
    User: User accounts with authentication
    UserApiKey: Encrypted API keys for LLM providers
    Topic: Discussion topics
    Character: AI character configurations
    Discussion: Discussion sessions
    DiscussionParticipant: Character participation in discussions
    DiscussionMessage: Individual messages in discussions
    Report: Generated discussion reports
    ShareLink: Shareable discussion links

Usage:
    from app.models import User, Topic, Discussion

    # Create a new user
    user = User(email="user@example.com", name="John Doe")

    # Query discussions
    async for session in get_db():
        result = await session.execute(
            select(Discussion).where(Discussion.status == 'running')
        )
        discussions = result.scalars().all()
"""

# Import all models
from app.models.api_key import UserApiKey
from app.models.character import Character
from app.models.discussion import Discussion, DiscussionMessage, DiscussionParticipant
from app.models.report import Report, ShareLink
from app.models.topic import Topic
from app.models.user import User

# Convenience exports for common use cases
__all__ = [
    # User models
    "User",
    "UserApiKey",
    # Content models
    "Topic",
    "Character",
    # Discussion models
    "Discussion",
    "DiscussionParticipant",
    "DiscussionMessage",
    # Report models
    "Report",
    "ShareLink",
]

# Model lists for introspection
ALL_MODELS = [
    User,
    UserApiKey,
    Topic,
    Character,
    Discussion,
    DiscussionParticipant,
    DiscussionMessage,
    Report,
    ShareLink]

# Grouped by functionality
USER_MODELS = [User, UserApiKey]
CONTENT_MODELS = [Topic, Character]
DISCUSSION_MODELS = [Discussion, DiscussionParticipant, DiscussionMessage]
REPORT_MODELS = [Report, ShareLink]
