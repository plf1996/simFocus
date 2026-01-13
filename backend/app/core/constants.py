"""
Application constants

Defines constant values used throughout the application.
"""
from enum import Enum


class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class UserRole(str, Enum):
    """User role."""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class OAuthProvider(str, Enum):
    """OAuth provider names."""
    GOOGLE = "google"
    GITHUB = "github"


class DiscussionStatus(str, Enum):
    """Discussion status states."""
    PENDING = "pending"        # Waiting to start
    IN_PROGRESS = "in_progress" # Currently running
    PAUSED = "paused"          # Paused by user
    COMPLETED = "completed"    # Finished all rounds
    FAILED = "failed"          # Error occurred
    CANCELLED = "cancelled"    # Cancelled by user


class DiscussionMode(str, Enum):
    """Discussion modes."""
    FREE = "free"                    # Free discussion
    STRUCTURED_DEBATE = "structured_debate"  # Pro/con/neutral
    CREATIVE_BRAINSTORM = "creative_brainstorm"  # "Yes, and" style
    CONSENSUS = "consensus"          # Seeking agreement


class DiscussionStage(str, Enum):
    """Discussion stages."""
    OPENING = "opening"          # 1-2 rounds: Introductions
    DEVELOPMENT = "development"  # 3-8 rounds: Deep dive
    DEBATE = "debate"            # 2-5 rounds: Direct confrontation
    CONCLUSION = "conclusion"    # 1-2 rounds: Summary


class CharacterType(str, Enum):
    """Character types."""
    CUSTOM = "custom"            # User-created
    PRESET = "preset"            # Built-in template
    AI_GENERATED = "ai_generated" # AI-generated for topic


class MessageRole(str, Enum):
    """Message roles in discussion."""
    SYSTEM = "system"
    CHARACTER = "character"
    MODERATOR = "moderator"
    USER = "user"


class APIProvider(str, Enum):
    """Supported API providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"  # OpenAI-compatible


class ReportFormat(str, Enum):
    """Report export formats."""
    PDF = "pdf"
    MARKDOWN = "markdown"
    JSON = "json"


class CharacterPersonalityTrait(str, Enum):
    """Character personality traits."""
    OPENNESS = "openness"          # 1-10
    CONSCIENTIOUSNESS = "conscientiousness"  # 1-10
    EXTRAVERSION = "extraversion"  # 1-10
    AGREEABLENESS = "agreeableness" # 1-10
    NEUROTICISM = "neuroticism"    # 1-10


class CharacterStance(str, Enum):
    """Character's discussion stance."""
    SUPPORT = "support"
    OPPOSE = "oppose"
    NEUTRAL = "neutral"
    CRITICAL = "critical"


class CharacterExpressiveStyle(str, Enum):
    """Character's expression style."""
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    STORYTELLING = "storytelling"


class CharacterBehaviorPattern(str, Enum):
    """Character's behavior pattern."""
    ACTIVE = "active"              # Proactive speaker
    RESPONSIVE = "responsive"      # Reactive speaker
    BALANCED = "balanced"          # Mixed behavior


# Pagination constants
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Discussion configuration
MIN_DISCUSSION_ROUNDS = 3
DEFAULT_DISCUSSION_ROUNDS = 10
MAX_DISCUSSION_ROUNDS = 20

MIN_CHARACTERS = 2
MAX_CHARACTERS = 10

# Rate limiting
RATE_LIMIT_PER_MINUTE = 60
RATE_LIMIT_BURST = 100

# Token lengths
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# File upload
MAX_UPLOAD_SIZE_MB = 10
ALLOWED_UPLOAD_EXTENSIONS = ["pdf", "txt", "md", "json"]

# API timeout
API_TIMEOUT_SECONDS = 120
API_MAX_RETRIES = 3

# Message content limits
MAX_MESSAGE_LENGTH = 5000
MAX_TOPIC_DESCRIPTION = 2000
MAX_CHARACTER_BIO = 1000
MAX_TOPIC_TITLE = 200

# Report settings
REPORT_SUMMARY_MAX_LENGTH = 1000
REPORT_INSIGHTS_COUNT = 5
