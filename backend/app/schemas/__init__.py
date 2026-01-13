"""
Pydantic schemas package

This package contains all Pydantic schemas for request/response validation.
"""
# Common schemas
from app.schemas.common import (
    ErrorResponse,
    IdResponse,
    MessageResponse,
    PaginatedResponse,
    PaginationParams,
)

# Auth schemas
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)

# User schemas
from app.schemas.user import (
    APIKeyCreateRequest,
    APIKeyResponse,
    APIKeyUpdateRequest,
    UserStatsResponse,
    UserUpdateRequest,
    UserResponse,
)

# Topic schemas
from app.schemas.topic import (
    TopicCreateRequest,
    TopicListResponse,
    TopicResponse,
    TopicUpdateRequest,
)

# Character schemas
from app.schemas.character import (
    CharacterConfig,
    CharacterCreateRequest,
    CharacterResponse,
    CharacterTemplateResponse,
    CharacterUpdateRequest,
    KnowledgeBackground,
    PersonalityTraits,
)

# Discussion schemas
from app.schemas.discussion import (
    DiscussionControlRequest,
    DiscussionCreateRequest,
    DiscussionDetailResponse,
    DiscussionListResponse,
    DiscussionResponse,
    InjectQuestionRequest,
    MessageResponse,
    ParticipantResponse,
)

# Report schemas
from app.schemas.report import (
    ReportResponse,
    ReportSummaryResponse,
    ShareLinkCreateRequest,
    ShareLinkResponse,
)

__all__ = [
    # Common
    "ErrorResponse",
    "IdResponse",
    "MessageResponse",
    "PaginatedResponse",
    "PaginationParams",
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "VerifyEmailRequest",
    "ChangePasswordRequest",
    # User
    "UserResponse",
    "UserUpdateRequest",
    "UserStatsResponse",
    "APIKeyCreateRequest",
    "APIKeyResponse",
    "APIKeyUpdateRequest",
    # Topic
    "TopicCreateRequest",
    "TopicUpdateRequest",
    "TopicResponse",
    "TopicListResponse",
    # Character
    "PersonalityTraits",
    "KnowledgeBackground",
    "CharacterConfig",
    "CharacterCreateRequest",
    "CharacterUpdateRequest",
    "CharacterResponse",
    "CharacterTemplateResponse",
    # Discussion
    "DiscussionCreateRequest",
    "DiscussionResponse",
    "DiscussionListResponse",
    "DiscussionDetailResponse",
    "ParticipantResponse",
    "MessageResponse",
    "InjectQuestionRequest",
    "DiscussionControlRequest",
    # Report
    "ReportResponse",
    "ReportSummaryResponse",
    "ShareLinkCreateRequest",
    "ShareLinkResponse",
]
