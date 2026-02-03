# Models module
# Import all models to ensure SQLAlchemy relationships are properly initialized

from app.models.user import User
from app.models.api_key import UserAPIKey
from app.models.topic import Topic
from app.models.character import Character
from app.models.discussion import Discussion
from app.models.participant import DiscussionParticipant
from app.models.message import DiscussionMessage
from app.models.report import Report
from app.models.share_link import ShareLink
from app.models.audit_log import AuditLog

__all__ = [
    'User',
    'UserAPIKey',
    'Topic',
    'Character',
    'Discussion',
    'DiscussionParticipant',
    'DiscussionMessage',
    'Report',
    'ShareLink',
    'AuditLog',
]
